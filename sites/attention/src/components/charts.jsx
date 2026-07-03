// Tiny dependency-free SVG charts with a hover layer (crosshair + tooltip on
// lines, per-mark tooltip on bars/cells). Colors are passed in by role from the
// validated palette in App.jsx.
import React, { useMemo, useRef, useState } from 'react'

const PAD = { l: 46, r: 16, t: 14, b: 34 }

function useTooltip() {
  const [tip, setTip] = useState(null) // {x, y, lines:[{color?, text}]}
  const wrapRef = useRef(null)
  const show = (evt, lines) => {
    const r = wrapRef.current?.getBoundingClientRect()
    if (!r) return
    setTip({ x: evt.clientX - r.left, y: evt.clientY - r.top, lines })
  }
  const hide = () => setTip(null)
  const node = tip && (
    <div className="tip" style={{ left: tip.x + 12, top: tip.y + 12 }}>
      {tip.lines.map((l, i) => (
        <div key={i} className="tip-row">
          {l.color && <i style={{ background: l.color }} />}<span>{l.text}</span>
        </div>
      ))}
    </div>
  )
  return { wrapRef, show, hide, node }
}

export function LineChart({ series, width = 460, height = 260, yMax = 1,
                            yLabel = '', xLabel = '', xTicks, fmt = v => v.toFixed(3) }) {
  const iw = width - PAD.l - PAD.r
  const ih = height - PAD.t - PAD.b
  const xs = series[0]?.points.map(p => p.x) ?? []
  const xmin = Math.min(...xs), xmax = Math.max(...xs)
  const sx = x => PAD.l + (xmax === xmin ? 0 : (x - xmin) / (xmax - xmin)) * iw
  const sy = y => PAD.t + ih - (y / yMax) * ih
  const yGrid = [0, 0.25, 0.5, 0.75, 1].map(f => f * yMax)
  const ticks = xTicks ?? xs
  const { wrapRef, show, hide, node } = useTooltip()
  const [hoverX, setHoverX] = useState(null)

  const onMove = evt => {
    const r = wrapRef.current.getBoundingClientRect()
    const px = evt.clientX - r.left
    // nearest data x
    let best = null, bd = Infinity
    for (const x of xs) { const d = Math.abs(sx(x) - px); if (d < bd) { bd = d; best = x } }
    if (best == null) return
    setHoverX(best)
    show(evt, [
      { text: `${xLabel || 'x'} = ${best}` },
      ...series.map(s => {
        const p = s.points.find(q => q.x === best)
        return p ? { color: s.color, text: `${s.name}: ${fmt(p.y)}` } : null
      }).filter(Boolean),
    ])
  }
  const onLeave = () => { hide(); setHoverX(null) }

  return (
    <div className="chart-wrap" ref={wrapRef}>
      <svg width={width} height={height} role="img" onMouseMove={onMove} onMouseLeave={onLeave}>
        {yGrid.map((g, i) => (
          <g key={i}>
            <line x1={PAD.l} x2={width - PAD.r} y1={sy(g)} y2={sy(g)} stroke="var(--grid)" />
            <text x={PAD.l - 8} y={sy(g) + 4} textAnchor="end" className="barlabel">{g.toFixed(2)}</text>
          </g>
        ))}
        {ticks.map((t, i) => (
          <text key={i} x={sx(t)} y={height - 12} textAnchor="middle" className="barlabel">{t}</text>
        ))}
        {xLabel && <text x={PAD.l + iw / 2} y={height - 0} textAnchor="middle" className="barlabel">{xLabel}</text>}
        {yLabel && <text transform={`translate(12 ${PAD.t + ih / 2}) rotate(-90)`} textAnchor="middle" className="barlabel">{yLabel}</text>}
        {hoverX != null && (
          <line x1={sx(hoverX)} x2={sx(hoverX)} y1={PAD.t} y2={PAD.t + ih} stroke="var(--baseline)" strokeDasharray="3 3" />
        )}
        {series.map((s, si) => (
          <g key={si}>
            <polyline fill="none" stroke={s.color} strokeWidth="2"
              strokeDasharray={s.dashed ? '5 4' : ''}
              points={s.points.map(p => `${sx(p.x)},${sy(p.y)}`).join(' ')} />
            {s.points.map((p, pi) => (
              <circle key={pi} cx={sx(p.x)} cy={sy(p.y)} r={p.x === hoverX ? 4.5 : 3}
                fill={s.color} stroke="var(--panel)" strokeWidth={p.x === hoverX ? 2 : 0} />
            ))}
          </g>
        ))}
      </svg>
      {node}
    </div>
  )
}

