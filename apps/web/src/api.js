const BASE = import.meta.env.VITE_API_URL || '/api'

export async function getCities() {
  const res = await fetch(`${BASE}/cities`)
  if (!res.ok) throw new Error('Failed to load cities')
  return res.json()
}

export async function searchRoutes(from, to) {
  const res = await fetch(`${BASE}/routes?from=${encodeURIComponent(from)}&to=${encodeURIComponent(to)}`)
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || 'Route search failed')
  }
  return res.json()
}

export async function saveOnboarding(prefs) {
  const res = await fetch(`${BASE}/onboarding`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(prefs),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || 'Failed to save preferences')
  }
  return res.json()
}
