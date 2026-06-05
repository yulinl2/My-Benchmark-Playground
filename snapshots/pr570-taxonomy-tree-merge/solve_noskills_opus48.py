#!/usr/bin/env python3
"""
PR #570 taxonomy-tree-merge — WITHOUT-SKILLS condition.

Opus 4.8 Max solving purely from instruction.md (no import / use of the bundled
`hierarchical-taxonomy-clustering` skill). This is my own independent
implementation of the unification methodology the instruction describes.
"""
import os
import re
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import linkage, fcluster
import nltk
from nltk.stem import WordNetLemmatizer

for pkg in ("wordnet", "omw-1.4"):
    try:
        nltk.data.find(f"corpora/{pkg}")
    except LookupError:
        nltk.download(pkg, quiet=True)

np.random.seed(0)

HERE = Path(__file__).resolve().parent
DATA = HERE / "task" / "environment" / "data"
OUT = Path(os.environ.get("OUTPUT_DIR", HERE / "output_without_skills"))
OUT.mkdir(parents=True, exist_ok=True)

MAX_DEPTH = 5
LEVEL_WEIGHTS = {i: 0.6 ** (i - 1) for i in range(1, MAX_DEPTH + 1)}
L1_MIN, L1_MAX = 12, 18
SUB_MIN, SUB_MAX = 3, 20
COVERAGE = 0.70
MAX_WORDS = 5
LEAF_LIMIT = 3

_lem = WordNetLemmatizer()
_cache: dict[str, str] = {}


def lemma(tok: str) -> str:
    out = _cache.get(tok)
    if out is None:
        out = _lem.lemmatize(tok, pos="n")
        _cache[tok] = out
    return out


def clean_level(part: str) -> str:
    part = part.replace("&", " and ").replace("/", " ").replace("-", " ")
    part = part.replace(",", " ").replace("'s", "").replace("'", "").replace('"', "")
    part = re.sub(r"[^a-z0-9 ]", " ", part.lower())
    return " ".join(lemma(t) for t in part.split() if t and t != "and")


def clean_path(path: str) -> str:
    p = str(path).strip().replace("->", ">").replace("|", ">").replace(" > ", ">")
    parts = [clean_level(s) for s in p.split(">")]
    return " > ".join(s for s in parts if s)


def load_source(fname: str, source: str) -> pd.DataFrame:
    df = pd.read_csv(DATA / fname)
    col = "category_path" if "category_path" in df.columns else next(
        c for c in df.columns if c.lower().strip() == "category_path")
    s = df[col].dropna().astype(str).map(clean_path)
    s = s[s.str.len() > 0]
    return pd.DataFrame({"category_path": s, "source": source}).drop_duplicates("category_path")


def build_frame() -> pd.DataFrame:
    df = pd.concat([
        load_source("amazon_product_categories.csv", "amazon"),
        load_source("fb_product_categories.csv", "facebook"),
        load_source("google_shopping_product_categories.csv", "google"),
    ], ignore_index=True)
    df["depth"] = df["category_path"].str.count(" > ") + 1
    df = df[df["depth"] <= MAX_DEPTH].copy()

    paths = set(df["category_path"])
    drop = set()
    for p in paths:
        parts = p.split(" > ")
        for i in range(1, len(parts)):
            pre = " > ".join(parts[:i])
            if pre in paths:
                drop.add(pre)
    df = df[~df["category_path"].isin(drop)].reset_index(drop=True)
    for i in range(1, MAX_DEPTH + 1):
        df[f"level_{i}"] = df["category_path"].map(
            lambda p, i=i: (p.split(" > ")[i - 1] if len(p.split(" > ")) >= i else None))
    return df


def embed(df: pd.DataFrame) -> np.ndarray:
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer("all-MiniLM-L6-v2")
    vocab = sorted({v for i in range(1, MAX_DEPTH + 1) for v in df[f"level_{i}"].dropna().unique()})
    vec = model.encode(vocab, batch_size=256, show_progress_bar=False)
    lut = {w: vec[i] for i, w in enumerate(vocab)}
    dim = vec.shape[1]
    out = np.zeros((len(df), dim), dtype=np.float32)
    for r, row in enumerate(df.itertuples(index=False)):
        acc = np.zeros(dim, dtype=np.float32); wsum = 0.0
        for i in range(1, MAX_DEPTH + 1):
            val = getattr(row, f"level_{i}")
            if isinstance(val, str) and val in lut:
                w = LEVEL_WEIGHTS[i]; acc += lut[val] * w; wsum += w
        if wsum > 0:
            acc /= wsum
        out[r] = acc
    return out


