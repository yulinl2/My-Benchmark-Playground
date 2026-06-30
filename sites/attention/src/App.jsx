import React, { useMemo, useState } from 'react'
import { LineChart, GroupedBars, Legend } from './components/charts.jsx'
import { FAMILIES } from './generators.js'
import rankSep from './data/rank_separation.json'
import trainCurves from './data/train_curves.json'
import depthSep from './data/depth_separation.json'
import sweep from './data/sweep_results.json'

const C = { soft: '#3aa0ff', lin: '#ff6b6b', floor: '#f0b429', good: '#2fd07a', warn: '#f0b429', bad: '#ff6b6b' }
const scoreColor = v => (v >= 0.95 ? C.good : v >= 0.5 ? C.warn : C.bad)
const numIn = s => { const m = String(s).match(/\d+/); return m ? +m[0] : 0 }

const SECTIONS = [
  { id: 'overview', grp: 'Start', label: 'Overview' },
  { id: 'theory', grp: 'The claim', label: 'Theory & rank explorer' },
  { id: 'numeric', grp: 'The claim', label: 'Numeric proofs' },
  { id: 'depth', grp: 'The claim', label: 'Depth (multi-layer)' },
  { id: 'families', grp: 'Generalization', label: 'Task families (live)' },
  { id: 'sweep', grp: 'Generalization', label: 'Haiku scaling sweep' },
  { id: 'repro', grp: 'Meta', label: 'Repo & reproduce' },
]

export default function App() {
  const [sec, setSec] = useState('overview')
  const grps = [...new Set(SECTIONS.map(s => s.grp))]
  return (
    <div className="app">
      <aside className="sidebar">
        <div className="brand">Attention Separation
          <small>softmax vs. linear attention — audit console</small>
        </div>
        <nav className="nav">
          {grps.map(g => (
            <React.Fragment key={g}>
              <div className="grp">{g}</div>
              {SECTIONS.filter(s => s.grp === g).map(s => (
                <button key={s.id} className={sec === s.id ? 'active' : ''} onClick={() => setSec(s.id)}>{s.label}</button>
              ))}
            </React.Fragment>
          ))}
        </nav>
      </aside>
      <main className="main">
        {sec === 'overview' && <Overview go={setSec} />}
        {sec === 'theory' && <Theory />}
        {sec === 'numeric' && <Numeric />}
        {sec === 'depth' && <Depth />}
        {sec === 'families' && <Families />}
        {sec === 'sweep' && <Sweep />}
        {sec === 'repro' && <Repro />}
      </main>
    </div>
  )
}

