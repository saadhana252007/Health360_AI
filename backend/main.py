from fastapi import FastAPI

from backend.routers.checkups import router as checkups_router
from backend.routers.assistant import router as assistant_router

app = FastAPI(
    title="Health360 AI",
    version="1.0.0",
    description="Modular AI-powered personal health checkup API"
)


app.include_router(checkups_router)
app.include_router(assistant_router)

@app.get("/")
def root():
    return {
        "name": "Health360 AI",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }