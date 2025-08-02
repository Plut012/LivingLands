"""flow_controller.py - Game Flow Management

GAME FLOW CONTROL:
- Manages game state transitions
- Handles player actions and responses
- Coordinates between different game systems
- Easy to extend with new mechanics
"""

from typing import Dict, Any, List, Optional, Tuple
import uuid
import json
import logging
from models import GameState, Character, create_new_game
from game.ollama_client import ollama

logger = logging.getLogger(__name__)

class GameFlowController:
    """Controls the flow of the game"""
    
    def __init__(self):
        self.active_sessions: Dict[str, GameState] = {}
        self.action_handlers = {}
        self._setup_default_handlers()
    
    def _setup_default_handlers(self):
        """Setup default action handlers"""
        self.action_handlers.update({
            "explore": self._handle_explore,
            "travel": self._handle_travel,
            "rest": self._handle_rest,
            "interact": self._handle_interact,
            "check": self._handle_check_status,
            # "inventory": self._handle_inventory,   # inventory management should not include language model
        })
    
    async def process_action(self, session_id: str, player_input: str, selected_intent: str = None) -> Dict[str, Any]:
        """Process a player action and return the result"""
        logger.info(f"Processing action for session {session_id}: '{player_input}' with intent: {selected_intent}")
        
        game_state = self.get_session(session_id)
        if not game_state:
            logger.error(f"Session {session_id} not found")
            return {"error": "Session not found"}

        if selected_intent:    # when button pressed, update recent user intent
            # update game state
            game_state.recent_user_intent = selected_intent
            return {}
        elif game_state.recent_user_intent:
            selected_intent = game_state.recent_user_intent
            action_data = {'intent': selected_intent, 'player_input': player_input}

        try:
            # Step 1: Interpret the player's action
            if not selected_intent:
                logger.debug("Step 1: Interpreting player action")
                action_data = await self._interpret_action(game_state, player_input)
                logger.info(f"Action interpreted as: {action_data.get('intent', 'unknown')}")
            
            # Step 2: Execute the action
            logger.debug("Step 2: Executing action")
            result = await self._execute_action(game_state, action_data)
            logger.info(f"Action executed successfully")
            
            # Step 3: Update game state
            logger.debug("Step 3: Updating game state")
            game_state.add_history_entry(
                action=player_input,
                result=result.get("narrative", ""),
                context=action_data
            )
            turn_count = game_state.game_data.get("turn_count", 0) + 1
            game_state.game_data["turn_count"] = turn_count
            logger.info(f"Game state updated, turn count now: {turn_count}")
            
            # Step 4: Generate response
            logger.debug("Step 4: Generating response")
            response = {
                "session_id": session_id,
                "narrative": result.get("narrative", ""),
                "game_state": game_state.to_dict(),
                "options": result.get("options", []),
                "action_data": action_data
            }
            
            logger.info(f"Action processing completed successfully for session {session_id}")
            # TODO clear user intent
            game_state.recent_user_intent = None
            return response
            
        except Exception as e:
            logger.error(f"Error processing action '{player_input}' for session {session_id}: {str(e)}", exc_info=True)
            return {
                "error": f"Error processing action: {str(e)}",
                "session_id": session_id
            }
    
    async def _interpret_action(self, game_state: GameState, player_input: str) -> Dict[str, Any]:
        """Interpret what the player wants to do"""
        
        # Build context for the AI
        context = ollama.build_game_context(game_state)

        # Use AI to interpret the action
        try:
            response = await ollama.generate(
                "action_interpreter",
                situation=context,
                player_input=player_input
            )
            
            # Try to parse as JSON
            try:
                action_data = json.loads(response)
            except json.JSONDecodeError:
                # Fallback to simple interpretation
                logger.error(f"Error interpreting action: {response}", exc_info=True)
                action_data = {
                    "player_input": player_input,
                    "risk_level": "low",
                    "mechanics": [],
                    "needs_roll": False
                }
            
            return action_data
            
        except Exception as e:
            # Fallback interpretation
            return {
                "intent": player_input,
                "risk_level": "unknown",
                "mechanics": [],
                "needs_roll": False,
                "error": str(e)
            }
    
    async def _execute_action(self, game_state: GameState, action_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the interpreted action"""
        
        intent = action_data.get("intent", "").lower()
        logger.debug(f"Executing action with intent: '{intent}'")
        
        # Check for specific action handlers
        for action_type, handler in self.action_handlers.items():
            if action_type in intent:
                logger.info(f"Using specific handler: {action_type}")
                return await handler(game_state, action_data)
        
        # Default: Use AI to generate narrative response
        logger.info("Using general AI handler for action")
        return await self._handle_general_action(game_state, action_data)
    
    async def _handle_explore(self, game_state: GameState, action_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle exploration actions"""
        
        # Generate a location or encounter
        context = ollama.build_game_context(game_state)
        
        narrative = await ollama.generate(
            "world_builder",
            location_type="mysterious location",
            context=context
        )
        
        # Update world data
        current_location = game_state.world_data.get("current_location", "Unknown")
        discovered = game_state.world_data.get("discovered_areas", [])
        if current_location not in discovered:
            discovered.append(current_location)
            game_state.world_data["discovered_areas"] = discovered
        
        return {
            "narrative": narrative,
            "options": ["Investigate further", "Move on", "Rest here"]
        }
    
    async def _handle_travel(self, game_state: GameState, action_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle travel actions"""
        
        # Simple travel system
        current = game_state.world_data.get("current_location", "Starting Area")
        new_location = f"New Area #{len(game_state.world_data.get('discovered_areas', [])) + 1}"
        
        game_state.world_data["current_location"] = new_location
        
        narrative = f"You travel from {current} to {new_location}. The landscape changes around you..."
        
        # Use AI to describe the new area
        context = ollama.build_game_context(game_state)
        description = await ollama.generate(
            "world_builder",
            location_type="travel destination",
            context=context
        )
        
        return {
            "narrative": f"{narrative}\n\n{description}",
            "options": ["Explore the area", "Continue traveling", "Make camp"]
        }
    
    async def _handle_rest(self, game_state: GameState, action_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle rest actions"""
        
        # Simple healing/recovery
        main_char = game_state.get_main_character()
        if main_char:
            # Restore some stats
            for stat in ["VIG", "CLA", "SPI"]:
                current = main_char.get_stat(stat, 10)
                main_char.set_stat(stat, min(current + 2, 20))  # Cap at 20
        
        narrative = "You rest and recover your strength. Your vitality and clarity improve."
        
        return {
            "narrative": narrative,
        }
    
    async def _handle_interact(self, game_state: GameState, action_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle interaction actions"""
        
        context = ollama.build_game_context(game_state)
        
        narrative = await ollama.generate(
            "gamemaster",
            game_state=context,
            player_action=action_data.get("intent", "interact with something")
        )
        
        return {
            "narrative": narrative,
            "options": ["Continue", "Ask questions", "Leave"]
        }
    
    async def _handle_check_status(self, game_state: GameState, action_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle status check actions"""
        
        main_char = game_state.get_main_character()
        if not main_char:
            return {"narrative": "No character found.", "options": []}
        
        status_parts = [
            f"**{main_char.name}**",
            f"Location: {game_state.world_data.get('current_location', 'Unknown')}",
            f"Turn: {game_state.game_data.get('turn_count', 0)}",
            "",
            "**Stats:**"
        ]
        
        for stat, value in main_char.stats.items():
            status_parts.append(f"  {stat}: {value}")
        
        if main_char.inventory:
            status_parts.extend(["", "**Inventory:**"])
            for item in main_char.inventory:
                status_parts.append(f"  - {item}")
        
        narrative = "\n".join(status_parts)
        
        return {
            "narrative": narrative,
            "options": ["Continue", "Rest", "Check surroundings"]
        }
    
    async def _handle_inventory(self, game_state: GameState, action_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle inventory actions"""
        
        main_char = game_state.get_main_character()
        if not main_char or not main_char.inventory:
            narrative = "Your inventory is empty."
        else:
            inventory_list = "\n".join([f"- {item}" for item in main_char.inventory])
            narrative = f"**Inventory:**\n{inventory_list}"
        
        return {
            "narrative": narrative,
            "options": ["Continue", "Use an item", "Drop something"]
        }
    
    async def _handle_general_action(self, game_state: GameState, action_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle general actions using AI"""
        
        context = ollama.build_game_context(game_state)
        
        narrative = await ollama.generate(
            "gamemaster",
            game_state=context,
            player_intent=action_data.get("intent", "do something"),
            player_action = action_data.get("player_input", "")
        )
        
        return {
            "narrative": narrative,
            "options": ["Continue", "Eat shit", "Chase ass"]
        }
    
    def add_action_handler(self, action_type: str, handler_func):
        """Add a custom action handler"""
        self.action_handlers[action_type] = handler_func
    
    def list_sessions(self) -> List[Dict[str, Any]]:
        """List all active sessions"""
        return [
            {
                "session_id": session_id,
                "character": state.get_main_character().name if state.get_main_character() else "Unknown",
                "location": state.world_data.get("current_location", "Unknown"),
                "turn_count": state.game_data.get("turn_count", 0),
                "created_at": state.created_at.isoformat()
            }
            for session_id, state in self.active_sessions.items()
        ]

    def create_session(self, character_name: str) -> str:
        """Create a new game session"""
        session_id = str(uuid.uuid4())
        game_state = create_new_game(session_id, character_name, description="New Player Character")
        self.active_sessions[session_id] = game_state
        logger.info(
            f"Created new session {session_id} for character '{character_name}', total sessions: {len(self.active_sessions)}")
        return session_id

    def get_session(self, session_id: str) -> Optional[GameState]:
        """Get a game session"""
        logger.debug(f"Looking for session {session_id}, available sessions: {list(self.active_sessions.keys())}")
        return self.active_sessions.get(session_id)


# Global instance
game_controller = GameFlowController()
