import { useState, useEffect } from 'react'
import { searchRoutes } from './api'
import RouteCard from './components/RouteCard'
import Co2Chart from './components/Co2Chart'
import RouteMap from './components/RouteMap'
import OnboardingModal from './components/OnboardingModal'
import CityAutocomplete from './components/CityAutocomplete'

export default function App() {
  const [from, setFrom] = useState(null)   // { name, country, lat, lon }
  const [to, setTo] = useState(null)
  const [date, setDate] = useState(() => {
    const d = new Date(); d.setDate(d.getDate() + 1)
    return d.toISOString().split('T')[0]
  })
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [selected, setSelected] = useState('fastest')
  const [showOnboarding, setShowOnboarding] = useState(false)
  const [prefs, setPrefs] = useState(null)

  useEffect(() => {
    const saved = localStorage.getItem('routeiq_prefs')
    if (saved) {
      try { setPrefs(JSON.parse(saved)) } catch {}
    } else {
      setShowOnboarding(true)
    }
  }, [])

  async function search(e) {
    e?.preventDefault()
    if (!from || !to) return
    setLoading(true)
    setError(null)
    try {
      const data = await searchRoutes(from, to)
      setResult({ ...data, origin_city: from, destination_city: to })
      setSelected('fastest')
    } catch (err) {
      setError(err.message)
      setResult(null)
    } finally {
      setLoading(false)
    }
  }

  function handleOnboardingComplete(p) {
    setPrefs(p)
    setShowOnboarding(false)
  }

  const canSearch = from && to && !loading

  return (
    <>
      {showOnboarding && (
        <OnboardingModal
          onClose={() => setShowOnboarding(false)}
          onComplete={handleOnboardingComplete}
        />
      )}

      <header style={headerStyle}>
        <div style={logo}>
          <div style={logoIcon}>🗺️</div>
          <div>
            <div style={{ fontSize: '1.6rem', fontWeight: 800, letterSpacing: '-.5px', color: 'white' }}>RouteIQ</div>
            <div style={{ fontSize: '.8rem', opacity: .75, color: 'white' }}>Multimodal Intelligence</div>
          </div>
        </div>
        <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: '1rem' }}>
          {prefs && (
            <span style={{ color: 'rgba(255,255,255,.75)', fontSize: '.85rem' }}>
              👤 {prefs.email}
            </span>
          )}
          <button onClick={() => setShowOnboarding(true)} style={prefBtn}>
            ⚙️ Preferences
          </button>
        </div>
      </header>

      {/* Search bar */}
      <div style={searchPanel}>
        <form style={searchForm} onSubmit={search}>
          <div style={field}>
            <label style={fieldLabel}>From</label>
            <CityAutocomplete
              value={from}
              onChange={setFrom}
              placeholder="Type any city…"
            />
          </div>
          <div style={field}>
            <label style={fieldLabel}>To</label>
            <CityAutocomplete
              value={to}
              onChange={setTo}
              placeholder="Type any city…"
            />
          </div>
          <div style={{ ...field, minWidth: 130, maxWidth: 160 }}>
            <label style={fieldLabel}>Date</label>
            <input type="date" value={date} onChange={e => setDate(e.target.value)} style={inputStyle} />
          </div>
          <button type="submit" style={{ ...searchBtn, opacity: canSearch ? 1 : 0.6, cursor: canSearch ? 'pointer' : 'not-allowed' }} disabled={!canSearch}>
            {loading ? '…' : '🔍 Find Routes'}
          </button>
        </form>
      </div>

      <div style={container}>
        {error && (
          <div style={errorBox}>⚠️ {error}</div>
        )}

        {!result && !error && (
          <div style={emptyState}>
            <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>🚄</div>
            <p>Type any European city above to compare multimodal routes</p>
            <p style={{ fontSize: '.8rem', color: '#cbd5e1', marginTop: '.5rem' }}>Lyon → Honfleur, Paris → Berlin, and more</p>
          </div>
        )}

        {result && (
          <>
            <div style={{ fontSize: '.8rem', color: '#64748b', marginBottom: '.75rem', fontWeight: 500 }}>
              {result.origin_name} → {result.destination_name}
              {date && ` · ${new Date(date).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' })}`}
              {' · 3 route options compared'}
            </div>

            {result.last_mile_origin && (
              <div style={lastMileBox}>
                📍 <strong>Departure:</strong> {result.last_mile_origin.note}
              </div>
            )}
            {result.last_mile_destination && (
              <div style={lastMileBox}>
                📍 <strong>Arrival:</strong> {result.last_mile_destination.note}
              </div>
            )}

            <div style={resultsGrid}>
              {['fastest', 'cheapest', 'greenest'].map(type => (
                <RouteCard
                  key={type}
                  type={type}
                  route={result.routes[type]}
                  selected={selected === type}
                  onSelect={() => setSelected(type)}
                />
              ))}
            </div>

            <Co2Chart result={result} />

            <RouteMap result={result} selected={selected} cities={[]} />
          </>
        )}
      </div>

      <footer style={footerStyle}>
        RouteIQ Prototype · Open data · For investor demonstration only
      </footer>
    </>
  )
}

