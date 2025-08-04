"""models.py - Minimal Game Models for Development

SIMPLE GAME STATE:
- Basic character representation
- Flexible game state storage
- Easy to extend and modify
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime
from backend.game.dice_roller import roll_dice

@dataclass
class Hex:
    """Hex tile for the world map"""
    q: int  # Column coordinate
    r: int  # Row coordinate  
    explored: bool = False
    landscape: str
    landmark: Optional[str] = None
    omen: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "q": self.q,
            "r": self.r,
            "explored": self.explored,
            "landscape": self.landscape,
            "landmark": self.landmark,
            "omen": self.omen,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Hex':
        """Create Hex from dictionary"""
        
        return cls(
            q=data["q"],
            r=data["r"],
            explored=data.get("explored", False),
            landscape=data.get("landscape", "unknown"),
            landmark=data.get("landmark"),
            omen=data.get("omen"),
        )

@dataclass
class Character:
    """Simple character representation"""
    name: str
    description: Optional[str] = None
    player_party: Optional[bool] = None
    # age: Optional[int] = None

    full_vigour: int
    full_clarity: int
    full_spirit: int
    full_guard: int

    vigour: int
    clarity: int
    spirit: int
    guard: int

    fatigued: bool
    feats: List[str]
    scars: List[str]
    inventory: List[str] = field(default_factory=list)
    status: Dict[str, Any] = field(default_factory=dict)  # Wounds, conditions, etc.
    
    def get_stat(self, stat_name: str, default: int = 0) -> int:
        """Get a character stat with default value"""
        stat_map = {
            'vigour': self.vigour, 'clarity': self.clarity, 
            'spirit': self.spirit, 'guard': self.guard
        }
        return stat_map.get(stat_name.lower(), default)
    
    def set_stat(self, stat_name: str, value: int):
        """Set a character stat"""
        if stat_name.lower() == 'vigour':
            self.vigour = value
        elif stat_name.lower() == 'clarity':
            self.clarity = value
        elif stat_name.lower() == 'spirit':
            self.spirit = value
        elif stat_name.lower() == 'guard':
            self.guard = value

@dataclass
class Knight(Character):
    passion: str = ""
    ability: str = ""
    #steed: Optional[str] = None 

@dataclass
class GameState:
    """Flexible game state container"""
    session_id: str
    time_of_day: str
    recent_user_intent: str = field(default_factory=str)
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
    
    def get_current_position(self) -> Tuple[int, int]:
        """Get current hex position as (q, r) tuple"""
        pos = self.world_data.get("position", {"q": 0, "r": 0})
        return (pos["q"], pos["r"])
    
    def set_position(self, q: int, r: int):
        """Set current hex position"""
        self.world_data["position"] = {"q": q, "r": r}
    
    def get_hex(self, q: int, r: int) -> Optional[Hex]:
        """Get hex at coordinates"""
        hex_key = f"{q},{r}"
        hex_data = self.world_data.get("hexes", {}).get(hex_key)
        if hex_data:
            return Hex.from_dict(hex_data)
        return None
    
    def set_hex(self, hex_obj: Hex):
        """Store hex data"""
        hex_key = f"{hex_obj.q},{hex_obj.r}"
        if "hexes" not in self.world_data:
            self.world_data["hexes"] = {}
        self.world_data["hexes"][hex_key] = hex_obj.to_dict()
    
    def mark_hex_explored(self, q: int, r: int):
        """Mark a hex as explored"""
        hex_obj = self.get_hex(q, r)
        if hex_obj:
            hex_obj.explored = True
        else:
            hex_obj = Hex(q=q, r=r, explored=True, landscape="unexplored")
        self.set_hex(hex_obj)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "session_id": self.session_id,
            "characters": [{
                "name": c.name,
                "vigour": c.vigour,
                "clarity": c.clarity,
                "spirit": c.spirit,
                "guard": c.guard,
                "inventory": c.inventory,
                "status": c.status
            } for c in self.characters],
            "world_data": self.world_data,
            "game_data": self.game_data,
            "history": self.history[-10:],  # Last 10 entries only
            "created_at": self.created_at.isoformat()
        }

# Helper functions
def create_knight(name: str, description: str, player_party: bool, stats: Dict[str, int] = None) -> Character:
    """Create a basic character with default stats"""
    # ROLL to select knight - IMPORTANT from set of knights not in world already
    # Get knights special traits: passion, ability, items, ...

    # Roll for stats if not provided
    if stats:
        vigour = stats.get("vigour", roll_dice(12)[0] + roll_dice(6)[0])
        clarity = stats.get("clarity", roll_dice(12)[0] + roll_dice(6)[0])
        spirit = stats.get("spirit", roll_dice(12)[0] + roll_dice(6)[0])
        guard = stats.get("guard", roll_dice(6)[0])
    else:
        vigour = roll_dice(12)[0] + roll_dice(6)[0]
        clarity = roll_dice(12)[0] + roll_dice(6)[0]
        spirit = roll_dice(12)[0] + roll_dice(6)[0]
        guard = roll_dice(6)[0]
    
    return Character(
        name=name,
        description=description,
        player_party=player_party,
        full_vigour=vigour,
        full_clarity=clarity,
        full_spirit=spirit,
        full_guard=guard,
        vigour=vigour,
        clarity=clarity,
        spirit=spirit,
        guard=guard,
        fatigued=False,
        feats=[],
        scars=[],
        inventory=["basic gear"],
        status={"wounds": 0, "conditions": []}
    )

def create_new_game(session_id: str, character_name: str, description: str) -> GameState:
    """Create a new game session"""
    character = create_knight(character_name, description, player_party=True)
    
    # Create starting hex
    starting_hex = Hex(q=0, r=0, explored=True, landscape="starting_area")
    
    game_state = GameState(
        session_id=session_id,
        characters=[character],
        time_of_day='morning',
        recent_user_intent='',
        world_data={
            "current_location": "Starting Area", 
            "discovered_areas": [],
            "position": {"q": 0, "r": 0},  # Starting hex position
            "hexes": {"0,0": starting_hex.to_dict()}  # Initialize with starting hex
        },
        game_data={"turn_count": 0, "active_events": []}
    )
    
    return game_state
