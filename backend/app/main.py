from fastapi import FastAPI

from backend.app.core.database import Base, engine
from backend.app.models.document import Document
from backend.app.api.routes.documents import router as documents_router


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Document Intelligence API",
    version="1.0.0",
)


app.include_router(documents_router)


@app.get("/api/v1/health")
def health_check():
    return {
        "status": "healthy",
        "message": "Document Intelligence API is running",
    }
