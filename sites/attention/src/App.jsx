import React, { useMemo, useState, useEffect } from 'react'
import { LineChart, GroupedBars, Legend, Heatmap } from './components/charts.jsx'
import { FAMILIES } from './generators.js'
import rankSep from './data/rank_separation.json'
import trainCurves from './data/train_curves.json'
import depthSep from './data/depth_separation.json'
import sweep from './data/sweep_results.json'
import sweepRep from './data/sweep_replicated.json'
import tier3 from './data/trained_tiny_mqar.json'

// Series colors: validated categorical slots (dark steps) on the panel surface —
// validate_palette.js: worst-adjacent CVD ΔE 35.9, all >= 3:1 vs #141a26.
// Status colors are the fixed status palette; a status-colored mark is always
// paired with its printed value, so color never carries meaning alone.
const C = { soft: '#3987e5', lin: '#e66767', floor: '#c98500', good: '#0ca30c', warn: '#fab219', bad: '#d03b3b' }
const scoreColor = v => (v >= 0.95 ? C.good : v >= 0.5 ? C.warn : C.bad)
const numIn = s => { const m = String(s).match(/\d+/); return m ? +m[0] : 0 }

const SECTIONS = [
  { id: 'overview', grp: 'Start', label: 'Overview' },
  { id: 'theory', grp: 'The claim', label: 'Theory & rank explorer' },
  { id: 'matrices', grp: 'The claim', label: 'Attention matrices' },
  { id: 'statebound', grp: 'The claim', label: 'State bottleneck (Thm II)' },
  { id: 'numeric', grp: 'The claim', label: 'Numeric proofs' },
  { id: 'depth', grp: 'The claim', label: 'Depth (multi-layer)' },
  { id: 'families', grp: 'Generalization', label: 'Task families (live)' },
  { id: 'pointerchase', grp: 'Generalization', label: 'Pointer chase' },
  { id: 'sweep', grp: 'Generalization', label: 'Haiku scaling sweep' },
  { id: 'tier3', grp: 'Generalization', label: 'Tier-3: trained cross-arch' },
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
        {sec === 'matrices' && <Matrices />}
        {sec === 'statebound' && <StateBottleneck />}
        {sec === 'numeric' && <Numeric />}
        {sec === 'depth' && <Depth />}
        {sec === 'families' && <Families />}
        {sec === 'pointerchase' && <PointerChase />}
        {sec === 'sweep' && <Sweep />}
        {sec === 'tier3' && <Tier3 />}
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

function mulberry32(a) {
  return function () {
    a |= 0; a = (a + 0x6D2B79F5) | 0
    let t = Math.imul(a ^ (a >>> 15), 1 | a)
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296
  }
}

function computeMatrices(N, m, seed) {
  const r = mulberry32(((seed + 1) * 2654435761) >>> 0)
  const pi = [...Array(N).keys()]
  for (let i = N - 1; i > 0; i--) { const j = Math.floor(r() * (i + 1));[pi[i], pi[j]] = [pi[j], pi[i]] }
  const P = Array.from({ length: N }, (_, i) => Array.from({ length: N }, (_, j) => (j === pi[i] ? 1 : 0)))
  // softmax attention: logits = beta * P  ->  sharp, ~one-hot
  const beta = 9
  const soft = P.map(row => {
    const ex = row.map(v => Math.exp(beta * v)); const s = ex.reduce((a, b) => a + b, 0)
    return ex.map(v => v / s)
  })
  // linear attention with m random features: phi(R e_{pi(i)}) . phi(R e_j), row-normalized -> rank <= m
  const R = Array.from({ length: m }, () => Array.from({ length: N }, () => r() * 2 - 1))
  const phiCol = k => R.map(rowm => { const x = rowm[k]; return x > 0 ? x + 1 : Math.exp(x) })
  const Q = pi.map(p => phiCol(p))
  const K = [...Array(N).keys()].map(j => phiCol(j))
  const lin = Q.map(qi => {
    const s = K.map(kj => qi.reduce((a, v, t) => a + v * kj[t], 0))
    const sum = s.reduce((a, b) => a + b, 0) + 1e-9
    return s.map(v => v / sum)
  })
  const fro = A => Math.sqrt(A.reduce((acc, row, i) => acc + row.reduce((b, v, j) => b + (v - P[i][j]) ** 2, 0), 0))
  const Pnorm = Math.sqrt(N)
  return { P, soft, lin, linErr: fro(lin) / Pnorm, softErr: fro(soft) / Pnorm, floor: Math.max(0, 1 - m / N) }
}

function Matrices() {
  const [N, setN] = useState(12)
  const [m, setM] = useState(3)
  const [seed, setSeed] = useState(0)
  const mm = Math.min(m, N)
  const { P, soft, lin, linErr, softErr, floor } = useMemo(() => computeMatrices(N, mm, seed), [N, mm, seed])
  const sz = 220
  // one-hue sequential ramp for all three panels (magnitude); identity is
  // carried by the title + tag chip, not by recoloring the ramp per panel.
  // Rows are scaled to their max — the standard way to read attention maps.
  const rowScale = A => A.map(row => { const mx = Math.max(...row) || 1; return row.map(v => v / mx) })
  const Panel = ({ title, sub, matrix, tag }) => (
    <div className="card" style={{ margin: 0 }}>
      <h3 style={{ marginTop: 0 }}>{title} {tag}</h3>
      <Heatmap matrix={rowScale(matrix)} size={sz} />
      <p className="note" style={{ marginBottom: 0 }}>{sub}</p>
    </div>
  )
  return (
    <>
      <h1>Attention matrices — see the separation</h1>
      <p className="lede">The proof in one picture. Each grid is the N×N attention matrix for a Gather(N) routing:
        row i should send all its weight to the source column π(i). Bright = high weight. Drag N and the linear
        feature dim m and watch what each architecture can actually draw.</p>
      <div className="card">
        <div className="controls">
          <div className="control"><label>N (context length) = <span className="val">{N}</span></label>
            <input type="range" min="4" max="28" value={N} onChange={e => setN(+e.target.value)} /></div>
          <div className="control"><label>m (linear feature dim) = <span className="val">{mm}</span></label>
            <input type="range" min="1" max="28" value={m} onChange={e => setM(+e.target.value)} /></div>
          <div className="control"><label>seed</label>
            <input className="seedbox" style={{ width: 64 }} type="number" value={seed} onChange={e => setSeed(+e.target.value || 0)} /></div>
        </div>
      </div>
      <div className="grid3">
        <Panel title="Target P_π" tag={<span className="tag good">rank {N}</span>}
          matrix={P} sub="What the task demands: a permutation. One bright cell per row." />
        <Panel title="Softmax" tag={<span className="tag soft">realizes it</span>}
          matrix={soft} sub={`Sharpened logits → ≈ P_π. Rel. error ${softErr.toFixed(3)}.`} />
        <Panel title="Linear (m feats)" tag={<span className="tag bad">rank ≤ {mm}</span>}
          matrix={lin} sub={`A smear it can't sharpen past rank ${mm}. Rel. error ${linErr.toFixed(3)}.`} />
      </div>
      <div className="card">
        <h3>What you're seeing</h3>
        <p>Softmax can make each row a spike at the right column, so it draws the permutation almost exactly. The
          linear map is a product of rank-{mm} feature matrices — its picture is forced to be a low-rank smear, and as
          you shrink m below N it physically cannot place N independent spikes. The rigorous floor on the best possible
          rank-≤m map is <span className="val">1 − m/N = {floor.toFixed(3)}</span> (Theorem I); the random-feature map
          shown here sits above it.</p>
        <p className="note">Tip: set m = N and the linear smear sharpens; drop m and the permutation dissolves while
          softmax stays crisp. That gap, widening with N, is the whole thesis.</p>
      </div>
    </>
  )
}

function StateBottleneck() {
  const [N, setN] = useState(64)
  const [m, setM] = useState(16)
  // round-robin assignment of N KV pairs into m fixed slots
  const loads = Array.from({ length: m }, (_, j) => Math.floor(N / m) + (j < (N % m) ? 1 : 0))
  const singles = loads.filter(l => l === 1).length
  const collided = loads.filter(l => l >= 2).length
  const recall = Math.min(1, m / N)
  const Ns = [2, 4, 8, 16, 32, 64, 128, 256]
  const bitsNeed = Math.round(N * Math.log2(Math.max(2, N)))
  const bitsHave = m * 16   // ~fp16 per slot
  const slotColor = l => (l === 0 ? '#1b2433' : l === 1 ? C.good : C.bad)
  return (
    <>
      <h1>State bottleneck — the streaming view (Theorem II)</h1>
      <p className="lede">Linear attention is a recurrent net with a <b>fixed-size state</b>: it must squeeze the whole
        prefix into <code>m</code> slots before any query. Softmax keeps every token in the KV cache (random access).
        Here are <code>N</code> key→value pairs being written into <code>m</code> slots — drag both and watch
        information collide.</p>
      <div className="card">
        <div className="controls">
          <div className="control"><label>N (key→value pairs) = <span className="val">{N}</span></label>
            <input type="range" min="2" max="256" value={N} onChange={e => setN(+e.target.value)} /></div>
          <div className="control"><label>m (fixed state slots) = <span className="val">{m}</span></label>
            <input type="range" min="1" max="64" value={m} onChange={e => setM(+e.target.value)} /></div>
        </div>
      </div>
      <div className="grid2">
        <div className="card">
          <h3 style={{ marginTop: 0 }}>Fixed state — {m} slots, {N} pairs</h3>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4 }}>
            {loads.map((l, j) => (
              <div key={j} title={`slot ${j}: ${l} pair(s)`} style={{
                width: 22, height: 22, borderRadius: 4, background: slotColor(l),
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontSize: 11, fontWeight: 700, color: '#fff'
              }}>{l >= 2 ? l : ''}</div>
            ))}
          </div>
          <Legend items={[
            { color: C.good, label: `singleton (recoverable) ×${singles}` },
            { color: C.bad, label: `collided (overwrite/interference) ×${collided}` },
          ]} />
          <p className="note" style={{ marginBottom: 0 }}>{N <= m
            ? 'N ≤ m: every pair gets its own slot — fully recoverable, like softmax.'
            : `N > m: ${N - m} pairs must share slots. Once written, collided values interfere; recall degrades.`}</p>
        </div>
        <div className="card">
          <h3 style={{ marginTop: 0 }}>Recall vs. number of pairs</h3>
          <LineChart width={440} yMax={1} xLabel="N (pairs)" yLabel="recall accuracy" xTicks={[2, 16, 64, 256]}
            series={[
              { name: 'softmax (KV cache)', color: C.soft, points: Ns.map(n => ({ x: n, y: 1 })) },
              { name: 'fixed state m', color: C.lin, points: Ns.map(n => ({ x: n, y: Math.min(1, m / n) })) },
            ]} />
          <Legend items={[
            { color: C.soft, label: 'softmax: random access → flat at 1' },
            { color: C.lin, label: 'fixed state: ≈ min(1, m/N)' },
          ]} />
        </div>
      </div>
      <div className="grid3">
        <Kpi v={recall.toFixed(2)} l={`fixed-state recall at N=${N}, m=${m} (≈ m/N)`} />
        <Kpi v="1.00" l="softmax recall (KV cache holds all N)" />
        <Kpi v={`${bitsNeed} ▸ ${bitsHave}`} l={`bits needed (≈N·log₂N) vs available (≈m·16) — loss when needed > have`} />
      </div>
      <p className="note">This is the communication-complexity argument made tangible: specifying which value goes with
        which of N keys needs ≈ N·log₂N bits at the prefix cut, but the state carries only ≈ m·(precision) bits. Grow N
        past that and recall must fall — exactly the MQAR / “Based” recall–throughput curve, and why the Haiku sweep’s
        recall families are the sharpest separation.</p>
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

function buildChain(L, seed) {
  const r = mulberry32(((seed + 7) * 40503) >>> 0)
  let pool = 'abcdefghijklmnopqrstuvwxyz'.split('')
  for (let i = pool.length - 1; i > 0; i--) { const j = Math.floor(r() * (i + 1));[pool[i], pool[j]] = [pool[j], pool[i]] }
  const cv = pool.slice(0, L + 1)
  const literal = String(10 + Math.floor(r() * 90))
  const chain = []
  for (let i = 0; i < L; i++) chain.push({ lhs: cv[i], rhs: cv[i + 1], lit: false })
  chain.push({ lhs: cv[L], rhs: literal, lit: true })
  const others = pool.slice(L + 1, L + 1 + Math.min(L + 1, pool.length - (L + 1)))
  const distract = others.map(n => ({ lhs: n, rhs: String(10 + Math.floor(r() * 90)), lit: true }))
  const all = [...chain, ...distract]
  for (let i = all.length - 1; i > 0; i--) { const j = Math.floor(r() * (i + 1));[all[i], all[j]] = [all[j], all[i]] }
  return { stmts: all, trace: cv, literal, query: cv[0] }
}

function PointerChase() {
  const [L, setL] = useState(6)
  const [seed, setSeed] = useState(0)
  const [step, setStep] = useState(0)
  const [playing, setPlaying] = useState(false)
  const { stmts, trace, literal, query } = useMemo(() => buildChain(L, seed), [L, seed])
  useEffect(() => { setStep(0); setPlaying(false) }, [L, seed])
  useEffect(() => {
    if (!playing) return
    if (step >= L) { setPlaying(false); return }
    const id = setTimeout(() => setStep(s => s + 1), 750)
    return () => clearTimeout(id)
  }, [playing, step, L])
  const visited = new Set(trace.slice(0, step + 1))
  const curVar = trace[Math.min(step, L)]
  const done = step >= L
  return (
    <>
      <h1>Pointer chase — how softmax resolves a chain</h1>
      <p className="lede">The Chain / multi-hop task: <code>{query}</code> points to another variable, which points to
        another… ending at a literal. Each hop is one sharp attention lookup (an induction head). Play it: softmax
        follows the chain by random access; a fixed-state model would have to hold the whole live binding table at once.</p>
      <div className="card">
        <div className="controls">
          <div className="control"><label>chain length L = <span className="val">{L}</span></label>
            <input type="range" min="2" max="14" value={L} onChange={e => setL(+e.target.value)} /></div>
          <div className="control"><label>seed</label>
            <input className="seedbox" style={{ width: 64 }} type="number" value={seed} onChange={e => setSeed(+e.target.value || 0)} /></div>
          <div className="control"><label>&nbsp;</label>
            <div className="pill-row" style={{ margin: 0 }}>
              <span className="pill active" onClick={() => setPlaying(p => !p)}>{playing ? '⏸ pause' : '▶ play'}</span>
              <span className="pill" onClick={() => { setPlaying(false); setStep(s => Math.min(L, s + 1)) }}>step ▸</span>
              <span className="pill" onClick={() => { setPlaying(false); setStep(0) }}>↺ reset</span>
            </div>
          </div>
        </div>
      </div>
      <div className="grid2">
        <div className="card">
          <h3 style={{ marginTop: 0 }}>Assignments (shuffled — distractors mixed in)</h3>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 7 }}>
            {stmts.map((s, i) => {
              const isActive = s.lhs === curVar
              const isOnChain = visited.has(s.lhs) && trace.includes(s.lhs)
              return (
                <span key={i} className="mono" style={{
                  padding: '6px 10px', borderRadius: 8, fontSize: 13,
                  border: '1px solid ' + (isActive ? '#7c5cff' : '#283349'),
                  background: isActive ? 'rgba(124,92,255,.22)' : isOnChain ? 'rgba(12,163,12,.14)' : '#141a26',
                  color: isActive ? '#fff' : isOnChain ? '#cdeed8' : '#8b97ab',
                }}>Let {s.lhs} = {s.rhs}.</span>
              )
            })}
          </div>
        </div>
        <div className="card">
          <h3 style={{ marginTop: 0 }}>Resolution trace</h3>
          <div className="mono" style={{ fontSize: 16, lineHeight: 2 }}>
            {trace.slice(0, step + 1).map((v, i) => (
              <span key={i}>
                <span style={{ color: i === step && !done ? '#7c5cff' : C.good, fontWeight: 700 }}>{v}</span>
                {i < step ? <span style={{ color: '#8b97ab' }}> → </span> : null}
              </span>
            ))}
            {done ? <span style={{ color: '#8b97ab' }}> = <span style={{ color: C.floor, fontWeight: 700 }}>{literal}</span></span> : null}
          </div>
          <p className="note">hop {Math.min(step, L)} / {L}{done ? ` — resolved: ${query} = ${literal}` : ` — now following ${curVar}`}</p>
          <div className="formula" style={{ marginTop: 8 }}>{done
            ? `Softmax: ${L} sharp lookups (O(L) layers, or O(log L) with pointer-jumping). Answer = ${literal}.`
            : `Reading the binding for "${curVar}" with one attention lookup…`}</div>
        </div>
      </div>
      <p className="note">Each green hop is an induction-head-style copy: query the current name, attend to its single
        defining line, jump to the value. Softmax can do this at any distance (random access). A fixed-state recurrence
        must instead carry every live binding forward in O(1) memory — which is the Theorem II bottleneck once the table
        outgrows the state.</p>
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

      <h2>Replication (fresh seeds) — what survived, what was an artifact</h2>
      <p className="note">Every claim cell re-run on 4–10 fresh seeds, and sequence tasks re-scored with an
        alignment-robust LCS grader alongside the strict positional one. Two corrections to the single-seed story
        above: <b>(1)</b> the multihop t32 “cliff” (0.00) did <b>not</b> replicate — 1.000 across 10 fresh seeds; the
        original was a formatting artifact. <b>(2)</b> much of the sequence-task decay is positional-grading artifact
        (one dropped line zeroes everything after it): under LCS the decay is far milder — the honest routing signal.</p>
      <div className="grid2">
        {['gather', 'selective_copy', 'sort_by_key'].map(t => {
          const cells = sweepRep.cells.filter(c => c.task === t && c.lcs_mean != null)
            .sort((a, b) => numIn(a.label) - numIn(b.label))
          return (
            <div className="card" key={t}>
              <h3>{t} — positional vs LCS (mean over fresh seeds)</h3>
              <GroupedBars width={440} height={230}
                groups={cells.map(c => ({
                  label: c.label,
                  bars: [
                    { key: 'pos', value: c.positional_mean, sd: c.positional_sd, n: c.n_fresh_seeds },
                    { key: 'lcs', value: c.lcs_mean, sd: c.lcs_sd, n: c.n_fresh_seeds },
                  ],
                }))}
                colorFor={k => (k === 'lcs' ? C.soft : C.floor)}
                tipFor={(g, b) => [
                  { text: `${t} ${g.label}` },
                  { color: b.key === 'lcs' ? C.soft : C.floor, text: `${b.key === 'lcs' ? 'LCS' : 'positional'} ${b.value.toFixed(3)} ± ${b.sd.toFixed(3)} (n=${b.n})` },
                ]} />
              <Legend items={[
                { color: C.floor, label: 'positional (strict order)' },
                { color: C.soft, label: 'LCS (alignment-robust)' },
              ]} />
            </div>
          )
        })}
        <div className="card">
          <h3>Replicated point estimates (n = fresh seeds)</h3>
          <table>
            <thead><tr><th>cell</th><th>n</th><th>positional</th><th>LCS</th></tr></thead>
            <tbody>{sweepRep.cells.slice().sort((a, b) => a.task.localeCompare(b.task) || numIn(a.label) - numIn(b.label)).map((c, i) => (
              <tr key={i}><td className="mono">{c.task} {c.label}</td><td className="mono">{c.n_fresh_seeds}</td>
                <td className="mono">{c.positional_mean.toFixed(3)} ± {c.positional_sd.toFixed(3)}</td>
                <td className="mono">{c.lcs_mean != null ? `${c.lcs_mean.toFixed(3)} ± ${c.lcs_sd.toFixed(3)}` : '—'}</td></tr>
            ))}</tbody>
          </table>
          <p className="note" style={{ marginBottom: 0 }}>multihop t32: 1.000 ± 0.000 over 10 fresh seeds — the
            single-seed 0.00 above is retracted as an artifact, not a capability cliff.</p>
        </div>
      </div>

      <h2>All instances (original single-seed run — kept for the record)</h2>
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

function Tier3() {
  const byKind = kind => tier3.rows.filter(r => r.kind === kind).sort((a, b) => a.K - b.K)
  const sm = byKind('softmax'), lin = byKind('linear')
  const gapK = 32
  const smK = sm.find(r => r.K === gapK), linK = lin.find(r => r.K === gapK)
  return (
    <>
      <h1>Tier-3 — the trained cross-architecture separation (P4)</h1>
      <p className="lede">The decisive test: two <b>identical</b> 2-layer residual stacks (~127K params, d=64), differing
        <b> only</b> in the mixer — softmax attention vs linear attention — each <b>trained from scratch</b> on MQAR with
        fresh key→value maps every batch (the Zoology protocol), then evaluated on 2,560 fresh sequences. No pretraining,
        no prompt-format luck: pure architecture.</p>
      <div className="card">
        <h3>Recall accuracy vs number of KV pairs (K)</h3>
        <LineChart width={560} height={300} yMax={1} xLabel="K (key→value pairs)" yLabel="recall accuracy"
          xTicks={[8, 16, 32, 64]}
          series={[
            { name: 'softmax mixer', color: C.soft, points: sm.map(r => ({ x: r.K, y: r.acc })) },
            { name: 'linear mixer', color: C.lin, points: lin.map(r => ({ x: r.K, y: r.acc })) },
          ]} />
        <Legend items={[
          { color: C.soft, label: 'softmax mixer (same params, same training)' },
          { color: C.lin, label: 'linear mixer' },
        ]} />
        <p className="note">{tier3.protocol}</p>
      </div>
      <div className="grid3">
        <Kpi v={smK ? smK.acc.toFixed(3) : '—'} l={`softmax at K=${gapK}`} />
        <Kpi v={linK ? linK.acc.toFixed(3) : '—'} l={`linear at K=${gapK} — same params, same training`} />
        <Kpi v={smK && linK ? (smK.acc - linK.acc).toFixed(3) : '—'} l="the architecture gap at K=32" />
      </div>
      <div className="card">
        <h3>Reading the curve honestly</h3>
        <p>K=8/16: both mixers solve the task — the state is big enough. <b>K=32: softmax 0.999, linear 0.342</b> — the
          fixed-state bottleneck bites exactly where Theorem II predicts (state can no longer hold all K bindings),
          while softmax's KV cache doesn't care. K=64: <i>both</i> collapse — that cell is an optimization/budget limit
          of the tiny d=64 model (softmax fails too), so it is <i>not</i> evidence of the separation; the separation
          claim rests on K=32.</p>
        <p className="note">Full protocol, zero-shot pilots (Pythia vs Mamba vs RWKV at 160M/410M) and scope caveats:
          <code> docs/06_tier3_pilot.md</code> on the research branch. Source: <code>src/tier3/train_tiny.py</code>;
          data: <code>results/tier3/trained_tiny_mqar.json</code>.</p>
      </div>
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
    ['docs/05_self_audit.md', 'Adversarial self-audit: what holds, what was overstated, scope limits'],
    ['docs/06_tier3_pilot.md', 'Tier-3 protocol + results (zero-shot pilots, task-trained grid)'],
    ['src/tier3/', 'Cross-architecture pilot + task-trained tiny models (torch)'],
    ['tests/run_tests.py', '36-check suite: generator/grader/theorem/spec contracts (CI-gated)'],
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
