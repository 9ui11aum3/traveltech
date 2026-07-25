import { useState, useRef, useEffect } from 'react'

const BASE = import.meta.env.VITE_API_URL || '/api'

const inputStyle = {
  padding: '.6rem .9rem',
  border: '1.5px solid #e2e8f0',
  borderRadius: '8px',
  fontSize: '.95rem',
  color: '#1e293b',
  background: 'white',
  transition: 'border-color .2s',
  fontFamily: 'inherit',
  width: '100%',
  boxSizing: 'border-box',
}

const dropdownStyle = {
  position: 'absolute',
  top: 'calc(100% + 4px)',
  left: 0,
  right: 0,
  background: 'white',
  border: '1.5px solid #e2e8f0',
  borderRadius: '8px',
  boxShadow: '0 8px 24px rgba(0,0,0,.12)',
  zIndex: 9999,
  listStyle: 'none',
  margin: 0,
  padding: '4px 0',
  maxHeight: '240px',
  overflowY: 'auto',
}

export default function CityAutocomplete({ value, onChange, placeholder = 'Type a city…' }) {
  const [query, setQuery] = useState(value ? `${value.name}${value.country ? `, ${value.country}` : ''}` : '')
  const [suggestions, setSuggestions] = useState([])
  const [open, setOpen] = useState(false)
  const [loading, setLoading] = useState(false)
  const debounceRef = useRef(null)
  const wrapRef = useRef(null)

  // Sync display when value is set externally (e.g. onboarding)
  useEffect(() => {
    if (value) {
      setQuery(`${value.name}${value.country ? `, ${value.country}` : ''}`)
    }
  }, [value?.name])

  useEffect(() => {
    function handleClick(e) {
      if (wrapRef.current && !wrapRef.current.contains(e.target)) {
        setOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClick)
    return () => document.removeEventListener('mousedown', handleClick)
  }, [])

  function handleChange(e) {
    const q = e.target.value
    setQuery(q)
    onChange(null) // clear selected value while typing

    if (q.length < 2) {
      setSuggestions([])
      setOpen(false)
      return
    }

    clearTimeout(debounceRef.current)
    setLoading(true)
    debounceRef.current = setTimeout(async () => {
      try {
        const res = await fetch(`${BASE}/geocode?q=${encodeURIComponent(q)}`)
        if (res.ok) {
          const data = await res.json()
          setSuggestions(data)
          setOpen(data.length > 0)
        }
      } catch {
        // ignore network errors silently
      } finally {
        setLoading(false)
      }
    }, 280)
  }

  function select(city) {
    setQuery(`${city.name}${city.country ? `, ${city.country}` : ''}`)
    onChange(city)
    setOpen(false)
    setSuggestions([])
  }

  return (
    <div ref={wrapRef} style={{ position: 'relative' }}>
      <input
        type="text"
        value={query}
        onChange={handleChange}
        placeholder={placeholder}
        style={{
          ...inputStyle,
          borderColor: open ? '#3b82f6' : '#e2e8f0',
        }}
        autoComplete="off"
        spellCheck={false}
      />
      {loading && (
        <span style={{
          position: 'absolute', right: '10px', top: '50%', transform: 'translateY(-50%)',
          fontSize: '.75rem', color: '#94a3b8',
        }}>…</span>
      )}
      {open && suggestions.length > 0 && (
        <ul style={dropdownStyle}>
          {suggestions.map((c, i) => (
            <li
              key={i}
              onMouseDown={() => select(c)}
              style={{
                padding: '.5rem .9rem',
                cursor: 'pointer',
                fontSize: '.9rem',
                color: '#1e293b',
                borderBottom: i < suggestions.length - 1 ? '1px solid #f1f5f9' : 'none',
              }}
              onMouseEnter={e => { e.currentTarget.style.background = '#f8fafc' }}
              onMouseLeave={e => { e.currentTarget.style.background = 'white' }}
            >
              <span style={{ fontWeight: 600 }}>{c.name}</span>
              {c.state && <span style={{ color: '#64748b', fontSize: '.82rem' }}> · {c.state}</span>}
              {c.country && <span style={{ color: '#94a3b8', fontSize: '.82rem' }}> · {c.country}</span>}
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
