from io import BytesIO
import base64

import requests


def load_image_from_url(image_url):
    import numpy as np
    from PIL import Image

    response = requests.get(image_url, timeout=20)
    response.raise_for_status()

    pil_image = Image.open(BytesIO(response.content)).convert("RGB")
    image_rgb = np.array(pil_image, dtype=np.uint8)
    return np.ascontiguousarray(image_rgb)


def refine_image_array(image_rgb):
    import cv2
    import numpy as np

    image_bgr = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)
    lab = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2LAB)
    lightness, channel_a, channel_b = cv2.split(lab)

    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced_lightness = clahe.apply(lightness)
    enhanced_lab = cv2.merge((enhanced_lightness, channel_a, channel_b))
    enhanced_bgr = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)

    denoised_bgr = cv2.fastNlMeansDenoisingColored(
        enhanced_bgr,
        None,
        h=4,
        hColor=4,
        templateWindowSize=7,
        searchWindowSize=21,
    )

    blur = cv2.GaussianBlur(denoised_bgr, (0, 0), sigmaX=1.0)
    sharpened_bgr = cv2.addWeighted(denoised_bgr, 1.35, blur, -0.35, 0)
    refined_rgb = cv2.cvtColor(sharpened_bgr, cv2.COLOR_BGR2RGB)
    return np.ascontiguousarray(refined_rgb)


def image_to_data_url(image_rgb, ext=".png"):
    import cv2

    image_bgr = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)
    ok, buffer = cv2.imencode(ext, image_bgr)

    if not ok:
        raise ValueError("Could not encode refined image.")

    encoded = base64.b64encode(buffer).decode("ascii")
    media_type = "image/png" if ext == ".png" else "image/jpeg"
    return f"data:{media_type};base64,{encoded}"


def process_image(image_url, include_image=True):
    import cv2

    image_rgb = load_image_from_url(image_url)
    image_bgr = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 80, 160)
    refined_rgb = refine_image_array(image_rgb)

    result = {
        "source_url": image_url,
        "shape_rgb": list(image_rgb.shape),
        "shape_bgr": list(image_bgr.shape),
        "shape_gray": list(gray.shape),
        "shape_edges": list(edges.shape),
        "shape_refined": list(refined_rgb.shape),
        "dtype": str(image_rgb.dtype),
    }

    if include_image:
        result["refined_image"] = image_to_data_url(refined_rgb)

    return result
