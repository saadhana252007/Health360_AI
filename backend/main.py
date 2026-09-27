from fastapi import FastAPI


app = FastAPI(
    title="Health360 AI",
    version="1.0.0",
    description="Modular AI-powered personal health checkup API"
)


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