function Overview({ go }) {
  const floorPts = rankSep.linear_rank_floor.map(r => ({ x: r.N, y: r.one_minus_Hm_over_N }))
  const linPts = rankSep.linear_rank_floor.map(r => ({ x: r.N, y: r.concrete_rankr_rel_err }))
  const smPts = rankSep.linear_rank_floor.map(r => ({ x: r.N, y: r.softmax_rel_err_beta30 }))
  return (
    <>
      <h1>Can a task be solvable from its prompt, yet impossible for linear attention?</h1>
      <p className="lede">A long-context, <b>self-contained</b> task family whose optimal attention is computable
        from the input alone, that softmax attention realizes at fixed cost but <b>any fixed-capacity linear-attention
        model cannot hit with high probability</b> — with the gap forced to grow as the task space is enriched. This
        console lets you audit every piece: the theorems, the runnable numeric proofs, the seven-family generator, and
        the scaling sweep on Haiku.</p>
      <div className="grid3">
        <Kpi v="2" l="separation theorems (rank bound + communication bound)" />
        <Kpi v="7" l="self-contained task families (numeric → NL)" />
        <Kpi v="27" l="Haiku sub-agent runs in the scaling sweep" />
      </div>
      <div className="card">
        <h3>The headline: Gather(N), gather error vs context length</h3>
        <LineChart yMax={1} xLabel="N (context length)" yLabel="relative gather error"
          xTicks={[8, 32, 64, 128, 256]}
          series={[
            { name: 'linear floor 1−Hm/N', color: C.floor, points: floorPts, dashed: true },
            { name: 'concrete rank-m linear', color: C.lin, points: linPts },
            { name: 'softmax (β=30)', color: C.soft, points: smPts },
          ]} />
        <Legend items={[
          { color: C.floor, label: 'Eckart–Young floor 1−Hm/N (rigorous lower bound)' },
          { color: C.lin, label: 'a concrete rank-m linear map' },
          { color: C.soft, label: 'softmax realizes the permutation → ~0' },
        ]} />
        <p className="note">Linear attention’s attention matrix has rank ≤ Hm; the optimal map is a permutation of rank N,
          so its relative error is ≥ 1 − Hm/N → 1. Softmax drives the error to 0. <a onClick={() => go('theory')} style={{ cursor: 'pointer' }}>See the theory ↗</a></p>
      </div>
      <div className="grid2">
        <div className="card"><h3>Why “self-contained” matters</h3>
          <p>The answer is a deterministic function of the prompt (follow the pointer, copy the tagged value). A failure
            therefore cannot be blamed on missing knowledge — only on the architecture. That makes the separation
            <i> attributable</i>.</p></div>
        <div className="card"><h3>What the sweep shows</h3>
          <p>Haiku (softmax) stays ~perfect on recall families up to k=128 / N=384 — exactly where fixed-state models
            provably need growing state — and degrades only <i>gradually with N</i> on permutation-output tasks: the
            predicted fingerprint, not a small-N cliff. <a onClick={() => go('sweep')} style={{ cursor: 'pointer' }}>Explore ↗</a></p></div>
      </div>
    </>
  )
}

function Kpi({ v, l }) { return <div className="kpi"><div className="v">{v}</div><div className="l">{l}</div></div> }

function Theory() {
  const [hm, setHm] = useState(8)
  const Ns = [8, 16, 32, 64, 128, 256, 512]
  const floor = Ns.map(N => ({ x: N, y: Math.max(0, 1 - hm / N) }))
  const sm = Ns.map(N => ({ x: N, y: 0 }))
  return (
    <>
      <h1>Theory & rank explorer</h1>
      <p className="lede">The separation reduces to two short arguments. Drag the linear capacity to see the floor move.</p>

      <h2>Theorem I — the Eckart–Young rank bound</h2>
      <div className="card">
        <div className="formula">Gather(N): optimal attention A* = P_π (a permutation, rank N, all singular values = 1).<br />
          Linear attention: A = Σ_h D_h⁻¹ φ(Q_h)φ(K_h)ᵀ  ⇒  rank(A) ≤ H·m.<br />
          Eckart–Young ⇒ rel. error²(AV, P_πV) ≥ (N − Hm)/N = <b>1 − Hm/N → 1.</b></div>
        <div className="controls">
          <div className="control">
            <label>linear capacity H·m = <span className="val">{hm}</span></label>
            <input type="range" min="1" max="64" value={hm} onChange={e => setHm(+e.target.value)} />
          </div>
          <div className="control"><label>floor at N=128</label><span className="val">{Math.max(0, 1 - hm / 128).toFixed(3)}</span></div>
          <div className="control"><label>floor at N=512</label><span className="val">{Math.max(0, 1 - hm / 512).toFixed(3)}</span></div>
        </div>
        <LineChart yMax={1} xLabel="N" yLabel="min relative error (any rank ≤ Hm map)"
          xTicks={[8, 32, 128, 512]}
          series={[{ name: 'floor', color: C.floor, points: floor }, { name: 'softmax', color: C.soft, points: sm }]} />
        <Legend items={[{ color: C.floor, label: 'linear floor 1 − Hm/N' }, { color: C.soft, label: 'softmax ≈ 0 (realizes P_π)' }]} />
        <p className="note">For any fixed capacity Hm, pick N large enough and the floor approaches 1 — the linear read-out
          learns almost nothing of a fresh random permutation. Multi-head only scales Hm by a constant.</p>
      </div>

      <h2>Theorem II — the recurrent-state / communication bound</h2>
      <div className="card">
        <p>Linear attention is equivalent to a linear-RNN with a fixed-size state Z ∈ ℝ^{`{m×d}`} (the SSM view). Reading
          the prompt left-to-right, it must compress the prefix into B = O(m·d·prec) bits before the queries. Answering
          arbitrary gather queries about a random permutation needs Θ(N log N) bits, so if B = o(N log N) the per-query
          error is bounded away from zero. Softmax is non-recurrent (random-access KV cache) and pays O(N) memory by design.</p>
        <p className="note">This is the same communication-complexity technique used by Sanford, Hsu &amp; Telgarsky
          (arXiv:2306.02896), and the empirical shadow of the recall-throughput tradeoff in “Based” (arXiv:2402.18668).</p>
        <div className="formula">overfit-vs-generalize: memorizing |S_N| = N! routings needs ≫ B bits; grow N and the
          model is forced off its memorized set, where the bound bites. Softmax <i>computes</i> the routing instead of storing it.</div>
      </div>
    </>
  )
}

