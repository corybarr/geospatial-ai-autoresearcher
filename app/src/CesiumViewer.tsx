import {
  Cartesian3,
  Cesium3DTileset,
  Color,
  createElevationBandMaterial,
  createOsmBuildingsAsync,
  ImageryLayer,
  Ion,
  IonImageryProvider,
  Math as CesiumMath,
  Scene,
  Terrain,
  Viewer,
} from 'cesium'
import 'cesium/Build/Cesium/Widgets/widgets.css'
import { useEffect, useRef, useState } from 'react'
import './ion-assets-panel.css'

interface Visibility {
  googlePhotorealistic: boolean
  osmBuildings: boolean
  bingAerial: boolean
  bingAerialLabels: boolean
  bingRoad: boolean
  earthAtNight: boolean
  sentinel2: boolean
  elevationBand: boolean
}

interface BandConfig {
  gradient: boolean
  band1Position: number
  band2Position: number
  band3Position: number
  bandThickness: number
  bandTransparency: number
  backgroundTransparency: number
}

// SF Bay Area: sea level to ~1300m (Mt. Hamilton). Bands at low foothills, mid hills, peaks.
const DEFAULT_BAND_CONFIG: BandConfig = {
  gradient: false,
  band1Position: 45,
  band2Position: 103,
  band3Position: 112,
  bandThickness: 80,
  bandTransparency: 0.5,
  backgroundTransparency: 0.75,
}

function buildElevationBandMaterial(scene: Scene, cfg: BandConfig) {
  const { gradient, band1Position, band2Position, band3Position, bandThickness, bandTransparency, backgroundTransparency } = cfg

  const layers = []

  const backgroundLayer = {
    entries: [
      { height: -50.0, color: new Color(0.0, 0.0, 0.2, backgroundTransparency) },
      { height: 1300.0, color: new Color(1.0, 1.0, 1.0, backgroundTransparency) },
      { height: 1500.0, color: new Color(1.0, 0.0, 0.0, backgroundTransparency) },
    ],
    extendDownwards: true,
    extendUpwards: true,
  }
  layers.push(backgroundLayer)

  const gridStartHeight = 0.0
  const gridEndHeight = 1400.0
  const gridCount = 50
  for (let i = 0; i < gridCount; i++) {
    const lerper = i / (gridCount - 1)
    const heightBelow = CesiumMath.lerp(gridStartHeight, gridEndHeight, lerper)
    const heightAbove = heightBelow + 5.0
    const alpha = CesiumMath.lerp(0.2, 0.4, lerper) * backgroundTransparency
    layers.push({
      entries: [
        { height: heightBelow, color: new Color(1.0, 1.0, 1.0, alpha) },
        { height: heightAbove, color: new Color(1.0, 1.0, 1.0, alpha) },
      ],
    })
  }

  const antialias = Math.min(10.0, bandThickness * 0.1)

  if (!gradient) {
    layers.push({
      entries: [
        { height: band1Position - bandThickness * 0.5 - antialias, color: new Color(0.0, 0.0, 1.0, 0.0) },
        { height: band1Position - bandThickness * 0.5, color: new Color(0.0, 0.0, 1.0, bandTransparency) },
        { height: band1Position + bandThickness * 0.5, color: new Color(0.0, 0.0, 1.0, bandTransparency) },
        { height: band1Position + bandThickness * 0.5 + antialias, color: new Color(0.0, 0.0, 1.0, 0.0) },
      ],
    })
    layers.push({
      entries: [
        { height: band2Position - bandThickness * 0.5 - antialias, color: new Color(0.0, 1.0, 0.0, 0.0) },
        { height: band2Position - bandThickness * 0.5, color: new Color(0.0, 1.0, 0.0, bandTransparency) },
        { height: band2Position + bandThickness * 0.5, color: new Color(0.0, 1.0, 0.0, bandTransparency) },
        { height: band2Position + bandThickness * 0.5 + antialias, color: new Color(0.0, 1.0, 0.0, 0.0) },
      ],
    })
    layers.push({
      entries: [
        { height: band3Position - bandThickness * 0.5 - antialias, color: new Color(1.0, 0.0, 0.0, 0.0) },
        { height: band3Position - bandThickness * 0.5, color: new Color(1.0, 0.0, 0.0, bandTransparency) },
        { height: band3Position + bandThickness * 0.5, color: new Color(1.0, 0.0, 0.0, bandTransparency) },
        { height: band3Position + bandThickness * 0.5 + antialias, color: new Color(1.0, 0.0, 0.0, 0.0) },
      ],
    })
  } else {
    layers.push({
      entries: [
        { height: band1Position - bandThickness * 0.5, color: new Color(0.0, 0.0, 1.0, bandTransparency) },
        { height: band2Position, color: new Color(0.0, 1.0, 0.0, bandTransparency) },
        { height: band3Position + bandThickness * 0.5, color: new Color(1.0, 0.0, 0.0, bandTransparency) },
      ],
    })
  }

  return createElevationBandMaterial({ scene, layers })
}

