from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import logging
from sqlalchemy.exc import OperationalError
from app.database import Base, engine
from app.routes.nasa import router as nasa_router
from app.routes.products import router as products_router
from app.routes.user import router as user_router

logger = logging.getLogger("uvicorn.error")

# Try to create tables, but don't let a DB connection failure crash the app.
try:
	Base.metadata.create_all(bind=engine)
	logger.info("Database tables ensured using %s", os.getenv("DATABASE_URL", "sqlite (dev.db)"))
except OperationalError as e:
	logger.warning("Could not connect to database during startup: %s", e)
	logger.warning("Proceeding without creating tables — set DATABASE_URL or start your DB to enable tables creation.")

app = FastAPI()
app.add_middleware(
	CORSMiddleware,
	allow_origins=[
		"http://127.0.0.1:5173",
		"http://localhost:5173",
	],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)
app.include_router(nasa_router)
app.include_router(products_router)
app.include_router(user_router)


@app.get("/")
def read_root():
	return {"message": "NEWAPP backend is running"}
