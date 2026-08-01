"""Tier-3, task-trained tier (the Zoology protocol, CPU-scale).

Zero-shot prompting cannot elicit in-context recall from 100-400M pretrained
models (see pilot_recall*.json + the error-mode diagnostic: they emit
prior-shaped values, not retrieved ones). The literature's clean separations at
small scale come from TASK-TRAINED tiny models (Zoology; Jelassi et al.'s
synthetic section). This module reproduces that protocol in-repo:

  * Task: synthetic MQAR. Sequence = k1 v1 k2 v2 ... kK vK q, target = the
    value paired with query key q. Fresh random key->value maps every batch,
    so nothing can be memorized — the model must implement retrieval.
  * Models: identical 2-layer stacks (embeddings, residual stream, LayerNorm,
    MLP) differing ONLY in the sequence mixer:
      - softmax attention (2 heads)
      - linear attention, elu(x)+1 features (2 heads)  [Katharopoulos form]
    Same d_model, same training steps/optimizer/batches/seeds.
  * Sweep K at fixed d_model: prediction (P4, task-trained form): softmax
    solves all K; linear caps when the needed state outgrows d_model.

Because these stacks have residual connections and MLPs, this also empirically
tests the audit A2 gap: the frozen rank-product argument does not cover
residual stacks, but Theorem II (fixed state) still should — if trained
linear-with-residuals caps at state capacity, the loophole does not save it.
"""
from __future__ import annotations
import argparse, json, math, os, time
import torch
import torch.nn as nn
import torch.nn.functional as F

torch.manual_seed(0)


def make_batch(B, K, n_keys, n_vals, device, m=None):
    """MQAR with MULTI-QUERY supervision (the Zoology shape): sequence =
    [k1 v1 ... kK vK  q1 a1 q2 a2 ... qm am]; loss at every answer position
    (m supervised tokens per sequence, not 1 — the dense signal induction
    circuits need to form). Keys distinct per sequence; fresh map each batch."""
    m = m or min(K, 8)
    keys = torch.stack([torch.randperm(n_keys)[:K] for _ in range(B)])  # (B,K)
    vals = torch.randint(0, n_vals, (B, K))
    qi = torch.stack([torch.randperm(K)[:m] for _ in range(B)])          # (B,m)
    bidx = torch.arange(B).unsqueeze(1)
    qk = keys[bidx, qi]                    # (B,m) query key tokens
    qa = vals[bidx, qi] + n_keys           # (B,m) answer value tokens
    T = 2 * K + 2 * m
    seq = torch.empty(B, T, dtype=torch.long)
    seq[:, 0:2 * K:2] = keys
    seq[:, 1:2 * K:2] = vals + n_keys
    seq[:, 2 * K::2] = qk
    seq[:, 2 * K + 1::2] = qa
    # labels: -100 everywhere except query positions, which predict the answer
    lab = torch.full((B, T), -100, dtype=torch.long)
    lab[:, 2 * K::2] = qa
    return seq.to(device), lab.to(device)


class Mixer(nn.Module):
    def __init__(self, d, heads, kind):
        super().__init__()
        self.h, self.dk, self.kind = heads, d // heads, kind
        # Short causal depthwise conv (kernel 2), as in Zoology/Based — given to
        # EVERY mixer incl. the softmax baseline. It supplies the previous-token
        # composition that induction circuits otherwise must learn position-by-
        # position under learned APE (the K=8->16 trainability cliff).
        self.conv = nn.Conv1d(d, d, 2, padding=1, groups=d, bias=False)
        self.qkv = nn.Linear(d, 3 * d, bias=False)
        self.out = nn.Linear(d, d, bias=False)

    def forward(self, x):
        B, T, D = x.shape
        x = x + self.conv(x.transpose(1, 2))[:, :, :T].transpose(1, 2)
        q, k, v = self.qkv(x).chunk(3, -1)
        q, k, v = (t.view(B, T, self.h, self.dk).transpose(1, 2) for t in (q, k, v))
        if self.kind == "softmax":
            mask = torch.triu(torch.full((T, T), float("-inf"), device=x.device), 1)
            att = torch.softmax(q @ k.transpose(-1, -2) / math.sqrt(self.dk) + mask, -1)
            y = att @ v
        else:  # linear attention, causal, elu+1 features
            q, k = F.elu(q) + 1, F.elu(k) + 1
            kv = torch.einsum("bhtd,bhte->bhtde", k, v).cumsum(2)   # running sum
            ks = k.cumsum(2)
            y = torch.einsum("bhtd,bhtde->bhte", q, kv) / \
                (torch.einsum("bhtd,bhtd->bht", q, ks).unsqueeze(-1) + 1e-6)
        return self.out(y.transpose(1, 2).reshape(B, T, D))


