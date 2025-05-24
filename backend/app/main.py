"""
FastAPI application entry point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from .routes import generations, models, images, batch
from .api import setup_exception_handlers


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    
    app = FastAPI(
        title="Nymo Art API",
        description="Professional AI Image Generation API",
        version="4.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:5175", "http://localhost:5176", "http://localhost:5177"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Setup exception handlers
    setup_exception_handlers(app)
    
    # Include routers
    app.include_router(generations.router, prefix="/api/v1")
    app.include_router(models.router, prefix="/api/v1")
    app.include_router(batch.router, prefix="/api/v1")
    app.include_router(images.router)
    
    @app.get("/")
    async def root():
        """Health check endpoint."""
        return {
            "service": "Nymo Art API",
            "version": "4.0.0",
            "status": "healthy"
        }
    
    @app.get("/health")
    async def health():
        """Detailed health check."""
        return {
            "status": "healthy",
            "timestamp": "2025-05-24T00:00:00Z",
            "version": "4.0.0"
        }
    
    logger.info("FastAPI application created successfully")
    return app


# Create app instance
app = create_app()
