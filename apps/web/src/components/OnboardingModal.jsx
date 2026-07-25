import { useState } from 'react'
import { saveOnboarding } from '../api'
import CityAutocomplete from './CityAutocomplete'

const STYLES = [
  { value: 'fast',     label: '⚡ Speed first',    desc: 'Minimize travel time, regardless of cost' },
  { value: 'cheap',    label: '💰 Budget travel',  desc: 'Find the lowest-cost option' },
  { value: 'green',    label: '🌿 Low carbon',     desc: 'Minimize CO₂ footprint' },
  { value: 'balanced', label: '⚖️ Balanced',       desc: 'Smart trade-off across all factors' },
]

const SENSITIVITY = [
  { value: 'low',    label: 'Low — cost matters most' },
  { value: 'medium', label: 'Medium — I care but flexibility matters' },
  { value: 'high',   label: 'High — I offset or avoid flying' },
]

const BASE = import.meta.env.VITE_API_URL || '/api'

async function snapToNearestSlug(lat, lon) {
  try {
    const res = await fetch(`${BASE}/snap?lat=${lat}&lon=${lon}`)
    const data = await res.json()
    return data.slug || null
  } catch {
    return null
  }
}

export default function OnboardingModal({ onClose, onComplete }) {
  const [step, setStep] = useState(0)
  const [homeCity, setHomeCity] = useState(null) // { name, country, lat, lon }
  const [form, setForm] = useState({
    email: '',
    home_city: '',
    travel_style: 'balanced',
    carbon_sensitivity: 'medium',
  })
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState(null)

  const set = (k, v) => setForm(f => ({ ...f, [k]: v }))

  async function finish() {
    setSaving(true)
    setError(null)
    try {
      let slug = form.home_city
      if (homeCity && !slug) {
        slug = await snapToNearestSlug(homeCity.lat, homeCity.lon)
      }
      const payload = { ...form, home_city: slug || 'paris' }
      await saveOnboarding(payload)
      localStorage.setItem('routeiq_prefs', JSON.stringify({ ...payload, home_city_display: homeCity?.name }))
      onComplete(payload)
    } catch (e) {
      setError(e.message)
    } finally {
      setSaving(false)
    }
  }

  const canProceedStep0 = form.email && homeCity

  return (
    <div style={overlay}>
      <div style={modal}>
        <button onClick={onClose} style={closeBtn} aria-label="Close">✕</button>

        <div style={{ marginBottom: '1.5rem' }}>
          <div style={stepDots}>
            {[0, 1, 2].map(i => (
              <div key={i} style={{ ...dot, background: i === step ? '#2563eb' : '#e2e8f0' }} />
            ))}
          </div>
          <h2 style={{ fontSize: '1.3rem', fontWeight: 700, marginBottom: '.25rem' }}>
            {step === 0 ? 'Welcome to RouteIQ' : step === 1 ? 'Your travel style' : 'Carbon sensitivity'}
          </h2>
          <p style={{ color: '#64748b', fontSize: '.9rem' }}>
            {step === 0
              ? 'Set up your preferences for smarter route recommendations.'
              : step === 1
              ? 'How do you prioritise when choosing a route?'
              : 'How important is reducing your carbon footprint?'}
          </p>
        </div>

        {step === 0 && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div>
              <label style={labelStyle}>Email address</label>
              <input
                type="email"
                value={form.email}
                onChange={e => set('email', e.target.value)}
                placeholder="you@example.com"
                style={inputStyle}
              />
            </div>
            <div>
              <label style={labelStyle}>Home city</label>
              <CityAutocomplete
                value={homeCity}
                onChange={setHomeCity}
                placeholder="Type your home city…"
              />
            </div>
            <button
              style={{ ...primaryBtn, opacity: canProceedStep0 ? 1 : 0.5, cursor: canProceedStep0 ? 'pointer' : 'not-allowed' }}
              disabled={!canProceedStep0}
              onClick={() => setStep(1)}
            >
              Next →
            </button>
          </div>
        )}

        {step === 1 && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '.75rem' }}>
            {STYLES.map(s => (
              <div
                key={s.value}
                onClick={() => set('travel_style', s.value)}
                style={{
                  ...optionCard,
                  border: form.travel_style === s.value ? '2px solid #2563eb' : '1.5px solid #e2e8f0',
                  background: form.travel_style === s.value ? '#eff6ff' : 'white',
                }}
              >
                <div style={{ fontWeight: 600 }}>{s.label}</div>
                <div style={{ fontSize: '.8rem', color: '#64748b' }}>{s.desc}</div>
              </div>
            ))}
            <div style={{ display: 'flex', gap: '.75rem', marginTop: '.5rem' }}>
              <button style={secondaryBtn} onClick={() => setStep(0)}>← Back</button>
              <button style={primaryBtn} onClick={() => setStep(2)}>Next →</button>
            </div>
          </div>
        )}

        {step === 2 && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '.75rem' }}>
            {SENSITIVITY.map(s => (
              <div
                key={s.value}
                onClick={() => set('carbon_sensitivity', s.value)}
                style={{
                  ...optionCard,
                  border: form.carbon_sensitivity === s.value ? '2px solid #059669' : '1.5px solid #e2e8f0',
                  background: form.carbon_sensitivity === s.value ? '#ecfdf5' : 'white',
                }}
              >
                <div style={{ fontWeight: 600 }}>{s.label}</div>
              </div>
            ))}
            {error && <p style={{ color: '#ef4444', fontSize: '.85rem' }}>{error}</p>}
            <div style={{ display: 'flex', gap: '.75rem', marginTop: '.5rem' }}>
              <button style={secondaryBtn} onClick={() => setStep(1)}>← Back</button>
              <button style={{ ...primaryBtn, opacity: saving ? 0.6 : 1, cursor: saving ? 'not-allowed' : 'pointer' }} disabled={saving} onClick={finish}>
                {saving ? 'Saving…' : 'Get started ✓'}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

