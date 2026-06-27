"""Deterministic graders for the NL lifts. Each returns a score in [0, 1].

Graders are lenient about surrounding prose / formatting but strict about the
content, so they fairly score a chat model's answer against the hidden key.
"""
from __future__ import annotations
import re


def _extract_answer_block(text: str) -> str:
    m = re.search(r"<answer>(.*?)</answer>", text, re.DOTALL | re.IGNORECASE)
    return m.group(1).strip() if m else text.strip()


def grade_gather(model_out: str, inst: dict) -> float:
    out = _extract_answer_block(model_out)
    words = [w.strip().lower() for w in re.findall(r"[A-Za-z]+", out)]
    gold = [w.lower() for w in inst["answer_list"]]
    # sequence match on the first len(gold) words
    n = len(gold)
    hits = sum(1 for i in range(min(n, len(words))) if words[i] == gold[i])
    return hits / n if n else 0.0


def grade_mqar(model_out: str, inst: dict) -> float:
    out = _extract_answer_block(model_out)
    found = dict(re.findall(r"(\d+)\s*[.):]\s*([0-9A-Za-z]{2,4})", out))
    # map question index -> expected code
    keys = list(inst["answer_map"].values())
    n = len(keys)
    hits = 0
    for i, code in enumerate(keys, start=1):
        if found.get(str(i), "").upper() == code.upper():
            hits += 1
    return hits / n if n else 0.0


def grade_chain(model_out: str, inst: dict) -> float:
    out = _extract_answer_block(model_out)
    nums = re.findall(r"-?\d+", out)
    return 1.0 if nums and nums[-1] == inst["answer"] else 0.0


def grade_seq_words(model_out: str, inst: dict) -> float:
    """Ordered word-sequence match (shared by selective_copy and sort_by_key)."""
    return grade_gather(model_out, inst)


def grade_kv_lastwrite(model_out: str, inst: dict) -> float:
    out = _extract_answer_block(model_out)
    found = dict(re.findall(r"(\d+)\s*[.):]\s*([0-9A-Za-z]{2,4})", out))
    keys = list(inst["answer_map"].values())
    n = len(keys)
    hits = sum(1 for i, code in enumerate(keys, start=1)
               if found.get(str(i), "").upper() == code.upper())
    return hits / n if n else 0.0


def grade_multihop(model_out: str, inst: dict) -> float:
    out = _extract_answer_block(model_out)
    toks = re.findall(r"[A-Za-z]\w*", out)
    return 1.0 if toks and toks[-1] == inst["answer"] else 0.0


GRADERS = {"gather": grade_gather, "mqar": grade_mqar, "chain": grade_chain,
           "selective_copy": grade_seq_words, "sort_by_key": grade_seq_words,
           "kv_lastwrite": grade_kv_lastwrite, "multihop_map": grade_multihop}


def grade(model_out: str, inst: dict) -> float:
    return GRADERS[inst["task"]](model_out, inst)
