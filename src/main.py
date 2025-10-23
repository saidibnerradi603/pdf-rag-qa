from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from config.settings import get_settings
from routes.auth import router as auth_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

settings = get_settings()


app = FastAPI(
    title=settings.project_name,
    version=settings.version,
    description="Retrieval-Augmented Generation system for intelligent question answering over PDF documents",
    docs_url="/docs",
    redoc_url="/redoc"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)

@app.get("/", tags=["Root"])
def root():
    """Root endpoint"""
    return {
        "message": "PDF RAG QA System API",
        "version": settings.version,
        "status": "running"
    }

@app.get("/health", tags=["Root"])
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.project_name
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0")