class Block(nn.Module):
    def __init__(self, d, heads, kind):
        super().__init__()
        self.n1, self.n2 = nn.LayerNorm(d), nn.LayerNorm(d)
        self.mix = Mixer(d, heads, kind)
        self.mlp = nn.Sequential(nn.Linear(d, 4 * d), nn.GELU(), nn.Linear(4 * d, d))

    def forward(self, x):
        x = x + self.mix(self.n1(x))
        return x + self.mlp(self.n2(x))


class TinyLM(nn.Module):
    def __init__(self, vocab, d=64, heads=2, layers=2, kind="softmax", T=200):
        super().__init__()
        self.emb = nn.Embedding(vocab, d)
        self.pos = nn.Embedding(T, d)
        self.blocks = nn.ModuleList(Block(d, heads, kind) for _ in range(layers))
        self.nf = nn.LayerNorm(d)
        self.head = nn.Linear(d, vocab, bias=False)

    def forward(self, seq):
        x = self.emb(seq) + self.pos(torch.arange(seq.shape[1], device=seq.device))
        for b in self.blocks:
            x = b(x)
        return self.head(self.nf(x))               # logits at every position


def run(kind, K, d=64, steps=1500, B=64, n_keys=96, n_vals=96, lr=2e-3, seed=0):
    torch.manual_seed(seed)
    dev = "cpu"
    m = min(K, 8)
    model = TinyLM(n_keys + n_vals, d=d, kind=kind, T=2 * K + 2 * m).to(dev)
    opt = torch.optim.AdamW(model.parameters(), lr=lr)
    warm = max(50, steps // 20)
    for step in range(steps):
        # warmup + cosine decay (the regime where tiny models learn MQAR)
        s = (step + 1) / warm if step < warm else \
            0.02 + 0.98 * 0.5 * (1 + math.cos(math.pi * (step - warm) / max(1, steps - warm)))
        for g in opt.param_groups:
            g["lr"] = lr * s
        seq, lab = make_batch(B, K, n_keys, n_vals, dev, m=m)
        logits = model(seq)
        loss = F.cross_entropy(logits.reshape(-1, logits.shape[-1]),
                               lab.reshape(-1), ignore_index=-100)
        opt.zero_grad(); loss.backward(); opt.step()
        if (step + 1) % 500 == 0:
            print(f"    [{kind} K={K}] step {step+1} loss={loss.item():.3f}", flush=True)
    # eval on fresh maps: accuracy over supervised (answer) positions
    model.eval(); hits = tot = 0
    with torch.no_grad():
        for _ in range(20):
            seq, lab = make_batch(128, K, n_keys, n_vals, dev, m=m)
            pred = model(seq).argmax(-1)
            sel = lab != -100
            hits += (pred[sel] == lab[sel]).sum().item(); tot += sel.sum().item()
    return hits / tot, sum(p.numel() for p in model.parameters())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ks", nargs="+", type=int, default=[8, 16, 32, 64])
    ap.add_argument("--d", type=int, default=64)
    ap.add_argument("--steps", type=int, default=1500)
    a = ap.parse_args()
    rows = []
    for K in a.ks:
        for kind in ("softmax", "linear"):
            t0 = time.time()
            acc, nparams = run(kind, K, d=a.d, steps=a.steps)
            print(f"K={K:>3} {kind:>8}: acc={acc:.3f}  "
                  f"({nparams/1e3:.0f}k params, {time.time()-t0:.0f}s)", flush=True)
            rows.append(dict(K=K, kind=kind, acc=acc, d=a.d, params=nparams))
    here = os.path.dirname(os.path.abspath(__file__))
    res = os.path.join(here, "..", "..", "results", "tier3")
    os.makedirs(res, exist_ok=True)
    with open(os.path.join(res, "trained_tiny_mqar.json"), "w", encoding="utf-8") as f:
        json.dump({"protocol": f"2-layer residual stacks, identical except the "
                               f"mixer; d={a.d}, {a.steps} steps, fresh maps "
                               "every batch; eval on 2560 fresh sequences",
                   "rows": rows}, f, indent=2)
    print("wrote results/tier3/trained_tiny_mqar.json")


if __name__ == "__main__":
    main()
