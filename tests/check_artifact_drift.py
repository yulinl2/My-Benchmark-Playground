"""Artifact drift check with float tolerance.

Byte-identical JSON comparison is too strict across machines: libm/BLAS differ
in the last ULP (observed: 0.7622298663093533 vs ...34 between CI and the dev
container). This compares committed result JSONs against freshly regenerated
ones structurally, with relative tolerance 1e-6 on numbers; text (suite.json
prompts/answers) must still match exactly.

Usage: python3 tests/check_artifact_drift.py <committed.json> <fresh.json> ...
       (pairs; exits 1 on structural or out-of-tolerance mismatch)
"""
from __future__ import annotations
import json, math, sys

RTOL, ATOL = 1e-6, 1e-9


def eq(a, b, path=""):
    if isinstance(a, dict) and isinstance(b, dict):
        if a.keys() != b.keys():
            return f"{path}: keys differ {sorted(a)} vs {sorted(b)}"
        for k in a:
            r = eq(a[k], b[k], f"{path}.{k}")
            if r:
                return r
        return None
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            return f"{path}: length {len(a)} vs {len(b)}"
        for i, (x, y) in enumerate(zip(a, b)):
            r = eq(x, y, f"{path}[{i}]")
            if r:
                return r
        return None
    if isinstance(a, bool) or isinstance(b, bool):   # bool before number check
        return None if a == b else f"{path}: {a} vs {b}"
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        if math.isclose(a, b, rel_tol=RTOL, abs_tol=ATOL):
            return None
        return f"{path}: {a} vs {b} (out of tolerance)"
    return None if a == b else f"{path}: {a!r} vs {b!r}"


def main(argv):
    if len(argv) % 2 or not argv:
        print("usage: check_artifact_drift.py <committed> <fresh> [pairs...]")
        return 2
    bad = 0
    for committed, fresh in zip(argv[::2], argv[1::2]):
        with open(committed, encoding="utf-8") as f:
            a = json.load(f)
        with open(fresh, encoding="utf-8") as f:
            b = json.load(f)
        r = eq(a, b, committed)
        if r:
            print(f"DRIFT  {committed}: {r}")
            bad += 1
        else:
            print(f"OK     {committed} (within rtol {RTOL})")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
