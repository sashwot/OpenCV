# NEWAPP NASA Image Viewer

NEWAPP is a small full-stack app that fetches NASA imagery from a FastAPI backend and displays original plus OpenCV-refined images in a React/Vite frontend.

The app currently shows:

- NASA Astronomy Picture of the Day image
- OpenCV-refined APOD image
- NASA EPIC Earth image
- OpenCV-refined EPIC Earth image

## Project Structure

```text
backend/
  app/
    main.py
    routes/nasa.py
    services/opencv_service.py

frontend/
  src/App.tsx
  src/App.css
```

## Backend

The backend is a FastAPI app. It calls NASA APIs and uses OpenCV to refine image data.

Start the backend from the `backend` folder:

```bash
cd backend
venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Backend URL:

```text
http://127.0.0.1:8000
```

API docs:

```text
http://127.0.0.1:8000/docs
```

Important endpoints:

```text
GET /nasa/galaxy
GET /nasa/galaxy/process
GET /nasa/apod/process?limit=1
```

To return smaller metadata without base64 image data:

```text
GET /nasa/galaxy/process?include_image=false
GET /nasa/apod/process?limit=1&include_image=false
```

## Frontend

Start the frontend from the `frontend` folder:

```bash
cd frontend
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```

Frontend URL:

```text
http://127.0.0.1:5173
```

Build for production:

```bash
npm run build
```

## Notes

The frontend expects the backend to be running at:

```text
http://127.0.0.1:8000
```

If images do not load, check:

- FastAPI is running
- The NASA API request succeeds
- CORS is enabled in `backend/app/main.py`
- OpenCV is installed in the backend virtual environment

The backend currently uses this OpenCV package:

```text
opencv-python-headless==4.10.0.84
```

This version was chosen because a newer OpenCV wheel had a missing macOS dynamic library issue.
