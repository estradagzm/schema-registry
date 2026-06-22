from fastapi import FastAPI
from app.routes import schemas, validate

app = FastAPI(
    title="Schema Registry",
    description="Register JSON schemas and validate payloads against them.",
    version="1.0.0",
)

app.include_router(schemas.router, prefix="/schemas", tags=["schemas"])
app.include_router(validate.router, prefix="/validate", tags=["validate"])


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}