def name_cluster(df, idx, start, exclude, used):
    w = {i: 0.6 ** (i - 1) for i in range(1, MAX_DEPTH + 1)}
    freq = Counter()
    for j in idx:
        row = df.iloc[j]
        for lv in range(start, MAX_DEPTH + 1):
            val = row[f"level_{lv}"]
            if isinstance(val, str):
                for tok in val.split():
                    if len(tok) > 2 and tok not in exclude:
                        freq[tok] += w[lv]
    if not freq:
        return None
    target = len(idx) * COVERAGE
    covered, chosen = set(), []
    for word, _ in sorted(freq.items(), key=lambda x: -x[1]):
        hit = set()
        for j in idx:
            if j in covered:
                continue
            row = df.iloc[j]
            for lv in range(start, MAX_DEPTH + 1):
                val = row[f"level_{lv}"]
                if isinstance(val, str) and word in val.split():
                    hit.add(j); break
        if hit:
            chosen.append(word); before = len(covered); covered |= hit
            if len(chosen) >= MAX_WORDS or len(covered) >= target:
                if len(covered) > before:
                    break
        if len(chosen) >= MAX_WORDS:
            break
    name = " | ".join(chosen)
    return name if name and name not in used else None


def cut(lk, lo, hi):
    heights = lk[:, 2]; best, bn = None, 0
    for t in sorted(heights, reverse=True):
        n = len(np.unique(fcluster(lk, t, criterion="distance")))
        if lo <= n <= hi and n > bn:
            best, bn = t, n
    if best is not None:
        return best
    for t in sorted(heights, reverse=True):
        if len(np.unique(fcluster(lk, t, criterion="distance"))) <= hi:
            return t
    return heights.max()


def recurse(df, emb, idx, level, parent_words, used, assign):
    if level > MAX_DEPTH or len(idx) <= LEAF_LIMIT:
        name = name_cluster(df, idx, level, parent_words, used)
        for j in idx:
            assign[j] = {level: name}
        if name:
            used.add(name)
        return
    lk = linkage(emb[idx], method="average", metric="cosine")
    lo, hi = (L1_MIN, L1_MAX) if level == 1 else (SUB_MIN, SUB_MAX)
    labels = fcluster(lk, cut(lk, lo, hi), criterion="distance")
    for cid in np.unique(labels):
        members = [idx[k] for k in np.where(labels == cid)[0]]
        name = name_cluster(df, members, level, parent_words, used)
        if name:
            used.add(name)
            child_excl = parent_words | set(name.replace(" | ", " ").split())
        else:
            child_excl = parent_words
        if len(members) <= LEAF_LIMIT or level >= MAX_DEPTH:
            for j in members:
                assign[j] = {level: name}
        else:
            recurse(df, emb, members, level + 1, child_excl, used, assign)
            for j in members:
                assign[j][level] = name


def main():
    print("[1/4] load+standardize"); df = build_frame()
    print(f"      {len(df)} paths {df.source.value_counts().to_dict()}")
    print("[2/4] embed"); emb = embed(df)
    print("[3/4] cluster"); assign = {}
    recurse(df, emb, list(range(len(df))), 1, set(), set(), assign)
    for lvl in range(1, MAX_DEPTH + 1):
        df[f"unified_level_{lvl}"] = [assign[j].get(lvl) for j in range(len(df))]
    print("[4/4] export")
    cols = ["source", "category_path", "depth"] + [f"unified_level_{i}" for i in range(1, 6)]
    df[cols].to_csv(OUT / "unified_taxonomy_full.csv", index=False)
    h = [f"unified_level_{i}" for i in range(1, 6)]
    hier = (df[h].dropna(subset=["unified_level_1"]).drop_duplicates()
            .sort_values(h, na_position="last").reset_index(drop=True))
    hier.to_csv(OUT / "unified_taxonomy_hierarchy.csv", index=False)
    print(f"   full={len(df)} hierarchy={len(hier)}")
    for i in range(1, 6):
        print(f"   L{i}: {df[f'unified_level_{i}'].nunique()}")


if __name__ == "__main__":
    main()