export function GroupedBars({ groups, width = 460, height = 260, yMax = 1,
                             colorFor, yLabel = 'accuracy', tipFor }) {
  // groups: [{label, bars:[{key, value}]}]
  const iw = width - PAD.l - PAD.r
  const ih = height - PAD.t - PAD.b
  const n = groups.length
  const gw = iw / n
  const sy = v => PAD.t + ih - (v / yMax) * ih
  const { wrapRef, show, hide, node } = useTooltip()
  return (
    <div className="chart-wrap" ref={wrapRef}>
      <svg width={width} height={height} role="img">
        {[0, 0.25, 0.5, 0.75, 1].map((f, i) => (
          <g key={i}>
            <line x1={PAD.l} x2={width - PAD.r} y1={sy(f * yMax)} y2={sy(f * yMax)} stroke="var(--grid)" />
            <text x={PAD.l - 8} y={sy(f * yMax) + 4} textAnchor="end" className="barlabel">{(f * yMax).toFixed(2)}</text>
          </g>
        ))}
        {groups.map((g, gi) => {
          const bw = Math.min(34, (gw - 12) / g.bars.length)
          const x0 = PAD.l + gi * gw + (gw - bw * g.bars.length) / 2
          return (
            <g key={gi}>
              {g.bars.map((b, bi) => {
                const h = Math.max(2, (b.value / yMax) * ih)
                const color = colorFor(b.key)
                return (
                  <g key={bi}>
                    <rect x={x0 + bi * bw} y={sy(b.value)} width={bw - 3} height={h}
                      rx="3" fill={color}
                      onMouseMove={e => show(e, tipFor ? tipFor(g, b) : [
                        { text: g.label },
                        { color, text: `accuracy ${b.value.toFixed(3)}` },
                      ])}
                      onMouseLeave={hide} />
                    <text x={x0 + bi * bw + (bw - 3) / 2} y={sy(b.value) - 4}
                      textAnchor="middle" className="barlabel">{b.value.toFixed(2)}</text>
                  </g>
                )
              })}
              <text x={PAD.l + gi * gw + gw / 2} y={height - 14} textAnchor="middle" className="barlabel">{g.label}</text>
            </g>
          )
        })}
        <text transform={`translate(12 ${PAD.t + ih / 2}) rotate(-90)`} textAnchor="middle" className="barlabel">{yLabel}</text>
      </svg>
      {node}
    </div>
  )
}

// Sequential one-hue heatmap for attention matrices. Value 0 recedes to the
// surface; value 1 is the brightest ramp step (single blue hue, dark-mode
// inversion of light->dark).
const RAMP_LO = [10, 13, 20]      // near-surface
const RAMP_HI = [134, 182, 239]   // #86b6ef (blue ramp step 250)
export function heatColor(v) {
  const t = Math.max(0, Math.min(1, v))
  const c = RAMP_LO.map((lo, i) => Math.round(lo + (RAMP_HI[i] - lo) * t))
  return `rgb(${c[0]},${c[1]},${c[2]})`
}

export function Heatmap({ matrix, size = 216, title = '', sub = '', tipLabel = 'A' }) {
  const N = matrix.length || 1
  const cell = size / N
  const { wrapRef, show, hide, node } = useTooltip()
  return (
    <div className="chart-wrap heat" ref={wrapRef}>
      {title ? <div className="heat-title">{title}</div> : null}
      <svg width={size} height={size} role="img" style={{ borderRadius: 6 }}>
        <rect x="0" y="0" width={size} height={size} fill={heatColor(0)} />
        {matrix.map((row, i) => row.map((v, j) => (
          v > 0.004 ? (
            <rect key={i + '_' + j} x={j * cell} y={i * cell}
              width={Math.max(cell, 1)} height={Math.max(cell, 1)} fill={heatColor(v)}
              onMouseMove={e => show(e, [{ text: `${tipLabel}[${i + 1}, ${j + 1}] = ${v.toFixed(3)}` }])}
              onMouseLeave={hide} />
          ) : null
        )))}
      </svg>
      {sub ? <div className="heat-sub">{sub}</div> : null}
      {node}
    </div>
  )
}

export function Legend({ items }) {
  return (
    <div className="legend">
      {items.map((it, i) => (
        <span key={i}><i style={{ background: it.color }} />{it.label}</span>
      ))}
    </div>
  )
}
