const BASE = import.meta.env.VITE_API_URL || '/api'

export async function getCities() {
  const res = await fetch(`${BASE}/cities`)
  if (!res.ok) throw new Error('Failed to load cities')
  return res.json()
}

export async function searchRoutes(from, to) {
  // from / to are city objects: { name, country, lat, lon }
  // or legacy slugs (strings) for backward compat
  let params
  if (typeof from === 'object' && from !== null) {
    params = new URLSearchParams({
      from_lat: from.lat,
      from_lon: from.lon,
      from_name: from.name,
      to_lat: to.lat,
      to_lon: to.lon,
      to_name: to.name,
    })
  } else {
    params = new URLSearchParams({ from, to })
  }

  const res = await fetch(`${BASE}/routes?${params}`)
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