type ImageryKey = Exclude<keyof Visibility, 'osmBuildings' | 'googlePhotorealistic' | 'elevationBand'>

const IMAGERY_ASSETS: { key: ImageryKey; id: number; label: string }[] = [
  { key: 'bingAerial', id: 2, label: 'Bing Maps Aerial' },
  { key: 'bingAerialLabels', id: 3, label: 'Bing Maps Aerial with Labels' },
  { key: 'bingRoad', id: 4, label: 'Bing Maps Road' },
  { key: 'earthAtNight', id: 3812, label: 'Earth at Night' },
  { key: 'sentinel2', id: 3954, label: 'Sentinel-2' },
]

const DEFAULT_VISIBILITY: Visibility = {
  googlePhotorealistic: false,
  osmBuildings: false,
  bingAerial: true,
  bingAerialLabels: false,
  bingRoad: false,
  earthAtNight: false,
  sentinel2: false,
  elevationBand: true,
}

function CesiumViewer() {
  const containerRef = useRef<HTMLDivElement | null>(null)
  const viewerRef = useRef<Viewer | null>(null)
  const photorealisticRef = useRef<Cesium3DTileset | null>(null)
  const buildingsRef = useRef<Cesium3DTileset | null>(null)
  const imageryLayersRef = useRef<Partial<Record<ImageryKey, ImageryLayer>>>({})
  const [visibility, setVisibility] = useState<Visibility>(DEFAULT_VISIBILITY)
  const visibilityRef = useRef(visibility)
  const [bandConfig] = useState<BandConfig>(DEFAULT_BAND_CONFIG)
  const bandConfigRef = useRef(bandConfig)

  useEffect(() => {
    visibilityRef.current = visibility
    bandConfigRef.current = bandConfig
    const viewer = viewerRef.current
    if (viewer) {
      viewer.scene.globe.show = !visibility.googlePhotorealistic
      viewer.scene.globe.material = visibility.elevationBand
        ? buildElevationBandMaterial(viewer.scene, bandConfig)
        : undefined
    }
    if (photorealisticRef.current) {
      photorealisticRef.current.show = visibility.googlePhotorealistic
    }
    if (buildingsRef.current) {
      buildingsRef.current.show = visibility.osmBuildings
    }
    for (const { key } of IMAGERY_ASSETS) {
      const layer = imageryLayersRef.current[key]
      if (layer) layer.show = visibility[key]
    }
  }, [visibility, bandConfig])

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
    viewerRef.current = viewer

    if (visibilityRef.current.elevationBand) {
      viewer.scene.globe.material = buildElevationBandMaterial(viewer.scene, bandConfigRef.current)
    }

    let disposed = false

    void (async () => {
      viewer.camera.flyTo({
        destination: Cartesian3.fromDegrees(-122.430398, 37.772770, 559.0),
        orientation: {
          heading: CesiumMath.toRadians(22.44),
          pitch: CesiumMath.toRadians(-11.07),
          roll: CesiumMath.toRadians(0.0),
        },
      })

      const photorealistic = await Cesium3DTileset.fromIonAssetId(2275207)
      if (!disposed) {
        photorealistic.show = visibilityRef.current.googlePhotorealistic
        viewer.scene.primitives.add(photorealistic)
        photorealisticRef.current = photorealistic
      }

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
      viewerRef.current = null
      photorealisticRef.current = null
      buildingsRef.current = null
      imageryLayersRef.current = {}
      viewer.destroy()
    }
  }, [])

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key !== 'p') return
      const viewer = viewerRef.current
      if (!viewer) return
      const { camera } = viewer
      const carto = camera.positionCartographic
      const lon = CesiumMath.toDegrees(carto.longitude)
      const lat = CesiumMath.toDegrees(carto.latitude)
      const height = carto.height
      const heading = CesiumMath.toDegrees(camera.heading)
      const pitch = CesiumMath.toDegrees(camera.pitch)
      const roll = CesiumMath.toDegrees(camera.roll)
      console.log('[camera] flyTo params:', {
        destination: { longitude: lon, latitude: lat, height },
        orientation: { heading, pitch, roll },
      })
      console.log(
        `[camera] Cartesian3.fromDegrees(${lon.toFixed(6)}, ${lat.toFixed(6)}, ${height.toFixed(1)}), heading: ${heading.toFixed(2)}°, pitch: ${pitch.toFixed(2)}°, roll: ${roll.toFixed(2)}°`,
      )
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [])

  const toggle = (key: keyof Visibility) =>
    setVisibility((prev) => ({ ...prev, [key]: !prev[key] }))

  // const setBand = (key: keyof BandConfig, value: number | boolean) =>
  //   setBandConfig((prev) => ({ ...prev, [key]: value }))

  const imageryDisabled = visibility.googlePhotorealistic
  // const bandDisabled = !visibility.elevationBand

  return (
    <div style={{ position: 'fixed', inset: 0 }}>
      <div ref={containerRef} style={{ position: 'absolute', inset: 0 }} />

      <div className="ion-assets-panel">
        <div className="ion-assets-panel__header">Ion Assets</div>
        <ul className="ion-assets-panel__list">
          {/* Globe Material section — hidden, restore to re-enable elevation band toggle
          <li className="ion-assets-panel__section">Globe Material</li>
          <li className="ion-assets-panel__item">
            <span className="ion-assets-panel__label">Elevation Band</span>
            <label className="ion-assets-panel__toggle">
              <input
                type="checkbox"
                checked={visibility.elevationBand}
                onChange={() => toggle('elevationBand')}
              />
              <span className="ion-assets-panel__toggle-track" />
            </label>
          </li>
          */}
          <li className="ion-assets-panel__section">3D Tiles</li>
          <li className="ion-assets-panel__item">
            <span className="ion-assets-panel__label">Google Photorealistic</span>
            <label className="ion-assets-panel__toggle">
              <input
                type="checkbox"
                checked={visibility.googlePhotorealistic}
                onChange={() => toggle('googlePhotorealistic')}
              />
              <span className="ion-assets-panel__toggle-track" />
            </label>
          </li>
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
          <li className={`ion-assets-panel__section${imageryDisabled ? ' ion-assets-panel__section--disabled' : ''}`}>
            Imagery
          </li>
          {IMAGERY_ASSETS.map(({ key, label }) => (
            <li
              key={key}
              className={`ion-assets-panel__item${imageryDisabled ? ' ion-assets-panel__item--disabled' : ''}`}
            >
              <span className="ion-assets-panel__label">{label}</span>
              <label className="ion-assets-panel__toggle">
                <input
                  type="checkbox"
                  checked={visibility[key]}
                  onChange={() => toggle(key)}
                  disabled={imageryDisabled}
                />
                <span className="ion-assets-panel__toggle-track" />
              </label>
            </li>
          ))}
        </ul>
      </div>

      {/* Band config panel — hidden, restore to re-enable elevation band controls
      <div className={`band-config-panel${bandDisabled ? ' band-config-panel--disabled' : ''}`}>
        <div className="band-config-panel__header">Elevation Bands</div>
        <div className="band-config-panel__row">
          <label className="band-config-panel__label">Gradient</label>
          <label className="ion-assets-panel__toggle">
            <input
              type="checkbox"
              checked={bandConfig.gradient}
              onChange={() => setBand('gradient', !bandConfig.gradient)}
              disabled={bandDisabled}
            />
            <span className="ion-assets-panel__toggle-track" />
          </label>
        </div>
        {(
          [
            { key: 'band1Position', label: 'Band 1 (blue)', min: 0, max: 1400, color: '#4af' },
            { key: 'band2Position', label: 'Band 2 (green)', min: 0, max: 1400, color: '#4d4' },
            { key: 'band3Position', label: 'Band 3 (red)', min: 0, max: 1400, color: '#f55' },
            { key: 'bandThickness', label: 'Thickness', min: 10, max: 300, color: undefined },
            { key: 'bandTransparency', label: 'Band opacity', min: 0, max: 1, step: 0.05, color: undefined },
            { key: 'backgroundTransparency', label: 'BG opacity', min: 0, max: 1, step: 0.05, color: undefined },
          ] as { key: keyof BandConfig; label: string; min: number; max: number; step?: number; color?: string }[]
        ).map(({ key, label, min, max, step = 1, color }) => (
          <div key={key} className="band-config-panel__row">
            <label className="band-config-panel__label" style={color ? { color } : undefined}>{label}</label>
            <input
              type="range"
              className="band-config-panel__slider"
              min={min}
              max={max}
              step={step}
              value={bandConfig[key] as number}
              onChange={(e) => setBand(key, parseFloat(e.target.value))}
              disabled={bandDisabled}
            />
            <span className="band-config-panel__value">
              {step < 1 ? (bandConfig[key] as number).toFixed(2) : Math.round(bandConfig[key] as number)}
              {max <= 1 ? '' : 'm'}
            </span>
          </div>
        ))}
        <button
          className="band-config-panel__reset"
          onClick={() => setBandConfig(DEFAULT_BAND_CONFIG)}
          disabled={bandDisabled}
        >
          Reset
        </button>
      </div>
      */}
    </div>
  )
}

export default CesiumViewer