const overlay = {
  position: 'fixed', inset: 0, background: 'rgba(15,23,42,.55)',
  display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000,
}
const modal = {
  background: 'white', borderRadius: '16px', padding: '2rem',
  width: '100%', maxWidth: '440px', position: 'relative', boxShadow: '0 24px 64px rgba(0,0,0,.2)',
}
const closeBtn = {
  position: 'absolute', top: '1rem', right: '1rem', background: 'none',
  border: 'none', fontSize: '1.1rem', color: '#94a3b8', padding: '.25rem', cursor: 'pointer',
}
const stepDots = { display: 'flex', gap: '.5rem', marginBottom: '1rem' }
const dot = { width: 8, height: 8, borderRadius: '50%', transition: 'background .2s' }
const labelStyle = { display: 'block', fontSize: '.75rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '.05em', color: '#64748b', marginBottom: '.4rem' }
const inputStyle = { width: '100%', padding: '.65rem .9rem', border: '1.5px solid #e2e8f0', borderRadius: '8px', fontSize: '.95rem', color: '#1e293b', background: 'white', outline: 'none', fontFamily: 'inherit', boxSizing: 'border-box' }
const primaryBtn = { flex: 1, padding: '.7rem 1.5rem', background: 'linear-gradient(135deg,#2563eb,#0ea5e9)', color: 'white', border: 'none', borderRadius: '8px', fontWeight: 600, fontSize: '.95rem' }
const secondaryBtn = { padding: '.7rem 1.2rem', background: '#f1f5f9', color: '#475569', border: 'none', borderRadius: '8px', fontWeight: 600, fontSize: '.95rem', cursor: 'pointer' }
const optionCard = { padding: '.85rem 1rem', borderRadius: '10px', cursor: 'pointer', transition: 'border .15s, background .15s' }
