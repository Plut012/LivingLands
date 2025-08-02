"""
main.py - FastAPI Application for Mythic Bastionlands

PLAN:
1. Initialize FastAPI app
2. Configure CORS for web clients
3. Include all route modules
4. Setup database connections
5. Configure error handling

FRAMEWORK:
- Keep initialization simple
- Use dependency injection for shared resources
- Handle errors gracefully
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import logging
import os
from typing import Dict

# Import our modules
from api.routes import router as api_router
from database import init_db, get_db

# STEP 1: Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# STEP 2: Define lifespan handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events"""
    # Startup
    logger.info("Starting Mythic Bastionlands server...")
    init_db()
    logger.info("Database initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")

# STEP 3: Create FastAPI app
app = FastAPI(
    title="Mythic Bastionlands API",
    description="Backend API for Mythic Bastionlands text adventure game",
    version="0.1.0",
    lifespan=lifespan
)

# STEP 4: Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# STEP 5: Include routers
app.include_router(api_router, prefix="/api/v1")

# STEP 6: API Status endpoint
@app.get("/api/status")
async def api_status():
    """API status check"""
    return {
        "status": "active",
        "game": "Mythic Bastionlands",
        "version": "0.1.0",
        "endpoints": {
            "new_game": "/api/v1/new-game",
            "game_state": "/api/v1/game-state",
            "action": "/api/v1/action",
            "character": "/api/v1/character",
            "command": "/api/v1/command"
        }
    }

# STEP 6.1: Serve static files (frontend) - must be last
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="static")

# STEP 7: Health check endpoint
@app.get("/health")
async def health_check():
    """Health check for monitoring"""
    return {"status": "healthy"}

# STEP 8: Global exception handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    return {
        "error": exc.detail,
        "status_code": exc.status_code
    }

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}")
    return {
        "error": "Internal server error",
        "status_code": 500
    }

# STEP 9: Middleware for request logging
@app.middleware("http")
async def log_requests(request, call_next):
    """Log all requests"""
    logger.info(f"{request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"Response status: {response.status_code}")
    return response

# STEP 10: Run server (for development)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # Enable hot reload for development
    )
