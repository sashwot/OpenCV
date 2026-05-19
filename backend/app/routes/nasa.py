from fastapi import APIRouter, HTTPException
import requests

from app.services.opencv_service import process_image

router = APIRouter(prefix="/nasa", tags=["nasa"])

API_KEY = "hJDhSsLSrNCv10NDORVGJiTkt5eC5KeGSrmJGaX6"
EPIC_URL = f"https://api.nasa.gov/EPIC/api/natural/date/2019-05-30?api_key={API_KEY}"
BPOD_URL = f"https://api.nasa.gov/planetary/apod?api_key={API_KEY}"


def fetch_nasa_json(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.HTTPError as exc:
        raise HTTPException(
            status_code=exc.response.status_code,
            detail=f"NASA API returned an error: {exc.response.text}",
        ) from exc
    except requests.RequestException as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Could not reach NASA API: {exc}",
        ) from exc


def get_apod():
    return fetch_nasa_json(EPIC_URL)


def get_bpod():
    return fetch_nasa_json(BPOD_URL)


def get_epic_image_url(item, ext="png"):
    date = item["date"].split()[0]
    year, month, day = date.split("-")
    image_name = item["image"]

    return (
        f"https://api.nasa.gov/EPIC/archive/natural/"
        f"{year}/{month}/{day}/{ext}/{image_name}.{ext}"
        f"?api_key={API_KEY}"
    )


def add_epic_image_urls(items):
    return [
        {
            **item,
            "image_url": get_epic_image_url(item),
        }
        for item in items
    ]


def refine_nasa_image(image_url, include_image=True):
    try:
        return process_image(image_url, include_image=include_image)
    except ModuleNotFoundError as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Missing Python dependency for image processing: {exc.name}",
        ) from exc
    except requests.RequestException as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Could not download NASA image: {exc}",
        ) from exc


def get_nasa_data(refine=False, limit=1, include_image=True):
    items = add_epic_image_urls(get_apod())

    if not refine:
        return items

    for item in items[:limit]:
        item["refined"] = refine_nasa_image(
            item["image_url"],
            include_image=include_image,
        )

    return items


def get_nasa_galaxy():
    return get_bpod()


@router.get("/")
def read_nasa_data(refine: bool = False, limit: int = 1, include_image: bool = True):
    return get_nasa_data(refine=refine, limit=limit, include_image=include_image)


@router.get("/apod")
def read_apod():
    return get_apod()


@router.get("/bpod")
def read_bpod():
    return get_bpod()


@router.get("/galaxy")
def read_nasa_galaxy():
    return get_nasa_galaxy()


@router.get("/galaxy/process")
def process_nasa_galaxy(include_image: bool = True):
    data = get_nasa_galaxy()
    image_url = data.get("url")

    if not image_url:
        raise HTTPException(
            status_code=502,
            detail="NASA APOD response did not include an image URL.",
        )

    return refine_nasa_image(image_url, include_image=include_image)


@router.get("/apod/process")
def process_nasa_data(limit: int = 1, include_image: bool = True):
    return get_nasa_data(refine=True, limit=limit, include_image=include_image)
