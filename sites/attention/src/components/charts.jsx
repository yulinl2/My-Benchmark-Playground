// Tiny dependency-free SVG charts.
import React from 'react'

const PAD = { l: 46, r: 16, t: 14, b: 34 }

export function LineChart({ series, width = 460, height = 260, yMax = 1,
                            yLabel = '', xLabel = '', xTicks }) {
  const iw = width - PAD.l - PAD.r
  const ih = height - PAD.t - PAD.b
  const xs = series[0]?.points.map(p => p.x) ?? []
  const xmin = Math.min(...xs), xmax = Math.max(...xs)
  const sx = x => PAD.l + (xmax === xmin ? 0 : (x - xmin) / (xmax - xmin)) * iw
  const sy = y => PAD.t + ih - (y / yMax) * ih
  const yGrid = [0, 0.25, 0.5, 0.75, 1].map(f => f * yMax)
  const ticks = xTicks ?? xs
  return (
    <svg width={width} height={height} role="img">
      {yGrid.map((g, i) => (
        <g key={i}>
          <line x1={PAD.l} x2={width - PAD.r} y1={sy(g)} y2={sy(g)} stroke="#283349" />
          <text x={PAD.l - 8} y={sy(g) + 4} textAnchor="end" className="barlabel">
            {g.toFixed(2)}
          </text>
        </g>
      ))}
      {ticks.map((t, i) => (
        <text key={i} x={sx(t)} y={height - 12} textAnchor="middle" className="barlabel">{t}</text>
      ))}
      {xLabel && <text x={PAD.l + iw / 2} y={height - 0} textAnchor="middle" className="barlabel">{xLabel}</text>}
      {yLabel && <text transform={`translate(12 ${PAD.t + ih / 2}) rotate(-90)`} textAnchor="middle" className="barlabel">{yLabel}</text>}
      {series.map((s, si) => (
        <g key={si}>
          <polyline fill="none" stroke={s.color} strokeWidth="2.2"
            strokeDasharray={s.dashed ? '5 4' : ''}
            points={s.points.map(p => `${sx(p.x)},${sy(p.y)}`).join(' ')} />
          {s.points.map((p, pi) => (
            <circle key={pi} cx={sx(p.x)} cy={sy(p.y)} r="3.2" fill={s.color} />
          ))}
        </g>
      ))}
    </svg>
  )
}

export function GroupedBars({ groups, width = 460, height = 260, yMax = 1,
                             colorFor, yLabel = 'accuracy' }) {
  // groups: [{label, bars:[{key, value}]}]
  const iw = width - PAD.l - PAD.r
  const ih = height - PAD.t - PAD.b
  const n = groups.length
  const gw = iw / n
  const sy = v => PAD.t + ih - (v / yMax) * ih
  return (
    <svg width={width} height={height} role="img">
      {[0, 0.25, 0.5, 0.75, 1].map((f, i) => (
        <g key={i}>
          <line x1={PAD.l} x2={width - PAD.r} y1={sy(f * yMax)} y2={sy(f * yMax)} stroke="#283349" />
          <text x={PAD.l - 8} y={sy(f * yMax) + 4} textAnchor="end" className="barlabel">{(f * yMax).toFixed(2)}</text>
        </g>
      ))}
      {groups.map((g, gi) => {
        const bw = Math.min(34, (gw - 12) / g.bars.length)
        const x0 = PAD.l + gi * gw + (gw - bw * g.bars.length) / 2
        return (
          <g key={gi}>
            {g.bars.map((b, bi) => {
              const h = (b.value / yMax) * ih
              return (
                <g key={bi}>
                  <rect x={x0 + bi * bw} y={sy(b.value)} width={bw - 3} height={h}
                    rx="2" fill={colorFor(b.key)} />
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
