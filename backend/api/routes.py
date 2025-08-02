"""
api/routes.py - API Routes for Mythic Bastionlands

PLAN:
1. Define request/response models
2. Create game session endpoints
3. Action processing endpoint
4. Game state retrieval
5. Character management

FRAMEWORK:
- Use Pydantic for validation
- Keep endpoints focused
- Return consistent response formats
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime
import uuid

# Import game modules
from models import GameSession, Company, Character, create_knight
from actions import process_action, create_action, ActionResult
from world import initialize_world, travel_cost
from combat import start_combat
from llm_client import interpret_player_input, generate_narrative, build_context
from database import get_db

# STEP 1: Create router
router = APIRouter()

# STEP 2: Define request/response models
class NewGameRequest(BaseModel):
    """Request to start a new game"""
    company_name: str = Field(..., min_length=1, max_length=50)
    knight_names: List[str] = Field(..., min_items=1, max_items=6)

class GameResponse(BaseModel):
    """Standard game response"""
    session_id: str
    narrative: str
    game_state: Dict
    options: Optional[List[str]] = None

class ActionRequest(BaseModel):
    """Player action request"""
    session_id: str
    action_text: str = Field(..., min_length=1, max_length=500)

class CommandRequest(BaseModel):
    """Natural language command"""
    session_id: str
    command: str = Field(..., min_length=1, max_length=500)

# STEP 3: In-memory session storage (replace with database)
game_sessions: Dict[str, GameSession] = {}

# STEP 4: Session endpoints for frontend compatibility
@router.post("/session/start")
async def start_session():
    """Start a new session - frontend compatibility endpoint"""
    session_id = str(uuid.uuid4())
    return {"sessionId": session_id}

@router.post("/session/save")
async def save_session(data: dict):
    """Save session data - frontend compatibility endpoint"""
    return {"status": "saved"}

# STEP 4: New game endpoint
@router.post("/new-game", response_model=GameResponse)
async def new_game(request: NewGameRequest):
    """Initialize a new game session"""
    
    # Generate session ID
    session_id = str(uuid.uuid4())
    
    # STEP 4.1: Create knights
    knights = []
    for name in request.knight_names:
        # Roll random stats (simplified)
        import random
        knight = create_knight(
            name=name,
            vig=random.randint(8, 15),
            cla=random.randint(8, 15),
            spi=random.randint(8, 15),
            gd=random.randint(4, 8)
        )
        knights.append(knight)
    
    # STEP 4.2: Create company
    company = Company(name=request.company_name, knights=knights)
    
    # STEP 4.3: Initialize world
    world = initialize_world()
    
    # STEP 4.4: Create game session
    session = GameSession(
        session_id=session_id,
        company=company,
        current_hex=(0, 0),
        world_hexes=world
    )
    
    # Store session
    game_sessions[session_id] = session
    
    # STEP 4.5: Generate opening narrative
    narrative = f"""
    The {company.name} stands ready at the edge of the realm.
    {len(knights)} knights have sworn the oath:
    Seek the Myths. Honour the Seers. Protect the Realm.
    
    Your journey begins in the borderlands...
    """
    
    return GameResponse(
        session_id=session_id,
        narrative=narrative.strip(),
        game_state={
            "company": company.name,
            "knights": [k.name for k in knights],
            "location": "Starting Hex",
            "turn": 0
        },
        options=["Explore the area", "Travel north", "Make camp"]
    )

# STEP 5: Get game state endpoint
@router.get("/game-state/{session_id}", response_model=GameResponse)
async def get_game_state(session_id: str):
    """Get current game state"""
    
    # Retrieve session
    session = game_sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Game session not found")
    
    # Get current hex
    current_hex = session.get_current_hex()
    
    # Build state summary
    game_state = {
        "company": session.company.name,
        "location": current_hex.landmark if current_hex and current_hex.landmark else "Wilderness",
        "turn": session.turn_count,
        "knights": [
            {
                "name": k.name,
                "guard": k.guard,
                "max_guard": k.max_guard,
                "wounds": len(k.wounds)
            }
            for k in session.company.knights
        ]
    }
    
    return GameResponse(
        session_id=session_id,
        narrative="You survey your surroundings...",
        game_state=game_state,
        options=["Explore", "Travel", "Rest", "Check equipment"]
    )

# STEP 6: Process action endpoint
@router.post("/action", response_model=GameResponse)
async def process_player_action(request: ActionRequest):
    """Process a player action"""
    
    # Retrieve session
    session = game_sessions.get(request.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Game session not found")
    
    # STEP 6.1: Create context and interpret action
    context = build_context(session)
    action_parts = interpret_player_input(request.action_text, context)
    
    # STEP 6.2: Create action object
    action = create_action(
        intent=action_parts["intent"],
        leverage=action_parts["leverage"],
        has_cost=action_parts.get("cost") is not None,
        is_risky=action_parts.get("risk") != "no_risk"
    )
    
    # STEP 6.3: Process the action
    # For now, assume success for no-risk actions
    if action.risk.value == "no_risk":
        result = process_action(action, session.company.knights[0])
    else:
        # Would need dice roll here
        result = process_action(action, session.company.knights[0], (True, 10))
    
    # STEP 6.4: Generate narrative
    narrative = generate_narrative(session, result.outcome, {"action": action.intent})
    
    # STEP 6.5: Update game state
    session.turn_count += 1
    
    return GameResponse(
        session_id=request.session_id,
        narrative=narrative,
        game_state={
            "last_action": action.intent,
            "outcome": result.outcome.value,
            "turn": session.turn_count
        }
    )

# STEP 7: Character details endpoint
@router.get("/character/{session_id}/{character_name}")
async def get_character(session_id: str, character_name: str):
    """Get detailed character information"""
    
    # Retrieve session
    session = game_sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Game session not found")
    
    # Find character
    character = None
    for knight in session.company.knights:
        if knight.name.lower() == character_name.lower():
            character = knight
            break
    
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    # Build detailed info
    return {
        "name": character.name,
        "is_knight": character.is_knight,
        "virtues": {
            "vigour": character.virtues.get("VIG", 0),
            "clarity": character.virtues.get("CLA", 0),
            "spirit": character.virtues.get("SPI", 0)
        },
        "guard": {
            "current": character.guard,
            "max": character.max_guard
        },
        "equipment": character.equipment,
        "wounds": character.wounds,
        "status": {
            "exhausted": character.virtues.get("VIG", 1) == 0,
            "exposed": character.virtues.get("CLA", 1) == 0,
            "impaired": character.virtues.get("SPI", 1) == 0
        }
    }

# STEP 8: Natural language command endpoint
@router.post("/command", response_model=GameResponse)
async def process_command(request: CommandRequest):
    """Process natural language commands"""
    
    # Retrieve session
    session = game_sessions.get(request.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Game session not found")
    
    # STEP 8.1: Interpret command
    context = build_context(session)
    command_lower = request.command.lower()
    
    # STEP 8.2: Handle specific commands
    if "status" in command_lower or "check" in command_lower:
        # Return status
        return await get_game_state(request.session_id)
    
    elif "rest" in command_lower or "camp" in command_lower:
        # Handle rest action
        narrative = "The company makes camp for the night. Guards are restored after a peaceful rest."
        for knight in session.company.knights:
            knight.guard = knight.max_guard
        
        return GameResponse(
            session_id=request.session_id,
            narrative=narrative,
            game_state={"action": "rest", "guards_restored": True}
        )
    
    elif any(word in command_lower for word in ["move", "travel", "go"]):
        # Handle travel
        direction = "north"  # Would parse from command
        narrative = f"The company travels {direction} through the wilderness..."
        
        # Simple movement
        x, y = session.current_hex
        session.current_hex = (x, y + 1)
        
        return GameResponse(
            session_id=request.session_id,
            narrative=narrative,
            game_state={"moved_to": session.current_hex}
        )
    
    else:
        # Process as general action
        return await process_player_action(
            ActionRequest(
                session_id=request.session_id,
                action_text=request.command
            )
        )

# STEP 9: Combat initiation endpoint
@router.post("/combat/start")
async def start_combat_encounter(session_id: str, enemy_type: str = "bandits"):
    """Start a combat encounter"""
    
    # Retrieve session
    session = game_sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Game session not found")
    
    # Define some basic enemies
    enemy_templates = {
        "bandits": [
            {"name": "Bandit Leader", "vig": 8, "cla": 6, "gd": 4, "armor": 1},
            {"name": "Bandit", "vig": 5, "cla": 5, "gd": 2, "armor": 0},
            {"name": "Bandit", "vig": 5, "cla": 5, "gd": 2, "armor": 0}
        ],
        "wolves": [
            {"name": "Alpha Wolf", "vig": 7, "cla": 8, "gd": 0, "armor": 0},
            {"name": "Wolf", "vig": 5, "cla": 6, "gd": 0, "armor": 0}
        ]
    }
    
    enemies = enemy_templates.get(enemy_type, enemy_templates["bandits"])
    
    # Start combat
    combat_state = start_combat(session.company.knights, enemies)
    session.active_combat = combat_state
    
    return {
        "combat_started": True,
        "enemies": [e["name"] for e in enemies],
        "initiative_order": combat_state.initiative_order,
        "narrative": f"Combat begins! {len(enemies)} {enemy_type} attack!"
    }

# STEP 10: List active sessions endpoint (for debugging)
@router.get("/sessions")
async def list_sessions():
    """List all active game sessions"""
    return {
        "active_sessions": len(game_sessions),
        "sessions": [
            {
                "id": sid,
                "company": s.company.name,
                "turn": s.turn_count,
                "location": s.current_hex
            }
            for sid, s in game_sessions.items()
        ]
    }
