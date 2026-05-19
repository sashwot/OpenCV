import { useEffect, useState } from 'react'
import './App.css'

const API_BASE = 'http://127.0.0.1:8000'

type GalaxyData = {
  title?: string
  explanation?: string
  url?: string
  hdurl?: string
  media_type?: string
}

type ProcessedImage = {
  source_url: string
  refined_image?: string
  shape_rgb: number[]
  shape_refined: number[]
  dtype: string
}

type EpicImage = {
  identifier: string
  caption: string
  date: string
  image_url: string
  refined?: ProcessedImage
}

function App() {
  const [galaxy, setGalaxy] = useState<GalaxyData | null>(null)
  const [processedGalaxy, setProcessedGalaxy] = useState<ProcessedImage | null>(
    null,
  )
  const [epicImage, setEpicImage] = useState<EpicImage | null>(null)
  const [status, setStatus] = useState('Loading NASA images...')
  const [error, setError] = useState('')

  useEffect(() => {
    const loadImages = async () => {
      try {
        setStatus('Fetching APOD and EPIC images from the backend...')
        setError('')

        const [galaxyResponse, processedGalaxyResponse, epicResponse] =
          await Promise.all([
            fetch(`${API_BASE}/nasa/galaxy`),
            fetch(`${API_BASE}/nasa/galaxy/process`),
            fetch(`${API_BASE}/nasa/apod/process?limit=1`),
          ])

        if (!galaxyResponse.ok) {
          throw new Error('Could not load APOD data.')
        }
        if (!processedGalaxyResponse.ok) {
          throw new Error('Could not load refined APOD image.')
        }
        if (!epicResponse.ok) {
          throw new Error('Could not load refined EPIC image.')
        }

        const galaxyJson = (await galaxyResponse.json()) as GalaxyData
        const processedGalaxyJson =
          (await processedGalaxyResponse.json()) as ProcessedImage
        const epicJson = (await epicResponse.json()) as EpicImage[]

        setGalaxy(galaxyJson)
        setProcessedGalaxy(processedGalaxyJson)
        setEpicImage(epicJson[0] ?? null)
        setStatus('Images ready')
      } catch (caught) {
        const message =
          caught instanceof Error ? caught.message : 'Something went wrong.'
        setError(message)
        setStatus('Unable to load images')
      }
    }

    loadImages()
  }, [])

  return (
    <main className="nasa-page">
      <header className="page-header">
        <div>
          <p className="eyebrow">NEWAPP NASA + OpenCV</p>
          <h1>Refined Space Images</h1>
        </div>
        <p className={error ? 'status error' : 'status'}>{error || status}</p>
      </header>

      <section className="image-section">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Astronomy Picture of the Day</p>
            <h2>{galaxy?.title ?? 'Galaxy image'}</h2>
          </div>
          {processedGalaxy && (
            <span className="meta">
              {processedGalaxy.shape_refined.join(' x ')} ·{' '}
              {processedGalaxy.dtype}
            </span>
          )}
        </div>

        <div className="image-grid">
          <figure>
            {galaxy?.url && <img src={galaxy.url} alt={galaxy.title ?? ''} />}
            <figcaption>Original</figcaption>
          </figure>
          <figure>
            {processedGalaxy?.refined_image && (
              <img
                src={processedGalaxy.refined_image}
                alt={`Refined ${galaxy?.title ?? 'NASA APOD image'}`}
              />
            )}
            <figcaption>OpenCV refined</figcaption>
          </figure>
        </div>

        {galaxy?.explanation && (
          <p className="description">{galaxy.explanation}</p>
        )}
      </section>

      <section className="image-section">
        <div className="section-heading">
          <div>
            <p className="eyebrow">EPIC Earth Camera</p>
            <h2>{epicImage?.identifier ?? 'Earth image'}</h2>
          </div>
          {epicImage?.refined && (
            <span className="meta">
              {epicImage.refined.shape_refined.join(' x ')} ·{' '}
              {epicImage.refined.dtype}
            </span>
          )}
        </div>

        <div className="image-grid">
          <figure>
            {epicImage?.image_url && (
              <img src={epicImage.image_url} alt={epicImage.caption} />
            )}
            <figcaption>Original</figcaption>
          </figure>
          <figure>
            {epicImage?.refined?.refined_image && (
              <img
                src={epicImage.refined.refined_image}
                alt={`Refined ${epicImage.identifier}`}
              />
            )}
            <figcaption>OpenCV refined</figcaption>
          </figure>
        </div>

        {epicImage && (
          <p className="description">
            {epicImage.caption}. Captured {epicImage.date}.
          </p>
        )}
      </section>
    </main>
  )
}

export default App
