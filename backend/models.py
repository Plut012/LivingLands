"""models.py - Minimal Game Models for Development

SIMPLE GAME STATE:
- Basic character representation
- Flexible game state storage
- Easy to extend and modify
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime

@dataclass
class Character:
    """Simple character representation"""
    name: str
    stats: Dict[str, int] = field(default_factory=dict)  # Flexible stats (VIG, CLA, SPI, etc.)
    inventory: List[str] = field(default_factory=list)
    status: Dict[str, Any] = field(default_factory=dict)  # Wounds, conditions, etc.
    
    def get_stat(self, stat_name: str, default: int = 0) -> int:
        """Get a character stat with default value"""
        return self.stats.get(stat_name, default)
    
    def set_stat(self, stat_name: str, value: int):
        """Set a character stat"""
        self.stats[stat_name] = value

@dataclass
class GameState:
    """Flexible game state container"""
    session_id: str
    characters: List[Character] = field(default_factory=list)
    world_data: Dict[str, Any] = field(default_factory=dict)  # Current location, discovered areas, etc.
    game_data: Dict[str, Any] = field(default_factory=dict)   # Turn count, active events, etc.
    history: List[Dict[str, Any]] = field(default_factory=list)  # Action history for context
    created_at: datetime = field(default_factory=datetime.now)
    
    def add_history_entry(self, action: str, result: str, context: Dict[str, Any] = None):
        """Add an entry to the game history"""
        entry = {
            "action": action,
            "result": result,
            "context": context or {},
            "timestamp": datetime.now()
        }
        self.history.append(entry)
    
    def get_main_character(self) -> Optional[Character]:
        """Get the first character (main character)"""
        return self.characters[0] if self.characters else None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "session_id": self.session_id,
            "characters": [{
                "name": c.name,
                "stats": c.stats,
                "inventory": c.inventory,
                "status": c.status
            } for c in self.characters],
            "world_data": self.world_data,
            "game_data": self.game_data,
            "history": self.history[-10:],  # Last 10 entries only
            "created_at": self.created_at.isoformat()
        }

# Helper functions
def create_basic_character(name: str, stats: Dict[str, int] = None) -> Character:
    """Create a basic character with default stats"""
    default_stats = {"VIG": 10, "CLA": 10, "SPI": 10, "GD": 5}
    if stats:
        default_stats.update(stats)
    
    return Character(
        name=name,
        stats=default_stats,
        inventory=["basic gear"],
        status={"wounds": 0, "conditions": []}
    )

def create_new_game(session_id: str, character_name: str) -> GameState:
    """Create a new game session"""
    character = create_basic_character(character_name)
    
    return GameState(
        session_id=session_id,
        characters=[character],
        world_data={"current_location": "Starting Area", "discovered_areas": []},
        game_data={"turn_count": 0, "active_events": []}
    )