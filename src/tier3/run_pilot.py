"""Tier-3 PILOT: the decisive cross-architecture test, CPU-scale (audit P4).

THE DESIGN
  * Models: EleutherAI/pythia-160m (softmax attention) vs
    state-spaces/mamba-130m-hf (selective SSM, fixed recurrent state), with
    RWKV rwkv-4-169m-pile optional. All are BASE models trained on the SAME
    corpus (The Pile) at matched scale, so architecture is the only variable
    that differs — the cleanest attribution available at this size.
  * Task: associative recall in completion form (the recall-robust regime our
    sweep showed softmax handles at ceiling, and where Theorem II / Zoology /
    Jelassi et al. predict fixed-state failure). The prompt lists k facts
        "The access code for {city} is {code}."
    in random order, then ends with the verbatim query prefix
        "The access code for {city} is"
    and the model must greedily complete the code. This is deliberately an
    INDUCTION-HEAD-shaped probe: the query is an exact prefix repetition, so a
    softmax model needs only attend back to the match; a fixed-state model must
    have kept the pair in its recurrent state.
  * Metric: exact-match of the greedy continuation against the code, over
    q sampled queries per instance, s seeds per k, k in {4,8,16,32,64}.
  * Prediction (P4, recall axis): pythia roughly flat in k; mamba/rwkv decay as
    k outgrows the state.

Base models are not instruction-tuned, so no instructions are given — the
format IS the task. Codes are 3 chars from [0-9A-Z] (multi-token; we string-
match the decoded continuation).
"""
from __future__ import annotations
import argparse, gc, json, os, random, time

CITIES = ("Lisbon Cairo Oslo Tokyo Lima Accra Hanoi Quito Riga Doha Sofia "
          "Tunis Minsk Dakar Amman Bogota Manila Vienna Nassau Maputo Zagreb "
          "Tirana Bamako Harare Havana Muscat Osaka Perth Quebec Rabat Seoul "
          "Tunja Umea Vaduz Warsaw Xalapa Yamba Zunyi Arica Bern Cusco Delhi "
          "Erbil Fez Gdansk Hue Izmir Jaipur Kyoto Leon Medan Nara Oran Pune "
          "Quimper Rennes Split Turin Ulsan Vigo Wuhan Xian Yazd Zaria").split()

# Common words verified single-token (with leading space) in the NeoX BPE used
# by both Pythia and mamba-hf — so with --value-style words, COPYING is a
# 1-token operation and RECALL is the only bottleneck (removes the floor
# effect the 3-char code format produced at 130-160M zero-shot).
WORD_VALUES = sorted(set(
    ("apple river stone music green house table light paper cloud "
     "dream glass horse metal night ocean piano queen radio sugar "
     "tiger urban voice water youth zebra bread chair dance eagle "
     "flame grape heart index juice knife lemon mouse north olive "
     "quiet round snake tower under vapor wheat yacht globe smoke "
     "honey lunar maple noble opera quartz solar ultra vivid whale "
     "yield frost coral brick candy fence magic shade shine trunk").split()))


def make_instance(k, seed, value_style="codes"):
    rng = random.Random(seed)
    cities = rng.sample(CITIES, k)
    if value_style == "words":
        vals = rng.sample(WORD_VALUES, k)
        codes = {c: v for c, v in zip(cities, vals)}
        facts = [f"The password for {c} is {codes[c]}." for c in cities]
    else:
        C = "0123456789ABCDEFGHJKLMNPQRSTUVWXYZ"
        codes = {c: "".join(rng.choice(C) for _ in range(3)) for c in cities}
        facts = [f"The access code for {c} is {codes[c]}." for c in cities]
    rng.shuffle(facts)
    return "\n".join(facts), cities, codes, rng


def eval_model(model_id, ks, seeds_per_k, queries_per_inst, out_rows,
               value_style="codes", dtype="float32"):
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    print(f"\n=== {model_id} [{value_style}] ===", flush=True)
    tok = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(model_id, dtype=getattr(torch, dtype))
    model.eval()
    q_tpl = ("The password for {} is" if value_style == "words"
             else "The access code for {} is")
    for k in ks:
        hits = tot = 0
        t0 = time.time()
        for s in range(seeds_per_k):
            facts, cities, codes, rng = make_instance(k, seed=1000 * k + s,
                                                      value_style=value_style)
            qs = rng.sample(cities, min(queries_per_inst, k))
            for city in qs:
                prompt = f"{facts}\n{q_tpl.format(city)}"
                ids = tok(prompt, return_tensors="pt").input_ids
                with torch.no_grad():
                    out = model.generate(ids, max_new_tokens=6, do_sample=False,
                                         pad_token_id=tok.eos_token_id)
                cont = tok.decode(out[0, ids.shape[1]:], skip_special_tokens=True)
                ok = cont.strip().startswith(codes[city])
                hits += ok; tot += 1
        acc = hits / tot
        dt = time.time() - t0
        print(f"  k={k:>3}: acc={acc:.3f}  ({hits}/{tot}, {dt:.0f}s)", flush=True)
        out_rows.append(dict(model=model_id, value_style=value_style, k=k,
                             acc=acc, n=tot))
    del model
    gc.collect()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", nargs="+", default=[
        "EleutherAI/pythia-160m", "state-spaces/mamba-130m-hf"])
    ap.add_argument("--ks", nargs="+", type=int, default=[4, 8, 16, 32, 64])
    ap.add_argument("--seeds", type=int, default=2)
    ap.add_argument("--queries", type=int, default=8)
    ap.add_argument("--value-style", default="codes", choices=["codes", "words"])
    ap.add_argument("--out", default="pilot_recall.json")
    a = ap.parse_args()
    rows = []
    for mid in a.models:
        try:
            eval_model(mid, a.ks, a.seeds, a.queries, rows,
                       value_style=a.value_style)
        except Exception as e:
            print(f"  !! {mid} failed: {type(e).__name__}: {e}", flush=True)
            rows.append(dict(model=mid, error=str(e)))
    here = os.path.dirname(os.path.abspath(__file__))
    res = os.path.join(here, "..", "..", "results", "tier3")
    os.makedirs(res, exist_ok=True)
    with open(os.path.join(res, a.out), "w", encoding="utf-8") as f:
        json.dump({"task": "associative recall, completion form",
                   "value_style": a.value_style,
                   "protocol": f"{a.seeds} seeds x {a.queries} queries per k; "
                               "greedy 6 tokens; exact prefix match",
                   "rows": rows}, f, indent=2)
    print(f"\nwrote results/tier3/{a.out}")


if __name__ == "__main__":
    main()