const headerStyle = {
  background: 'linear-gradient(135deg,#0f172a 0%,#1e3a8a 60%,#0ea5e9 100%)',
  padding: '1.5rem 2rem', display: 'flex', alignItems: 'center', gap: '1rem',
}
const logo = { display: 'flex', alignItems: 'center', gap: '.75rem' }
const logoIcon = {
  width: 44, height: 44, background: 'rgba(255,255,255,.15)', borderRadius: '12px',
  display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.5rem',
  border: '1px solid rgba(255,255,255,.2)',
}
const prefBtn = {
  padding: '.5rem 1rem', background: 'rgba(255,255,255,.15)', color: 'white',
  border: '1px solid rgba(255,255,255,.25)', borderRadius: '8px', fontSize: '.85rem', fontWeight: 600,
  cursor: 'pointer',
}
const searchPanel = {
  background: 'white', padding: '1.5rem 2rem',
  borderBottom: '1px solid #e2e8f0', boxShadow: '0 2px 4px rgba(0,0,0,.05)',
}
const searchForm = {
  display: 'flex', gap: '.75rem', flexWrap: 'wrap',
  alignItems: 'flex-end', maxWidth: 900, margin: '0 auto',
}
const field = { display: 'flex', flexDirection: 'column', gap: '.4rem', flex: 1, minWidth: 180 }
const fieldLabel = { fontSize: '.75rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '.05em', color: '#64748b' }
const inputStyle = {
  padding: '.6rem .9rem', border: '1.5px solid #e2e8f0', borderRadius: '8px',
  fontSize: '.95rem', color: '#1e293b', background: 'white', outline: 'none', fontFamily: 'inherit',
}
const searchBtn = {
  padding: '.65rem 1.8rem', background: 'linear-gradient(135deg,#2563eb,#0ea5e9)',
  color: 'white', border: 'none', borderRadius: '8px', fontSize: '.95rem',
  fontWeight: 600, whiteSpace: 'nowrap', minWidth: 130,
}
const container = { maxWidth: 1100, margin: '0 auto', padding: '1.5rem 1rem' }
const resultsGrid = { display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(280px,1fr))', gap: '1rem', marginBottom: '1.5rem' }
const emptyState = { textAlign: 'center', padding: '4rem 2rem', color: '#94a3b8', fontSize: '.95rem' }
const errorBox = { background: '#fef2f2', border: '1px solid #fca5a5', borderRadius: '10px', padding: '1rem 1.25rem', color: '#b91c1c', marginBottom: '1rem' }
const lastMileBox = { background: '#fffbeb', border: '1px solid #fde68a', borderRadius: '8px', padding: '.6rem 1rem', fontSize: '.82rem', color: '#92400e', marginBottom: '.5rem' }
const footerStyle = { textAlign: 'center', padding: '1.5rem', fontSize: '.75rem', color: '#94a3b8', borderTop: '1px solid #e2e8f0', background: 'white', marginTop: '1rem' }
