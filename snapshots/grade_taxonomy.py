#!/usr/bin/env python3
"""Grade taxonomy-tree-merge outputs with the fork verifier's weighting."""
import json, subprocess, sys, os
from pathlib import Path

OUTPUT_DIR = sys.argv[1]
TASK = Path(__file__).resolve().parent / "pr570-taxonomy-tree-merge" / "task"
report_json = "/tmp/taxonomy_report.json"

P0 = ["test_output_files_exist", "test_full_mapping_format", "test_hierarchy_format",
      "test_source_preservation", "test_depth_filtering", "test_prefix_removal",
      "test_cross_source_deduplication", "test_hierarchical_structure", "test_pyramid_distribution",
      "test_cluster_size_balance", "test_category_naming_constraints", "test_parent_word_exclusion",
      "test_lemmatization_applied"]
P1 = ["test_path_representativeness", "test_sibling_distinctiveness", "test_children_count_limit",
      "test_hierarchy_depth_consistency", "test_mapping_completeness", "test_hierarchy_coverage",
      "test_source_balance"]
P2 = ["test_no_empty_clusters", "test_special_characters_removed"]

env = dict(os.environ, OUTPUT_DIR=OUTPUT_DIR)
subprocess.run([sys.executable, "-m", "pytest", str(TASK / "tests" / "test_outputs.py"),
                "-q", "--json-report", f"--json-report-file={report_json}",
                "-p", "no:cacheprovider", "--tb=line"], env=env)

rep = json.load(open(report_json))
passed = {t["nodeid"].split("::")[-1] for t in rep["tests"] if t["outcome"] == "passed"}
p0 = sum(t in passed for t in P0); p1 = sum(t in passed for t in P1); p2 = sum(t in passed for t in P2)
score = p0/len(P0)*0.50 + p1/len(P1)*0.35 + p2/len(P2)*0.15
print(f"\n==== {OUTPUT_DIR} ====")
print(f"P0 {p0}/{len(P0)}  P1 {p1}/{len(P1)}  P2 {p2}/{len(P2)}  ->  reward {score:.4f}")
for grp, names in (("P0", P0), ("P1", P1), ("P2", P2)):
    for t in names:
        if t not in passed:
            print(f"  FAIL [{grp}] {t}")
