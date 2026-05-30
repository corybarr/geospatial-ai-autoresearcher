import {
  Cartesian3,
  Cesium3DTileset,
  createOsmBuildingsAsync,
  Ion,
  Math as CesiumMath,
  Terrain,
  Viewer,
} from 'cesium'
import 'cesium/Build/Cesium/Widgets/widgets.css'
import { useEffect, useRef, useState } from 'react'
import './ion-assets-panel.css'

function CesiumViewer() {
  const containerRef = useRef<HTMLDivElement | null>(null)
  const buildingsRef = useRef<Cesium3DTileset | null>(null)
  const [osmBuildingsVisible, setOsmBuildingsVisible] = useState(true)
  const osmVisibleRef = useRef(osmBuildingsVisible)

  useEffect(() => {
    osmVisibleRef.current = osmBuildingsVisible
    if (buildingsRef.current) {
      buildingsRef.current.show = osmBuildingsVisible
    }
  }, [osmBuildingsVisible])

  useEffect(() => {
    const container = containerRef.current
    const token = import.meta.env.VITE_CESIUM_ION_ACCESS_TOKEN?.trim()

    if (!container) {
      return
    }

    if (!token || token === 'PASTE_YOUR_TOKEN_HERE') {
      throw new Error(
        'Missing VITE_CESIUM_ION_ACCESS_TOKEN. Copy .env.example to .env.local and replace PASTE_YOUR_TOKEN_HERE before running the app.',
      )
    }

    Ion.defaultAccessToken = token

    const viewer = new Viewer(container, {
      terrain: Terrain.fromWorldTerrain(),
    })

    let disposed = false

    void (async () => {
      viewer.camera.flyTo({
        destination: Cartesian3.fromDegrees(-122.4175, 37.655, 400),
        orientation: {
          heading: CesiumMath.toRadians(0.0),
          pitch: CesiumMath.toRadians(-15.0),
        },
      })

      const buildings = await createOsmBuildingsAsync()
      if (!disposed) {
        buildings.show = osmVisibleRef.current
        viewer.scene.primitives.add(buildings)
        buildingsRef.current = buildings
      }
    })()

    return () => {
      disposed = true
      buildingsRef.current = null
      viewer.destroy()
    }
  }, [])

  return (
    <div style={{ position: 'fixed', inset: 0 }}>
      <div ref={containerRef} style={{ position: 'absolute', inset: 0 }} />
      <div className="ion-assets-panel">
        <div className="ion-assets-panel__header">Ion Assets</div>
        <ul className="ion-assets-panel__list">
          <li className="ion-assets-panel__item">
            <span className="ion-assets-panel__label">OSM Buildings</span>
            <label className="ion-assets-panel__toggle">
              <input
                type="checkbox"
                checked={osmBuildingsVisible}
                onChange={(e) => setOsmBuildingsVisible(e.target.checked)}
              />
              <span className="ion-assets-panel__toggle-track" />
            </label>
          </li>
        </ul>
      </div>
    </div>
  )
}

export default CesiumViewer
