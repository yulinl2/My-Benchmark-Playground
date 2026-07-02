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


def make_instance(k, seed):
    rng = random.Random(seed)
    cities = rng.sample(CITIES, k)
    C = "0123456789ABCDEFGHJKLMNPQRSTUVWXYZ"
    codes = {c: "".join(rng.choice(C) for _ in range(3)) for c in cities}
    facts = [f"The access code for {c} is {codes[c]}." for c in cities]
    rng.shuffle(facts)
    return "\n".join(facts), cities, codes, rng


def eval_model(model_id, ks, seeds_per_k, queries_per_inst, out_rows, dtype="float32"):
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    print(f"\n=== {model_id} ===", flush=True)
    tok = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(model_id, torch_dtype=getattr(torch, dtype))
    model.eval()
    for k in ks:
        hits = tot = 0
        t0 = time.time()
        for s in range(seeds_per_k):
            facts, cities, codes, rng = make_instance(k, seed=1000 * k + s)
            qs = rng.sample(cities, min(queries_per_inst, k))
            for city in qs:
                prompt = f"{facts}\nThe access code for {city} is"
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
        out_rows.append(dict(model=model_id, k=k, acc=acc, n=tot))
    del model
    gc.collect()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", nargs="+", default=[
        "EleutherAI/pythia-160m", "state-spaces/mamba-130m-hf"])
    ap.add_argument("--ks", nargs="+", type=int, default=[4, 8, 16, 32, 64])
    ap.add_argument("--seeds", type=int, default=2)
    ap.add_argument("--queries", type=int, default=8)
    a = ap.parse_args()
    rows = []
    for mid in a.models:
        try:
            eval_model(mid, a.ks, a.seeds, a.queries, rows)
        except Exception as e:
            print(f"  !! {mid} failed: {type(e).__name__}: {e}", flush=True)
            rows.append(dict(model=mid, error=str(e)))
    here = os.path.dirname(os.path.abspath(__file__))
    res = os.path.join(here, "..", "..", "results", "tier3")
    os.makedirs(res, exist_ok=True)
    with open(os.path.join(res, "pilot_recall.json"), "w", encoding="utf-8") as f:
        json.dump({"task": "associative recall, completion form",
                   "protocol": f"{a.seeds} seeds x {a.queries} queries per k; "
                               "greedy 6 tokens; exact prefix match",
                   "rows": rows}, f, indent=2)
    print("\nwrote results/tier3/pilot_recall.json")


if __name__ == "__main__":
    main()
