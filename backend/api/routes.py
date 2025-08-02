"""api/routes.py - Minimal API for Game Flow

SIMPLE ENDPOINTS:
- New game creation
- Action processing
- Game state retrieval
- Development utilities
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import logging

from game.flow_controller import game_controller

logger = logging.getLogger(__name__)

router = APIRouter()

# Request/Response models
class NewGameRequest(BaseModel):
    character_name: str

class ActionRequest(BaseModel):
    session_id: str
    action: str

class GameResponse(BaseModel):
    session_id: str
    narrative: str
    game_state: Dict[str, Any]
    options: Optional[List[str]] = None

# Core game endpoints
@router.post("/new-game")
async def create_new_game(request: NewGameRequest):
    """Start a new game session"""
    try:
        session_id = game_controller.create_session(request.character_name)
        game_state = game_controller.get_session(session_id)
        
        narrative = f"""Welcome, {request.character_name}!
        
You stand at the edge of the known world, where civilization gives way to mystery and danger. 
The Mythic Bastionland stretches before you - a realm of fallen industry, ancient powers, and forgotten truths.

Your journey begins..."""
        
        return {
            "session_id": session_id,
            "narrative": narrative,
            "game_state": game_state.to_dict(),
            "options": ["Explore the area", "Check your status", "Head into the wilderness"]
        }
        
    except Exception as e:
        logger.error(f"Error creating new game: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/action")
async def process_action(request: ActionRequest):
    """Process a player action"""
    try:
        result = await game_controller.process_action(request.session_id, request.action)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except Exception as e:
        logger.error(f"Error processing action: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/game/{session_id}")
async def get_game_state(session_id: str):
    """Get current game state"""
    game_state = game_controller.get_session(session_id)
    if not game_state:
        raise HTTPException(status_code=404, detail="Game session not found")
    
    return {
        "session_id": session_id,
        "game_state": game_state.to_dict(),
        "narrative": "You take a moment to assess your situation...",
        "options": ["Continue", "Rest", "Check status"]
    }

# Development and utility endpoints
@router.get("/sessions")
async def list_sessions():
    """List all active game sessions"""
    return {
        "sessions": game_controller.list_sessions()
    }

@router.get("/templates")
async def list_prompt_templates():
    """List available AI prompt templates"""
    from game.ollama_client import ollama
    return {
        "templates": ollama.list_templates()
    }

@router.post("/test-prompt")
async def test_prompt(data: dict):
    """Test a prompt template with custom data"""
    from game.ollama_client import ollama
    
    template_name = data.get("template")
    kwargs = data.get("data", {})
    
    if not template_name:
        raise HTTPException(status_code=400, detail="Template name required")
    
    try:
        result = await ollama.generate(template_name, **kwargs)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/experiment")
async def create_prompt_experiment(data: dict):
    """Create and test a new prompt template"""
    from game.ollama_client import ollama
    
    name = data.get("name")
    system = data.get("system")
    user = data.get("user")
    variables = data.get("variables", [])
    test_data = data.get("test_data", {})
    
    if not all([name, system, user]):
        raise HTTPException(status_code=400, detail="Name, system, and user prompts required")
    
    try:
        template = ollama.create_prompt_experiment(name, system, user, variables)
        
        # Test the template if test data provided
        result = None
        if test_data:
            result = await ollama.generate(f"experiment_{name}", **test_data)
        
        return {
            "template_created": template.name,
            "test_result": result
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Health check
@router.get("/health")
async def health_check():
    """API health check"""
    return {"status": "healthy", "active_sessions": len(game_controller.active_sessions)}

# API Status endpoint (for compatibility)
@router.get("/status") 
async def api_status():
    """API status with endpoint info"""
    return {
        "status": "active",
        "game": "Mythic Bastionland",
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