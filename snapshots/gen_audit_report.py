#!/usr/bin/env python3
import json,os,datetime
os.chdir("/home/user/My-Benchmark-Playground")
DATE="2026-06-05"
META={
 "pr372":dict(pr=372,name="trend-anomaly-causal-inference",title="Add trend-anomaly-causal-inference task",
   branch="refs/pull/372/head",author="(contributor PR #372)",category="data-science",difficulty="hard",
   tags="data-cleaning, time-series, anomaly-detection, causal-inference, feature-engineering, pandas",
   desc="Given dirty e-commerce transaction + demographic survey data, clean both sources, detect "
        "category-level temporal anomalies, engineer features, and run a difference-in-differences causal "
        "analysis producing surge/slump categories and a structured report.",
   skills=[("data_cleaning","clean/normalize the dirty purchase + survey CSVs"),
           ("time_series_anomaly_detection","Prophet-based per-category anomaly detection"),
           ("feature_engineering","derive user/category/period aggregate features"),
           ("did_causal_analysis","difference-in-differences causal estimation")],
   reqs=["Cleaned purchase + survey files (schema + value correctness)","Anomaly detection outputs",
         "Feature-engineering aggregates","Causal report: metadata, surge/slump categories, DiD summary",
         "Cross-file consistency between cleaned outputs"],
   root="snapshots/pr372-trend-anomaly-causal-inference"),
 "pr570":dict(pr=570,name="taxonomy-tree-merge",title="Add taxonomy-tree-merge task",
   branch="refs/pull/570/head",author="(contributor PR #570)",category="ML/NLP",difficulty="hard",
   tags="taxonomy-alignment, hierarchical-clustering, embeddings, nlp, ecommerce, ontology-merging",
   desc="Unify product-category taxonomies from Amazon, Facebook and Google Shopping (10,939 paths) into one "
        "merged hierarchy via embedding + hierarchical clustering, with a deduped cross-source mapping and a "
        "depth/format/coverage-constrained unified tree.",
   skills=[("hierarchical-taxonomy-clustering","embedding + agglomerative clustering workflow to merge "
            "multi-source category trees with prefix/depth/coverage rules")],
   reqs=["Output files exist, correct schema","Hierarchy format + depth (1..5) constraints",
         "Prefix removal per level","unified_level_1 path coverage >=70%","Cross-source dedup, balance, "
         "no empty clusters","Lemmatization + special-char removal"],
   root="snapshots/pr570-taxonomy-tree-merge"),
}
def pct(r): return f"{round(r*100,2)}%"
TMPL_HEAD="="*80
def report(m):
    aud=m["root"]+"/audit"
    summ=json.load(open(aud+"/summary.json"))
    sk=json.load(open(aud+"/audit-claude-skills.json"))
    ns=json.load(open(aud+"/audit-claude-noskills.json"))
    si=list(summ["skill_impact"].values())[0]
    L=[]
    L.append(TMPL_HEAD); L.append(f"     PR #{m['pr']} BENCHMARK REPORT: {m['name']}"); L.append(TMPL_HEAD)
    L.append(f"Date:    {DATE}"); L.append(f"PR:      #{m['pr']} — {m['title']}")
    L.append(f"Branch:  {m['branch']}"); L.append(f"Author:  {m['author']}")
    L.append("\nHarness note: scores produced via harbor `claude-code -m claude-opus-4-8` (docker sandbox),")
    L.append("not the canonical `bench eval create -a claude-agent-acp`. Codex configs NOT run (Claude-only).")
    L.append("This is a Step-5 trajectory audit (audit-general C0/C1 + SkillsBench layer) over those runs.")
    L.append("\n"+TMPL_HEAD); L.append("                       TASK DESCRIPTION"); L.append(TMPL_HEAD)
    L.append(f"Task:        {m['name']}"); L.append(f"Category:    {m['category']}")
    L.append(f"Difficulty:  {m['difficulty']}"); L.append(f"Tags:        {m['tags']}")
    L.append(f"\nDescription:\n{m['desc']}")
    L.append("\nSkills Provided:")
    for n,p in m["skills"]: L.append(f"- {n}: {p}")
    L.append("\nKey Requirements:")
    for r in m["reqs"]: L.append(f"- {r}")
    L.append("\n"+TMPL_HEAD); L.append("                       ORACLE RESULTS"); L.append(TMPL_HEAD)
    L.append("Status:  PASSED\nReward:  1.0000  (solution/solve.sh)\nTests:   all passed")
    L.append("\n"+TMPL_HEAD); L.append("                       BENCHMARK RESULTS TABLE"); L.append(TMPL_HEAD)
    L.append("+--------------------+-----------------+--------+----------+-----------+")
    L.append("| Agent              | Model           | Skills | Accuracy | Verdict   |")
    L.append("+--------------------+-----------------+--------+----------+-----------+")
    L.append(f"| oracle             | -               | n/a    | 100.00%  | -         |")
    L.append(f"| harbor:claude-code | claude-opus-4-8 | Yes    | {pct(sk['reward']):>8} | {sk['verdict']:<9} |")
    L.append(f"| harbor:claude-code | claude-opus-4-8 | No     | {pct(ns['reward']):>8} | {ns['verdict']:<9} |")
    L.append(f"| codex-acp          | (not run)       | Yes/No | --       | N/A       |")
    L.append("+--------------------+-----------------+--------+----------+-----------+")
    L.append("\n"+TMPL_HEAD); L.append("                       SKILLS IMPACT ANALYSIS"); L.append(TMPL_HEAD)
    L.append(f"claude (harbor:claude-code):  with={pct(si['with_skills_reward'])}  "
             f"without={pct(si['no_skills_reward'])}  Δ={si['delta_pp']:+}pp  → {si['outcome'].upper()}")
    L.append(f"Trial count: {si['trial_count']} ({si['noise_caveat']})")
    L.append(f"\nSB-1 skill invocation (with-skills): {sk['skill_invocation']['status']} "
             f"via {sk['skill_invocation']['discovery_method']}")
    L.append(f"  skills_read: {sk['skill_invocation']['skills_read']}")
    L.append(f"  sub_files_read (references/*.md): {sk['skill_invocation']['sub_files_read'] or 'none'}")
    L.append(f"  SB-3 top_level_only={sk['skill_misuse']['top_level_only']} "
             f"partial_follow_through={sk['skill_misuse']['partial_follow_through']}")
    L.append("\nToken diagnostic (in/out/cost):")
    for tag,a in (("with-skills",sk),("without-skills",ns)):
        t=a["tokens"]; c=t.get('cost_usd'); cs=f"${round(c,2)}" if c is not None else "n/a (pre-reset run)"
        L.append(f"- claude {tag}: in={t['in']}, out={t['out']}, cost={cs}")
    L.append("- codex with/without: (not run)")
    L.append("\n"+TMPL_HEAD); L.append("                       FAILURE ANALYSIS"); L.append(TMPL_HEAD)
    any_fail=False
    for a in (sk,ns):
        if a["reward"]<0.999:
            any_fail=True
            L.append(f"\n[{a['config']}] reward={a['reward']}  bucket={a['failure_bucket']}  "
                     f"format_vs_reasoning={a['format_vs_reasoning']}")
            L.append(f"  failed_tests: {a.get('failed_tests')}")
            L.append(f"  root cause: {a.get('failure_evidence')}")
            L.append(f"  verbatim_final: {a['verbatim_final'][:200]!r}")
    if not any_fail: L.append("All configs reward 1.0 — no failures.")
    L.append("\n"+TMPL_HEAD); L.append("                       TRAJECTORY AUDIT (per job)"); L.append(TMPL_HEAD)
    for a in (sk,ns):
        tb=a["tool_breakdown"]; st=a["struggle"]
        L.append(f"\n[{a['config']}] verdict={a['verdict']}")
        L.append(f"  anti_cheat_read={a['anti_cheat_read']['status']}  anti_cheat_write={a['anti_cheat_write']['status']}")
        L.append(f"  agentic_floor={a['agentic_floor']['n_tool_calls']} ({a['agentic_floor']['verdict']})")
        L.append(f"  tool_breakdown: total={tb['total']} by_kind={tb['by_kind']} by_title={tb['by_title']}")
        L.append(f"  struggle={st['verdict']} (retries={st['retries']} rewrites={st['rewrites']} "
                 f"reversals={st['reversals']} exploration_loop={st['exploration_loop']})")
        L.append(f"  memorization={a['memorization_signal']['status']}  "
                 f"filesystem_pollution={a['filesystem_pollution']['status']}  self_doubt={a['self_doubt']['status']}")
    L.append("\n"+TMPL_HEAD); L.append("                       CRITICAL FINDINGS"); L.append(TMPL_HEAD)
    if m["pr"]==570:
        L.append("1. Skills HELP on this task (Δ=+21.5pp): with-skills nails the path-encoding contract (1.0);")
        L.append("   from-scratch builds a sound taxonomy but misses 3 P0 + 2 P1 output-contract tests (0.78).")
        L.append("2. SB-1 VERIFIED — agent invoked hierarchical-taxonomy-clustering via the Skill tool.")
        L.append("3. No-skills run shows struggle signals (1 repeat, 1 reversal) over 87 tool calls / 24 edits.")
    else:
        L.append("1. Skills are effectively a NO-OP here for opus-4.8 (Δ=-5pp): the model solves from scratch")
        L.append("   at 1.0, while the bundled skill pipeline drops 228 IDs and loses one P2 (0.95).")
        L.append("2. SB-1 VERIFIED — all 4 SKILL.md manifests read; pipeline mirrors the prescribed steps.")
        L.append("3. The single failure is a cross-file data-completeness loss, not format and not cheating.")
    L.append("\n"+TMPL_HEAD); L.append("                       RECOMMENDATION"); L.append(TMPL_HEAD)
    L.append(f"Verdict: {summ['pr_verdict']}")
    L.append("\n(Audit-only re-alignment to task-review Step 5; this is a model-column fill on opus-4.8, not a")
    L.append(" gate on the PR. Required changes: none from this audit. Suggested: run the canonical")
    L.append(" claude-agent-acp + codex-acp configs for a like-for-like maintainer number; re-run multi-trial")
    L.append(" since single-trial |Δ| is within the noise floor.)")
    L.append("\n"+TMPL_HEAD); L.append("                       ARTIFACTS"); L.append(TMPL_HEAD)
    L.append("audit/summary.json, audit/audit-claude-skills.json, audit/audit-claude-noskills.json")
    L.append("harbor_*/trajectory.json, harbor_*/verifier_report.json, harbor_*/job_result.json")
    L.append(TMPL_HEAD); L.append("                       END OF REPORT"); L.append(TMPL_HEAD)
    out=f"{m['root']}/audit/pr-{m['pr']}-{m['name']}-{DATE.replace('-','')}-run.txt"
    open(out,"w").write("\n".join(L)+"\n")
    print("wrote",out,f"({summ['pr_verdict']})")
for k in META: report(META[k])
