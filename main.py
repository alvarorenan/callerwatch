from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.core.config import settings
from app.routers import auth, security
from app.dependencies import get_cache_repository

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting CallerWatch API...")

    # Initialize connections
    cache_repo = await get_cache_repository()
    logger.info("Cache repository initialized")

    yield

    # Shutdown
    logger.info("Shutting down CallerWatch API...")
    await cache_repo.disconnect()
    logger.info("Connections closed")

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API de Verificação de Segurança de IPs e Callers",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(security.router)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "healthy"
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "debug": settings.DEBUG
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
