from fastapi import APIRouter

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/")
def read_products():
    return {"products": []}