function Numeric() {
  const rs = rankSep.linear_rank_floor
  const tc = trainCurves.rows
  return (
    <>
      <h1>Numeric proofs (runnable)</h1>
      <p className="lede">Outputs committed under <code>results/numeric/</code>, produced by
        <code> rank_separation.py</code> and <code>train.py</code>. Deterministic — no SVD-basis dependence.</p>

      <h2>Rank separation — Theorem I, measured</h2>
      <div className="card">
        <table>
          <thead><tr><th>N</th><th>rank(A*)</th><th>Eckart–Young 1−Hm/N</th><th>concrete rank-m err</th><th>softmax (β=30)</th></tr></thead>
          <tbody>{rs.map(r => (
            <tr key={r.N}><td className="mono">{r.N}</td><td className="mono">{r.rank_A_star}</td>
              <td className="mono" style={{ color: C.floor }}>{r.one_minus_Hm_over_N.toFixed(4)}</td>
              <td className="mono" style={{ color: C.lin }}>{r.concrete_rankr_rel_err.toFixed(4)}</td>
              <td className="mono" style={{ color: C.soft }}>{r.softmax_rel_err_beta30.toFixed(6)}</td></tr>
          ))}</tbody>
        </table>
      </div>

      <h2>Trained heads — softmax generalizes, linear collapses as m/N</h2>
      <div className="card">
        <LineChart yMax={1} xLabel="N" yLabel="held-out exact-match accuracy"
          series={[
            { name: 'softmax', color: C.soft, points: tc.map(r => ({ x: r.N, y: r.softmax_heldout_acc })) },
            { name: 'linear rank-m', color: C.lin, points: tc.map(r => ({ x: r.N, y: r.linear_rankm_concrete_acc })) },
          ]} />
        <Legend items={[
          { color: C.soft, label: 'trained softmax head, fresh held-out permutations' },
          { color: C.lin, label: 'concrete rank-m linear map (proxy) ≈ m/N' },
        ]} />
        <p className="note">m = {trainCurves.linear_feature_dim_m}. Softmax stays at 1.0 across N; the linear proxy falls as m/N.
          The rigorous statement is the error bound above — this argmax curve is its intuitive companion.</p>
      </div>
    </>
  )
}

function Depth() {
  const rp = depthSep.rank_of_product
  const th = depthSep.two_hop
  return (
    <>
      <h1>Depth does not rescue linear attention</h1>
      <p className="lede">Two-hop Gather (target T = P₂P₁, a rank-N permutation). From <code>depth_separation.py</code>.</p>
      <div className="grid2">
        <div className="card"><h3>Product of L rank-≤m maps stays rank ≤ m</h3>
          <table><thead><tr><th>layers L</th><th>rank(product)</th><th>m</th></tr></thead>
            <tbody>{rp.map(r => <tr key={r.L}><td className="mono">{r.L}</td><td className="mono">{r.rank_product}</td><td className="mono">{r.m}</td></tr>)}</tbody></table>
          <p className="note">Stacking frozen linear layers cannot raise the rank ceiling — it often lowers it.</p>
        </div>
        <div className="card"><h3>Two-hop routing error</h3>
          <LineChart width={420} yMax={1} xLabel="N" yLabel="relative error"
            series={[
              { name: 'softmax depth-2', color: C.soft, points: th.map(r => ({ x: r.N, y: r.softmax_rel_err })) },
              { name: 'linear depth-2', color: C.lin, points: th.map(r => ({ x: r.N, y: r.linear_rel_err })) },
              { name: 'floor', color: C.floor, dashed: true, points: th.map(r => ({ x: r.N, y: r.floor_1_minus_Hm_N })) },
            ]} />
          <Legend items={[{ color: C.soft, label: 'depth-2 softmax ≈ 0' }, { color: C.lin, label: 'depth-2 frozen linear' }, { color: C.floor, label: '1−Hm/N floor' }]} />
        </div>
      </div>
      <p className="note">Adaptive (recomputing) layers are covered by Theorem II rather than this frozen-product demo.</p>
    </>
  )
}

