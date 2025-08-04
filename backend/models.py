"""models.py - Minimal Game Models for Development

SIMPLE GAME STATE:
- Basic character representation
- Flexible game state storage
- Easy to extend and modify
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime
from enum import Enum
from backend.game.dice_roller import roll_dice

class TerrainType(Enum):
    """Terrain types from the Mythic Bastionlands rules"""
    MARSH = "marsh"
    HEATH = "heath"
    CRAG = "crag"
    PEAKS = "peaks"
    FOREST = "forest"
    VALLEY = "valley"
    HILLS = "hills"
    MEADOW = "meadow"
    BOG = "bog"
    LAKE = "lake"
    GLADE = "glade"
    PLAINS = "plains"

class LandmarkType(Enum):
    """Landmark types from the rules"""
    DWELLING = "dwelling"
    SANCTUM = "sanctum"
    MONUMENT = "monument"
    HAZARD = "hazard"
    CURSE = "curse"
    RUINS = "ruins"
    HOLDING = "holding"  # Castles, towns, fortresses

class MythType(Enum):
    """The 6 Myths from Mythic Bastionlands"""
    GOBLIN = "goblin"
    HERALD = "herald"
    PRISONER = "prisoner"
    TYRANT = "tyrant"
    DRAGON = "dragon"
    SLEEPER = "sleeper"

@dataclass
class Barrier:
    """Represents a barrier between two adjacent hexes"""
    hex1: tuple[int, int]  # (q, r) coordinates of first hex
    hex2: tuple[int, int]  # (q, r) coordinates of second hex
    barrier_type: str = "impassable"  # Type of barrier (cliff, wall, etc.)
    description: Optional[str] = None
    
    def __post_init__(self):
        """Ensure consistent ordering of hex coordinates"""
        if self.hex1 > self.hex2:
            self.hex1, self.hex2 = self.hex2, self.hex1
    
    def blocks_travel(self, from_hex: tuple[int, int], to_hex: tuple[int, int]) -> bool:
        """Check if this barrier blocks travel between two hexes"""
        ordered_from, ordered_to = (from_hex, to_hex) if from_hex <= to_hex else (to_hex, from_hex)
        return (ordered_from, ordered_to) == (self.hex1, self.hex2)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "hex1": self.hex1,
            "hex2": self.hex2,
            "barrier_type": self.barrier_type,
            "description": self.description
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Barrier':
        """Create Barrier from dictionary"""
        return cls(
            hex1=tuple(data["hex1"]),
            hex2=tuple(data["hex2"]),
            barrier_type=data.get("barrier_type", "impassable"),
            description=data.get("description")
        )

@dataclass
class Hex:
    """Hex tile for the world map"""
    q: int  # Column coordinate (axial coordinates)
    r: int  # Row coordinate (axial coordinates)
    terrain: TerrainType
    explored: bool = False
    landmark: Optional[LandmarkType] = None
    landmark_name: Optional[str] = None
    landmark_description: Optional[str] = None
    myth: Optional[MythType] = None
    myth_name: Optional[str] = None
    omen_encountered: bool = False
    current_omen: int = 1  # Which omen (1-6) is currently active
    river: bool = False  # Part of river system
    
    def __post_init__(self):
        """Validate hex data after initialization"""
        if not isinstance(self.terrain, TerrainType):
            raise ValueError(f"terrain must be a TerrainType, got {type(self.terrain)}")
    
    @property
    def display_name(self) -> str:
        """Get display name for the hex"""
        if self.landmark_name:
            return f"{self.landmark_name} ({self.terrain.value.title()})"
        elif self.myth_name:
            return f"{self.myth_name} ({self.terrain.value.title()})"
        else:
            return self.terrain.value.title()
    
    @property
    def is_wilderness(self) -> bool:
        """Check if this hex is wilderness (no holding)"""
        return self.landmark != LandmarkType.HOLDING
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "q": self.q,
            "r": self.r,
            "terrain": self.terrain.value,
            "explored": self.explored,
            "landmark": self.landmark.value if self.landmark else None,
            "landmark_name": self.landmark_name,
            "landmark_description": self.landmark_description,
            "myth": self.myth.value if self.myth else None,
            "myth_name": self.myth_name,
            "omen_encountered": self.omen_encountered,
            "current_omen": self.current_omen,
            "river": self.river
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Hex':
        """Create Hex from dictionary"""
        terrain = TerrainType(data["terrain"])
        landmark = LandmarkType(data["landmark"]) if data.get("landmark") else None
        myth = MythType(data["myth"]) if data.get("myth") else None
        
        return cls(
            q=data["q"],
            r=data["r"],
            terrain=terrain,
            explored=data.get("explored", False),
            landmark=landmark,
            landmark_name=data.get("landmark_name"),
            landmark_description=data.get("landmark_description"),
            myth=myth,
            myth_name=data.get("myth_name"),
            omen_encountered=data.get("omen_encountered", False),
            current_omen=data.get("current_omen", 1),
            river=data.get("river", False)
        )

@dataclass
class Character:
    """Simple character representation"""
    name: str
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
    description: Optional[str] = None
    player_party: Optional[bool] = None
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
            hex_obj = Hex(q=q, r=r, explored=True, terrain=TerrainType.PLAINS)
        self.set_hex(hex_obj)
    
    def get_barriers(self) -> List[Barrier]:
        """Get all barriers in the world"""
        barrier_data = self.world_data.get("barriers", [])
        return [Barrier.from_dict(b) for b in barrier_data]
    
    def set_barriers(self, barriers: List[Barrier]):
        """Store barriers data"""
        self.world_data["barriers"] = [b.to_dict() for b in barriers]
    
    def can_travel_between(self, from_coords: tuple[int, int], to_coords: tuple[int, int]) -> bool:
        """Check if travel between two adjacent hexes is possible"""
        barriers = self.get_barriers()
        for barrier in barriers:
            if barrier.blocks_travel(from_coords, to_coords):
                return False
        return True

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
    starting_hex = Hex(q=0, r=0, explored=True, terrain=TerrainType.MEADOW)
    
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

# Utility functions for hex map operations
class HexMap:
    """Container for hex-based map operations"""
    
    def __init__(self, hexes: List[Hex], barriers: List[Barrier] = None):
        self.hexes = {(hex.q, hex.r): hex for hex in hexes}
        self.barriers = barriers or []
    
    def get_hex(self, q: int, r: int) -> Optional[Hex]:
        """Get hex at coordinates"""
        return self.hexes.get((q, r))
    
    def get_neighbors(self, q: int, r: int) -> List[Hex]:
        """Get neighboring hexes (axial coordinates)"""
        directions = [(1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1)]
        neighbors = []
        for dq, dr in directions:
            neighbor = self.get_hex(q + dq, r + dr)
            if neighbor:
                neighbors.append(neighbor)
        return neighbors
    
    def get_accessible_neighbors(self, q: int, r: int) -> List[Hex]:
        """Get neighboring hexes that can be traveled to (not blocked by barriers)"""
        neighbors = self.get_neighbors(q, r)
        accessible = []
        
        for neighbor in neighbors:
            if self.can_travel_between((q, r), (neighbor.q, neighbor.r)):
                accessible.append(neighbor)
        
        return accessible
    
    def can_travel_between(self, from_coords: tuple[int, int], to_coords: tuple[int, int]) -> bool:
        """Check if travel between two adjacent hexes is possible (not blocked by barriers)"""
        if not (self.get_hex(*from_coords) and self.get_hex(*to_coords)):
            return False
        
        for barrier in self.barriers:
            if barrier.blocks_travel(from_coords, to_coords):
                return False
        
        return True
    
    def get_barriers_from_hex(self, q: int, r: int) -> List[tuple[Barrier, tuple[int, int]]]:
        """Get all barriers adjacent to a hex and the hex they block travel to"""
        hex_coord = (q, r)
        barriers_info = []
        
        for barrier in self.barriers:
            if barrier.hex1 == hex_coord:
                barriers_info.append((barrier, barrier.hex2))
            elif barrier.hex2 == hex_coord:
                barriers_info.append((barrier, barrier.hex1))
        
        return barriers_info
    
    def get_myths(self) -> List[Hex]:
        """Get all hexes containing myths"""
        return [hex for hex in self.hexes.values() if hex.myth]
    
    def get_holdings(self) -> List[Hex]:
        """Get all hexes containing holdings"""
        return [hex for hex in self.hexes.values() 
                if hex.landmark == LandmarkType.HOLDING]

def create_sample_realm() -> tuple[List[Hex], List[Barrier]]:
    """Create a sample realm based on the provided sketch"""
    hexes = []
    
    # Row 1 (top)
    hexes.extend([
        Hex(0, 0, TerrainType.BOG, landmark=LandmarkType.HAZARD, 
            landmark_name="Cursed Mire", 
            landmark_description="A treacherous bog where lights dance at night"),
        Hex(1, 0, TerrainType.CRAG, myth=MythType.GOBLIN,
            myth_name="The Goblin's Lost Domain"),
        Hex(2, 0, TerrainType.PEAKS,
            landmark=LandmarkType.RUINS,
            landmark_name="Broken Crown Keep",
            landmark_description="Ancient fortress ruins crown this peak"),
        Hex(3, 0, TerrainType.FOREST),
        Hex(4, 0, TerrainType.FOREST, myth=MythType.HERALD,
            myth_name="The Whispering Grove"),
    ])
    
    # Row 2
    hexes.extend([
        Hex(-1, 1, TerrainType.MARSH, river=True),
        Hex(0, 1, TerrainType.HEATH, myth=MythType.SLEEPER,
            myth_name="The Sleeping Stone Circle"),
        Hex(1, 1, TerrainType.VALLEY, river=True,
            landmark=LandmarkType.DWELLING,
            landmark_name="Miller's Crossing",
            landmark_description="A humble mill by the river"),
        Hex(2, 1, TerrainType.HILLS),
        Hex(3, 1, TerrainType.LAKE, river=True,
            landmark=LandmarkType.MONUMENT,
            landmark_name="The Drowned Statue",
            landmark_description="Ancient statue rises from lake waters"),
        Hex(4, 1, TerrainType.GLADE),
    ])
    
    # Row 3 (middle)
    hexes.extend([
        Hex(-1, 2, TerrainType.MARSH, river=True),
        Hex(0, 2, TerrainType.MEADOW, 
            landmark=LandmarkType.HOLDING,
            landmark_name="Thornwick",
            landmark_description="A fortified village surrounded by thorn hedges"),
        Hex(1, 2, TerrainType.PLAINS, river=True),
        Hex(2, 2, TerrainType.VALLEY, myth=MythType.PRISONER,
            myth_name="The Chained Valley"),
        Hex(3, 2, TerrainType.PLAINS),
        Hex(4, 2, TerrainType.MEADOW,
            landmark=LandmarkType.SANCTUM,
            landmark_name="Shrine of the Dawn",
            landmark_description="A peaceful shrine tended by a hermit seer"),
    ])
    
    # Row 4
    hexes.extend([
        Hex(-1, 3, TerrainType.PLAINS),
        Hex(0, 3, TerrainType.HILLS,
            landmark=LandmarkType.RUINS,
            landmark_name="The Tumbled Towers",
            landmark_description="Mysterious ruins of an ancient watchtower"),
        Hex(1, 3, TerrainType.PLAINS, river=True),
        Hex(2, 3, TerrainType.LAKE, river=True,
            myth=MythType.DRAGON,
            myth_name="Deepwater's Claim"),
        Hex(3, 3, TerrainType.PLAINS,
            landmark=LandmarkType.HOLDING,
            landmark_name="Ironhold",
            landmark_description="A trading post built around an old iron mine"),
        Hex(4, 3, TerrainType.HILLS),
    ])
    
    # Row 5 (bottom)
    hexes.extend([
        Hex(0, 4, TerrainType.PLAINS,
            landmark=LandmarkType.CURSE,
            landmark_name="The Barren Circle",
            landmark_description="A perfectly circular patch where nothing grows"),
        Hex(1, 4, TerrainType.MEADOW),
        Hex(2, 4, TerrainType.PLAINS, myth=MythType.TYRANT,
            myth_name="The Tyrant's Road",
            landmark=LandmarkType.RUINS,
            landmark_name="Broken Crown Road",
            landmark_description="Ancient stone road leading to nowhere"),
        Hex(3, 4, TerrainType.HEATH,
            landmark=LandmarkType.DWELLING,
            landmark_name="Heather Hall",
            landmark_description="A lonely inn at the crossroads"),
        Hex(4, 4, TerrainType.VALLEY),
    ])
    
    # Define barriers between specific hexes
    barriers = [
        # Mountain barriers around the peaks
        Barrier((2, 0), (2, 1), "cliff face", "Steep cliffs block passage"),
        Barrier((2, 0), (3, 0), "rockfall", "Recent rockfall blocks the path"),
        Barrier((1, 0), (2, 0), "chasm", "A deep chasm splits the mountainside"),
        
        # Bog barriers (treacherous terrain)
        Barrier((0, 0), (0, 1), "quagmire", "Impassable bog waters"),
        
        # Forest barriers (dense thickets)
        Barrier((3, 0), (4, 0), "thornwall", "Impenetrable wall of thorns"),
        
        # Magical barriers near myths
        Barrier((0, 1), (1, 1), "spectral wall", "Ghostly barrier from the Stone Circle"),
        Barrier((2, 2), (3, 2), "chain ward", "Mystical chains block passage"),
    ]
    
    return hexes, barriers

def create_new_game_with_sample_realm(session_id: str, character_name: str, description: str) -> GameState:
    """Create a new game session with the sample realm"""
    character = create_knight(character_name, description, player_party=True)
    
    # Create sample realm
    hexes, barriers = create_sample_realm()
    
    # Convert hexes to dict format for storage
    hexes_dict = {}
    for hex_obj in hexes:
        hex_key = f"{hex_obj.q},{hex_obj.r}"
        hexes_dict[hex_key] = hex_obj.to_dict()
    
    # Start at Thornwick (0, 2) - a safe holding
    starting_pos = {"q": 0, "r": 2}
    
    game_state = GameState(
        session_id=session_id,
        characters=[character],
        time_of_day='morning',
        recent_user_intent='',
        world_data={
            "current_location": "Thornwick", 
            "discovered_areas": [],
            "position": starting_pos,
            "hexes": hexes_dict,
            "barriers": [b.to_dict() for b in barriers]
        },
        game_data={"turn_count": 0, "active_events": []}
    )
    
    # Mark starting hex and immediate neighbors as explored
    game_state.mark_hex_explored(0, 2)
    game_state.mark_hex_explored(0, 1)  # Stone Circle (visible from Thornwick)
    game_state.mark_hex_explored(1, 2)  # Plains (visible from Thornwick)
    
    return game_state
