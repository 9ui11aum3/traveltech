import { useEffect, useRef } from 'react'

const COLORS = { fastest: '#2563eb', cheapest: '#16a34a', greenest: '#059669' }

export default function RouteMap({ result, selected }) {
  const mapRef = useRef(null)
  const mapInstanceRef = useRef(null)
  const layersRef = useRef({})

  useEffect(() => {
    if (!window.L) return
    const L = window.L

    if (mapInstanceRef.current) {
      mapInstanceRef.current.remove()
      mapInstanceRef.current = null
    }

    const map = L.map(mapRef.current)
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors', maxZoom: 10,
    }).addTo(map)
    mapInstanceRef.current = map

    const allLatLngs = []
    layersRef.current = {}

    Object.entries(result.routes).forEach(([type, route]) => {
      if (!route) return
      const color = COLORS[type]
      const latlngs = []
      route.segments.forEach(seg => {
        if (seg.from_lat != null) latlngs.push([seg.from_lat, seg.from_lon])
        if (seg.to_lat != null) latlngs.push([seg.to_lat, seg.to_lon])
        if (seg.from_lat != null) allLatLngs.push([seg.from_lat, seg.from_lon])
        if (seg.to_lat != null) allLatLngs.push([seg.to_lat, seg.to_lon])
      })

      const layer = L.layerGroup()
      L.polyline(latlngs, { color, weight: 4, opacity: 0.7 }).addTo(layer)

      route.segments.forEach((seg, i) => {
        if (i === 0 && seg.from_lat != null) {
          L.circleMarker([seg.from_lat, seg.from_lon], { radius: 8, color: 'white', fillColor: color, fillOpacity: 1, weight: 2 })
            .addTo(layer).bindPopup(seg.from_name)
        }
        if (seg.to_lat != null) {
          L.circleMarker([seg.to_lat, seg.to_lon], {
            radius: i === route.segments.length - 1 ? 9 : 6,
            color: 'white', fillColor: color, fillOpacity: 0.9, weight: 2,
          }).addTo(layer).bindPopup(seg.to_name)
        }
      })

      layersRef.current[type] = layer
    })

    if (allLatLngs.length) map.fitBounds(allLatLngs, { padding: [30, 30] })

    if (layersRef.current[selected]) {
      layersRef.current[selected].addTo(map)
    }

    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove()
        mapInstanceRef.current = null
      }
    }
  }, [result])

  useEffect(() => {
    const map = mapInstanceRef.current
    if (!map || !window.L) return
    Object.entries(layersRef.current).forEach(([type, layer]) => {
      if (type === selected) {
        layer.addTo(map)
      } else {
        layer.remove()
      }
    })
  }, [selected])

  return (
    <div style={container}>
      <div style={header}>🗺️ Route map — click a route card to highlight it</div>
      <div ref={mapRef} style={{ height: 360 }} />
    </div>
  )
}

const container = {
  background: 'white', borderRadius: '14px', border: '1.5px solid #e2e8f0',
  overflow: 'hidden', marginBottom: '1.5rem',
}
const header = {
  padding: '.9rem 1.2rem', fontWeight: 600, fontSize: '.9rem',
  borderBottom: '1px solid #f1f5f9', color: '#475569',
}
