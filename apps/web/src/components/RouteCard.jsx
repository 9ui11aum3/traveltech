const MODE_ICON = { train: '🚄', bus: '🚌', plane: '✈️' }

function fmtDur(m) {
  if (m < 60) return `${m}min`
  return `${Math.floor(m / 60)}h${m % 60 ? ' ' + (m % 60) + 'm' : ''}`
}
function fmtPrice(e) { return `€${Math.round(e)}` }
function fmtCo2(kg) { return kg < 1 ? `${Math.round(kg * 1000)}g` : `${kg.toFixed(1)}kg` }

const THEMES = {
  fastest:  { accent: '#2563eb', bg: '#eff6ff', icon: '⚡' },
  cheapest: { accent: '#16a34a', bg: '#f0fdf4', icon: '💰' },
  greenest: { accent: '#059669', bg: '#ecfdf5', icon: '🌿' },
}

export default function RouteCard({ type, route, selected, onSelect }) {
  if (!route) return (
    <div style={cardBase}>
      <div style={{ padding: '2rem', textAlign: 'center', color: '#94a3b8', fontSize: '.9rem' }}>
        No {type} route found
      </div>
    </div>
  )

  const { accent, bg, icon } = THEMES[type]
  const label = type.charAt(0).toUpperCase() + type.slice(1)

  return (
    <div
      onClick={onSelect}
      style={{
        ...cardBase,
        border: selected ? `2px solid ${accent}` : '1.5px solid #e2e8f0',
        boxShadow: selected ? `0 0 0 3px ${accent}22` : 'none',
      }}
    >
      {/* Header */}
      <div style={{ ...cardHeader, background: bg }}>
        <div style={{ ...badge, background: accent }}>{icon}</div>
        <div>
          <div style={{ fontWeight: 700 }}>{label} Route</div>
          <div style={{ fontSize: '.75rem', color: '#64748b' }}>
            {route.transfers === 0 ? 'Direct' : `${route.transfers} transfer${route.transfers > 1 ? 's' : ''}`}
          </div>
        </div>
      </div>

      {/* Stats row */}
      <div style={statsRow}>
        <Stat label="Duration" value={fmtDur(route.total_duration)} highlight={type === 'fastest'} accent={accent} />
        <Stat label="Cost"     value={fmtPrice(route.total_price)}  highlight={type === 'cheapest'} accent={accent} />
        <Stat label="CO₂"     value={fmtCo2(route.total_co2)}      highlight={type === 'greenest'} accent={accent} />
      </div>

      {/* Segments */}
      <div style={{ padding: '.75rem 1.1rem', borderTop: '1px solid #f1f5f9' }}>
        {route.segments.map((seg, i) => (
          <div key={i} style={segRow}>
            <div style={{ ...modeIcon, background: seg.mode === 'train' ? '#dbeafe' : seg.mode === 'bus' ? '#fef9c3' : '#fce7f3', color: seg.mode === 'train' ? '#1d4ed8' : seg.mode === 'bus' ? '#a16207' : '#be185d' }}>
              {MODE_ICON[seg.mode]}
            </div>
            <div style={{ flex: 1 }}>
              <div style={{ fontWeight: 600, fontSize: '.85rem', color: '#334155' }}>
                {seg.from_name} → {seg.to_name}
              </div>
              <div style={{ fontSize: '.75rem', color: '#94a3b8' }}>{seg.operator}</div>
            </div>
            <div style={{ textAlign: 'right', fontSize: '.75rem', color: '#64748b' }}>
              {fmtDur(seg.duration)}<br />{fmtPrice(seg.price)}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

function Stat({ label, value, highlight, accent }) {
  return (
    <div style={{ flex: 1, padding: '.65rem .4rem', textAlign: 'center', borderRight: '1px solid #f1f5f9' }}>
      <div style={{ fontSize: '1rem', fontWeight: 700, color: highlight ? accent : '#1e293b' }}>{value}</div>
      <div style={{ fontSize: '.65rem', textTransform: 'uppercase', letterSpacing: '.05em', color: '#94a3b8' }}>{label}</div>
    </div>
  )
}

const cardBase = {
  background: 'white', borderRadius: '14px', overflow: 'hidden',
  cursor: 'pointer', transition: 'box-shadow .2s, border .15s',
}
const cardHeader = {
  padding: '.85rem 1.1rem', display: 'flex', alignItems: 'center', gap: '.6rem',
}
const badge = {
  width: 36, height: 36, borderRadius: '9px', display: 'flex',
  alignItems: 'center', justifyContent: 'center', fontSize: '1.1rem', color: 'white',
}
const statsRow = {
  display: 'flex', borderTop: '1px solid #f1f5f9',
}
const segRow = {
  display: 'flex', alignItems: 'center', gap: '.5rem',
  padding: '.3rem 0', borderBottom: '1px dashed #f1f5f9',
}
const modeIcon = {
  width: 26, height: 26, borderRadius: '6px', display: 'flex',
  alignItems: 'center', justifyContent: 'center', fontSize: '.85rem', flexShrink: 0,
}