function Families() {
  const keys = Object.keys(FAMILIES)
  const [fam, setFam] = useState('mqar')
  const [seed, setSeed] = useState(0)
  const def = FAMILIES[fam]
  const [params, setParams] = useState(() => Object.fromEntries(def.knobs.map(k => [k[0], k[3]])))
  // reset params when family changes
  const onFam = f => { setFam(f); setParams(Object.fromEntries(FAMILIES[f].knobs.map(k => [k[0], k[3]]))) }
  const inst = useMemo(() => {
    try { return def.knobs.length ? def.fn(params, seed) : def.fn(seed) }
    catch (e) { return { prompt: 'error: ' + e.message, answer: '', meta: {} } }
  }, [fam, params, seed])
  return (
    <>
      <h1>Task families — live preview</h1>
      <p className="lede">Seven self-contained generators. These are in-browser reimplementations (JS PRNG) that mirror the
        Python generators’ structure — they show the task <i>shape</i> at any difficulty, not the exact committed instances.</p>
      <div className="pill-row">
        {keys.map(k => <span key={k} className={'pill' + (k === fam ? ' active' : '')} onClick={() => onFam(k)}>{k}</span>)}
      </div>
      <div className="card">
        <p style={{ marginTop: 0 }}>{def.blurb}</p>
        <div className="controls">
          {def.knobs.map(([name, min, max]) => (
            <div className="control" key={name}>
              <label>{name} = <span className="val">{params[name]}</span></label>
              <input type="range" min={min} max={max} value={params[name]}
                onChange={e => setParams(p => ({ ...p, [name]: +e.target.value }))} />
            </div>
          ))}
          <div className="control">
            <label>seed</label>
            <input className="seedbox" style={{ width: 70 }} type="number" value={seed} onChange={e => setSeed(+e.target.value || 0)} />
          </div>
        </div>
        <div className="note">meta: <span className="mono">{JSON.stringify(inst.meta)}</span></div>
      </div>
      <div className="grid2">
        <div className="card"><h3>Prompt (model input)</h3><div className="prompt">{inst.prompt}</div></div>
        <div className="card"><h3>Hidden answer key</h3><div className="prompt answer">{inst.answer}</div>
          <p className="note">Computed deterministically from the prompt — the optimum a faithful random-access reader achieves.</p></div>
      </div>
    </>
  )
}

