function fmtCo2(kg) { return kg < 1 ? `${Math.round(kg * 1000)}g` : `${kg.toFixed(1)}kg` }

function haversine(lat1, lon1, lat2, lon2) {
  const R = 6371
  const dLat = (lat2 - lat1) * Math.PI / 180
  const dLon = (lon2 - lon1) * Math.PI / 180
  const a = Math.sin(dLat / 2) ** 2 + Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * Math.sin(dLon / 2) ** 2
  return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
}

export default function Co2Chart({ result }) {
  const { routes } = result
  const originCity = result.origin_city
  const destCity   = result.destination_city

  const distKm = (originCity && destCity)
    ? haversine(originCity.lat, originCity.lon, destCity.lat, destCity.lon)
    : 0

  const carCo2   = distKm * 0.12
  const planeCo2 = distKm * 0.255

  const bars = []
  if (routes.fastest)  bars.push({ label: '⚡ Fastest',  co2: routes.fastest.total_co2,  color: '#2563eb' })
  const cheapCo2 = routes.cheapest?.total_co2
  if (routes.cheapest && cheapCo2 !== routes.fastest?.total_co2)
    bars.push({ label: '💰 Cheapest', co2: cheapCo2, color: '#16a34a' })
  const greenCo2 = routes.greenest?.total_co2
  if (routes.greenest && greenCo2 !== routes.fastest?.total_co2 && greenCo2 !== cheapCo2)
    bars.push({ label: '🌿 Greenest', co2: greenCo2, color: '#059669' })
  if (distKm > 0) {
    bars.push({ label: '🚗 Car (est.)',    co2: carCo2,   color: '#f59e0b' })
    bars.push({ label: '✈️ Flight (est.)', co2: planeCo2, color: '#ef4444' })
  }

  const maxCo2 = Math.max(...bars.map(b => b.co2))

  return (
    <div style={container}>
      <h3 style={title}>🌍 Carbon Footprint Comparison</h3>
      {bars.map(b => (
        <div key={b.label} style={row}>
          <div style={barLabel}>{b.label}</div>
          <div style={track}>
            <div style={{
              ...fill,
              width: `${Math.max(2, (b.co2 / maxCo2) * 100)}%`,
              background: b.color,
            }} />
          </div>
          <div style={value}>{fmtCo2(b.co2)}</div>
        </div>
      ))}
    </div>
  )
}

const container = {
  background: 'white', borderRadius: '14px', border: '1.5px solid #e2e8f0',
  padding: '1.2rem 1.5rem', marginBottom: '1.5rem',
}
const title = {
  fontSize: '.85rem', fontWeight: 700, textTransform: 'uppercase',
  letterSpacing: '.05em', color: '#64748b', marginBottom: '1rem',
}
const row = { display: 'flex', alignItems: 'center', gap: '.75rem', marginBottom: '.5rem' }
const barLabel = { fontSize: '.8rem', width: 150, flexShrink: 0, color: '#475569', fontWeight: 500 }
const track = { flex: 1, height: 12, background: '#f1f5f9', borderRadius: 99, overflow: 'hidden' }
const fill = { height: '100%', borderRadius: 99, transition: 'width 1s ease' }
const value = { fontSize: '.8rem', fontWeight: 600, width: 55, textAlign: 'right', color: '#334155' }
