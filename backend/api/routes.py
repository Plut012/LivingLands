"""api/routes.py - Single Route Game API

SINGLE ENDPOINT:
- All user input goes to flow_controller
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import logging

from game.flow_controller import game_controller

logger = logging.getLogger(__name__)

router = APIRouter()

# Single request model
class InputRequest(BaseModel):
    input: str
    selected_intent: str = None

# Single route - everything goes to flow_controller
@router.post("/input")
async def process_input(request: InputRequest):
    """Single route: all input goes to flow_controller"""
    try:
        # Create session if none exists (simplified - no character creation)
        session_id = "default_session"
        if not game_controller.get_session(session_id):
            game_controller.create_session("Pluto")
            # Override with our default session_id
            game_state = game_controller.active_sessions.pop(list(game_controller.active_sessions.keys())[-1])
            game_controller.active_sessions[session_id] = game_state
        
        # Send everything to flow_controller
        result = await game_controller.process_action(session_id, request.input, request.selected_intent)
        return result
        
    except Exception as e:
        logger.error(f"Error processing input: {e}")
        raise HTTPException(status_code=500, detail=str(e))