function Sweep() {
  const rows = sweep.rows
  const byTask = useMemo(() => {
    const m = {}
    for (const r of rows) {
      (m[r.task] ||= {})
      const lab = r.label
      ;(m[r.task][lab] ||= []).push(r.score)
    }
    const out = {}
    for (const t of Object.keys(m)) {
      out[t] = Object.entries(m[t]).map(([label, scores]) => ({ label, value: scores.reduce((a, b) => a + b, 0) / scores.length, n: scores.length }))
        .sort((a, b) => numIn(a.label) - numIn(b.label))
    }
    return out
  }, [])
  const recall = ['mqar', 'chain', 'kv_lastwrite']
  const output = ['gather', 'selective_copy', 'sort_by_key', 'multihop_map']
  const Panel = t => (
    <div className="card" key={t}>
      <h3>{t}</h3>
      <GroupedBars width={440} height={230}
        groups={byTask[t].map(b => ({ label: b.label, bars: [{ key: scoreColor(b.value), value: b.value }] }))}
        colorFor={k => k} />
    </div>
  )
  return (
    <>
      <h1>Haiku scaling sweep — the degradation fingerprint</h1>
      <p className="lede">{sweep.rows.length} instances, in-session Haiku sub-agents (prompt-only), graded deterministically.
        Two qualitatively different regimes emerge.</p>

      <h2>Recall-robust — softmax stays flat (sharpest separation vs fixed-state)</h2>
      <p className="note">Exactly where fixed-state linear / SSM models provably need state growing with k (Zoology, Based) — Haiku does not.</p>
      <div className="grid3">{recall.map(Panel)}</div>

      <h2>High-rank output — softmax degrades with N (the predicted fingerprint)</h2>
      <p className="note">Graceful budget-limited decay as N grows — not a fixed small-N floor. Theory predicts a fixed-capacity linear model collapses earlier and faster on the same instances.</p>
      <div className="grid2">{output.map(Panel)}</div>

      <h2>All instances</h2>
      <div className="card">
        <table>
          <thead><tr><th>task</th><th>difficulty</th><th>meta</th><th>accuracy</th></tr></thead>
          <tbody>{rows.slice().sort((a, b) => a.task.localeCompare(b.task) || numIn(a.label) - numIn(b.label)).map((r, i) => (
            <tr key={i}><td>{r.task}</td><td className="mono">{r.label}</td>
              <td className="mono" style={{ color: '#8b97ab' }}>{JSON.stringify(r.meta)}</td>
              <td><span className="tag" style={{ background: scoreColor(r.score) + '28', color: scoreColor(r.score) }}>{r.score.toFixed(3)}</span></td></tr>
          ))}</tbody>
        </table>
      </div>
      <p className="note">Caveat: long-output tasks conflate attention with generation/throughput; the grader gives positional
        partial credit, so these are a faithful lower bound on “routing correct,” not an attention-only measurement.</p>
    </>
  )
}

function Repro() {
  const files = [
    ['docs/00_research_proposal.md', 'Question, formalization, two separation theorems, falsifiable predictions'],
    ['docs/01_task_family_spec.md', 'Formal task family T(N,k,ρ) and members'],
    ['docs/02_experimental_plan.md', 'Numeric / NL / Tier-3 plan'],
    ['docs/03_related_work.md', 'Literature anchors with verified arXiv ids'],
    ['docs/04_findings_generalization.md', 'Breadth + depth findings, sweep analysis'],
    ['src/numeric/rank_separation.py', 'Theorem I, runnable'],
    ['src/numeric/train.py', 'Trained-head curves'],
    ['src/numeric/depth_separation.py', 'Multi-layer demo'],
    ['src/nl/task_generator.py + extra_tasks.py', 'Seven NL generators'],
    ['src/nl/sweep.py', 'Scaling-sweep harness'],
    ['results/', 'Committed run outputs (this UI reads them)'],
  ]
  return (
    <>
      <h1>Repository & reproduce</h1>
      <p className="lede">Orphan research line <code>research/long-context-attention-expressivity-separation</code>;
        work on <code>claude/long-context-task-distribution-2iydu1</code> (PR #9).</p>
      <div className="card">
        <table><thead><tr><th>path</th><th>contents</th></tr></thead>
          <tbody>{files.map(([p, d]) => <tr key={p}><td className="mono">{p}</td><td style={{ color: '#c8d1de' }}>{d}</td></tr>)}</tbody></table>
      </div>
      <div className="card"><h3>Reproduce</h3>
        <div className="prompt">{`# numeric (numpy)
python3 src/numeric/rank_separation.py
python3 src/numeric/train.py
python3 src/numeric/depth_separation.py

# NL generators + base-suite grading
python3 src/nl/task_generator.py --demo
python3 src/nl/extra_tasks.py --demo
python3 src/nl/run_haiku_verification.py

# scaling sweep
python3 src/nl/sweep.py --emit <dir>
python3 src/nl/sweep.py --grade-dir <dir>

# this UI
cd app && npm install && npm run build   # -> app/dist`}</div>
      </div>
    </>
  )
}
