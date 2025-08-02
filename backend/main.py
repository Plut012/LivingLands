"""main.py - Minimal FastAPI Application

CLEAN SETUP:
- FastAPI app with essential middleware
- Simple logging
- Hot reload for development
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import logging
import os

from api.routes import router as api_router

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create app
app = FastAPI(
    title="Mythic Bastionland - Game Engine",
    description="Minimal skeleton for developing a text-based RPG with AI integration",
    version="0.1.0"
)

# Add CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

# API info endpoint (moved from root)
@app.get("/api")
async def api_info():
    """API endpoint info"""
    return {
        "message": "Mythic Bastionland Game Engine",
        "version": "0.1.0",
        "endpoints": {
            "new_game": "/api/v1/new-game",
            "action": "/api/v1/action", 
            "sessions": "/api/v1/sessions",
            "health": "/api/v1/health"
        },
        "development": {
            "templates": "/api/v1/templates",
            "test_prompt": "/api/v1/test-prompt",
            "experiment": "/api/v1/experiment"
        }
    }

# Serve frontend (must be last)
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="static")

# Development server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )