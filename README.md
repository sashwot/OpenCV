[OutPut (1).pdf](https://github.com/user-attachments/files/35436240/OutPut.1.pdf)

# NASA Image Enhancer

A full-stack web app that fetches imagery from NASA's public APIs and enhances it with a classical OpenCV image-processing pipeline, showing the original and enhanced versions side by side.

**Stack:** Python · FastAPI · OpenCV · React · TypeScript · Vite

![Original vs. enhanced comparison](docs/screenshot.png)
<!-- Add a screenshot or GIF of the app here. This is the most important line in the README. -->

---

## Features

- Pulls the **Astronomy Picture of the Day (APOD)** and **EPIC full-disk Earth** images (natural color, currently a fixed date: 2019-05-30) from NASA's APIs
- Enhances each image with a multi-step OpenCV pipeline (contrast, denoising, sharpening)
- Shows the original and enhanced images side by side in a React UI
- REST API with interactive docs (Swagger UI at `/docs`)
- Optional metadata-only responses (`include_image=false`) for lightweight requests

## How the enhancement pipeline works

Each image goes through `refine_image_array()` in `backend/app/services/opencv_service.py`:

| Step | Operation | Why |
|---|---|---|
| 1 | Convert RGB → LAB color space | Separates lightness from color, so contrast can be adjusted without shifting hues |
| 2 | **CLAHE** on the L channel (`clipLimit=2.0`, `tileGridSize=8×8`) | Boosts local contrast in dark or flat regions while limiting noise amplification |
| 3 | Convert LAB → BGR | Recombines the enhanced lightness with the original color channels |
| 4 | **Non-local means denoising** (`h=4`, `hColor=4`) | Removes noise that CLAHE can amplify, while preserving edges and fine detail |
| 5 | **Unsharp masking**: Gaussian blur (σ = 1.0), then `1.35 × image − 0.35 × blur` | Restores crispness lost during denoising |

The `/process` endpoints also run **Canny edge detection** (thresholds 80/160) on a grayscale copy and report the edge map's dimensions.

These are standard preprocessing techniques used in other imaging fields too, including satellite imagery and medical imaging (for example, CLAHE on X-ray and CT images).

## Project structure

```
.
├── backend/
│   └── app/
│       ├── main.py                  # FastAPI app, CORS setup
│       ├── routes/
│       │   └── nasa.py              # NASA API endpoints
│       └── services/
│           └── opencv_service.py    # Image enhancement pipeline
├── frontend/
│   └── src/
│       ├── App.tsx                  # Main UI: original vs. enhanced view
│       └── App.css
├── OutPut.pdf                       # Sample output
└── README.md
```

## Getting started

### Prerequisites

- Python 3.10+
- Node.js 18+
- A NASA API key (free at <https://api.nasa.gov>). `DEMO_KEY` works for light testing.

Set it as an environment variable before starting the backend:

```bash
export NASA_API_KEY=your_key_here      # Windows (PowerShell): $env:NASA_API_KEY="your_key_here"
```

### 1. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

API docs: <http://127.0.0.1:8000/docs>

### 2. Frontend

```bash
cd frontend
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```

Open <http://127.0.0.1:5173>. The frontend expects the backend at `http://127.0.0.1:8000`.

To create a production build: `npm run build`

## API endpoints

| Method | Endpoint | Query params | Description |
|---|---|---|---|
| GET | `/nasa/` | `refine` (default `false`), `limit` (default `1`), `include_image` (default `true`) | List EPIC Earth images with image URLs; optionally enhance the first `limit` items |
| GET | `/nasa/galaxy` | none | Raw APOD metadata (title, explanation, image URL) |
| GET | `/nasa/galaxy/process` | `include_image` (default `true`) | Fetch the APOD image and return the enhanced version (502 if APOD has no image URL, e.g. video days) |
| GET | `/nasa/apod/process` | `limit` (default `1`), `include_image` (default `true`) | List EPIC Earth images with the first `limit` items enhanced |

Set `include_image=false` to return metadata only, without base64 image data.

## Results

<!-- [OutPut (1).pdf](https://github.com/user-attachments/files/35436240/OutPut.1.pdf) -->

| Original | Enhanced |
|---|---|
| ![](docs/original_1.png) | ![](docs/enhanced_1.png) |

## Notes

- **OpenCV version is pinned** to `opencv-python-headless==4.10.0.84` because a newer wheel had a missing dynamic library issue on macOS.
- The headless build is used because the backend doesn't need GUI features.

## Troubleshooting

If images don't load:

1. Check that the FastAPI server is running on port 8000.
2. Check that the NASA API request succeeds (rate limits apply with `DEMO_KEY`).
3. Check that CORS is enabled in `backend/app/main.py`.
4. Check that OpenCV is installed in the backend virtual environment.

## Future work

- Let users pick the EPIC date instead of a fixed one
- Add user controls for pipeline parameters (CLAHE clip limit, denoising strength, sharpening amount)
- Display the Canny edge map in the UI
- Add quantitative image-quality metrics (e.g., contrast, sharpness, BRISQUE)
- Extend the pipeline to grayscale scientific and medical images (DICOM support, intensity windowing)
- Add unit tests and a Dockerfile for one-command setup

## Author

**Sashwot Koirala**: [LinkedIn](https://www.linkedin.com/in/YOUR-PROFILE) · [GitHub](https://github.com/sashwot)


