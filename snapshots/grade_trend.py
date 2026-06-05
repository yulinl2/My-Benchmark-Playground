#!/usr/bin/env python3
"""Grade trend-anomaly-causal-inference outputs with the fork verifier's weighting."""
import json, subprocess, sys, os
from pathlib import Path

OUTPUT_DIR = sys.argv[1]
TASK = Path(__file__).resolve().parent / "pr372-trend-anomaly-causal-inference" / "task"
report_json = "/tmp/trend_report.json"

P0 = ["test_cleaned_data[file_config0]", "test_cleaned_data[file_config1]",
      "test_anomaly_detection", "test_feature_engineering", "test_user_category_period_aggregated",
      "test_causal_report_structure[metadata-keys0]", "test_causal_report_structure[surge_categories-None]",
      "test_causal_report_structure[slump_categories-None]", "test_causal_report_structure[summary-keys3]"]
P1 = ["test_survey_cleaning_correctness", "test_purchase_cleaning_correctness",
      "test_anomaly_detection_correctness", "test_feature_engineering_correctness",
      "test_causal_analysis_baseline_period", "test_causal_report_categories", "test_causal_report_did_correctness"]
P2 = ["test_cross_file_consistency", "test_purchase_aggregation_correctness", "test_did_aggregation_independence"]

env = dict(os.environ, OUTPUT_DIR=OUTPUT_DIR)
subprocess.run([sys.executable, "-m", "pytest", str(TASK / "tests" / "test_outputs.py"),
                "-q", "--json-report", f"--json-report-file={report_json}",
                "-p", "no:cacheprovider", "--tb=line"],
               env=env, cwd=str(TASK / "tests"))

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
