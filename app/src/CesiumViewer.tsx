import {
  Cartesian3,
  Cesium3DTileset,
  createOsmBuildingsAsync,
  ImageryLayer,
  Ion,
  IonImageryProvider,
  Math as CesiumMath,
  Terrain,
  Viewer,
} from 'cesium'
import 'cesium/Build/Cesium/Widgets/widgets.css'
import { useEffect, useRef, useState } from 'react'
import './ion-assets-panel.css'

interface Visibility {
  osmBuildings: boolean
  bingAerial: boolean
  bingAerialLabels: boolean
  bingRoad: boolean
  earthAtNight: boolean
  sentinel2: boolean
}

type ImageryKey = Exclude<keyof Visibility, 'osmBuildings'>

const IMAGERY_ASSETS: { key: ImageryKey; id: number; label: string }[] = [
  { key: 'bingAerial', id: 2, label: 'Bing Maps Aerial' },
  { key: 'bingAerialLabels', id: 3, label: 'Bing Maps Aerial with Labels' },
  { key: 'bingRoad', id: 4, label: 'Bing Maps Road' },
  { key: 'earthAtNight', id: 3812, label: 'Earth at Night' },
  { key: 'sentinel2', id: 3954, label: 'Sentinel-2' },
]

const DEFAULT_VISIBILITY: Visibility = {
  osmBuildings: false,
  bingAerial: true,
  bingAerialLabels: false,
  bingRoad: false,
  earthAtNight: false,
  sentinel2: false,
}

function CesiumViewer() {
  const containerRef = useRef<HTMLDivElement | null>(null)
  const buildingsRef = useRef<Cesium3DTileset | null>(null)
  const imageryLayersRef = useRef<Partial<Record<ImageryKey, ImageryLayer>>>({})
  const [visibility, setVisibility] = useState<Visibility>(DEFAULT_VISIBILITY)
  const visibilityRef = useRef(visibility)

  useEffect(() => {
    visibilityRef.current = visibility
    if (buildingsRef.current) {
      buildingsRef.current.show = visibility.osmBuildings
    }
    for (const { key } of IMAGERY_ASSETS) {
      const layer = imageryLayersRef.current[key]
      if (layer) layer.show = visibility[key]
    }
  }, [visibility])

  useEffect(() => {
    const container = containerRef.current
    const token = import.meta.env.VITE_CESIUM_ION_ACCESS_TOKEN?.trim()

    if (!container) return

    if (!token || token === 'PASTE_YOUR_TOKEN_HERE') {
      throw new Error(
        'Missing VITE_CESIUM_ION_ACCESS_TOKEN. Copy .env.example to .env.local and replace PASTE_YOUR_TOKEN_HERE before running the app.',
      )
    }

    Ion.defaultAccessToken = token

    const viewer = new Viewer(container, {
      terrain: Terrain.fromWorldTerrain(),
    })
    viewer.imageryLayers.removeAll()

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
        buildings.show = visibilityRef.current.osmBuildings
        viewer.scene.primitives.add(buildings)
        buildingsRef.current = buildings
      }

      await Promise.all(
        IMAGERY_ASSETS.map(async ({ key, id }) => {
          const provider = await IonImageryProvider.fromAssetId(id)
          if (!disposed) {
            const layer = viewer.imageryLayers.addImageryProvider(provider)
            layer.show = visibilityRef.current[key]
            imageryLayersRef.current[key] = layer
          }
        }),
      )
    })()

    return () => {
      disposed = true
      buildingsRef.current = null
      imageryLayersRef.current = {}
      viewer.destroy()
    }
  }, [])

  const toggle = (key: keyof Visibility) =>
    setVisibility((prev) => ({ ...prev, [key]: !prev[key] }))

  return (
    <div style={{ position: 'fixed', inset: 0 }}>
      <div ref={containerRef} style={{ position: 'absolute', inset: 0 }} />
      <div className="ion-assets-panel">
        <div className="ion-assets-panel__header">Ion Assets</div>
        <ul className="ion-assets-panel__list">
          <li className="ion-assets-panel__section">3D Tiles</li>
          <li className="ion-assets-panel__item">
            <span className="ion-assets-panel__label">OSM Buildings</span>
            <label className="ion-assets-panel__toggle">
              <input
                type="checkbox"
                checked={visibility.osmBuildings}
                onChange={() => toggle('osmBuildings')}
              />
              <span className="ion-assets-panel__toggle-track" />
            </label>
          </li>
          <li className="ion-assets-panel__section">Imagery</li>
          {IMAGERY_ASSETS.map(({ key, label }) => (
            <li key={key} className="ion-assets-panel__item">
              <span className="ion-assets-panel__label">{label}</span>
              <label className="ion-assets-panel__toggle">
                <input
                  type="checkbox"
                  checked={visibility[key]}
                  onChange={() => toggle(key)}
                />
                <span className="ion-assets-panel__toggle-track" />
              </label>
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}

export default CesiumViewer
