"""
models.py - Core Game Models for Mythic Bastionlands

PLAN:
1. Define Character class with virtues, guard, equipment
2. Define Company class to manage knights and squires
3. Define WorldHex class for map locations
4. Define GameSession class for game state
5. Define CombatState class for active fights

FRAMEWORK:
- Use dataclasses for clean, simple data structures
- Keep relationships simple (lists, dictionaries)
- Focus on core attributes only
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum

# STEP 1: Define basic enums for game constants
class VirtueType(Enum):
    VIGOUR = "VIG"
    CLARITY = "CLA"
    SPIRIT = "SPI"

class WeaponType(Enum):
    HEFTY = "hefty"
    LONG = "long"
    HAND = "hand"

# STEP 2: Define Character class
@dataclass
class Character:
    """Represents a Knight or Squire"""
    name: str
    virtues: Dict[VirtueType, int]  # VIG, CLA, SPI values
    guard: int  # GD value
    max_guard: int
    equipment: List[str] = field(default_factory=list)
    wounds: List[str] = field(default_factory=list)  # Current wounds/scars
    is_knight: bool = True
    
    def __post_init__(self):
        # STEP 2.1: Validate virtues are within range 0-19
        for virtue, value in self.virtues.items():
            if not 0 <= value <= 19:
                raise ValueError(f"{virtue.value} must be between 0 and 19")

# STEP 3: Define Company class
@dataclass
class Company:
    """A group of Knights (and possibly Squires)"""
    name: str
    knights: List[Character] = field(default_factory=list)
    squires: List[Character] = field(default_factory=list)
    
    def get_all_members(self) -> List[Character]:
        """Return all company members"""
        return self.knights + self.squires

# STEP 4: Define WorldHex class
@dataclass
class WorldHex:
    """A hex on the game map"""
    coordinates: Tuple[int, int]  # (x, y) hex coordinates
    landmark: Optional[str] = None
    myth_id: Optional[int] = None
    current_omen: int = 0  # Which omen is active (0-6)
    explored: bool = False
    
    def has_myth(self) -> bool:
        """Check if this hex contains a myth"""
        return self.myth_id is not None

# STEP 5: Define GameSession class
@dataclass
class GameSession:
    """Current game state"""
    session_id: str
    company: Company
    current_hex: Tuple[int, int]
    world_hexes: Dict[Tuple[int, int], WorldHex] = field(default_factory=dict)
    active_combat: Optional['CombatState'] = None
    turn_count: int = 0
    
    def get_current_hex(self) -> WorldHex:
        """Get the hex the company is currently in"""
        return self.world_hexes.get(self.current_hex)

# STEP 6: Define CombatState class
@dataclass
class CombatState:
    """Active combat encounter"""
    combatants: List[Dict]  # List of all fighters with stats
    initiative_order: List[int] = field(default_factory=list)  # Indices into combatants
    current_turn: int = 0
    round_number: int = 1
    
    def get_active_combatant(self) -> Dict:
        """Get the current acting combatant"""
        if self.initiative_order:
            return self.combatants[self.initiative_order[self.current_turn]]
        return None

# STEP 7: Simple factory functions
def create_knight(name: str, vig: int, cla: int, spi: int, gd: int) -> Character:
    """Create a new Knight character"""
    return Character(
        name=name,
        virtues={
            VirtueType.VIGOUR: vig,
            VirtueType.CLARITY: cla,
            VirtueType.SPIRIT: spi
        },
        guard=gd,
        max_guard=gd,
        is_knight=True
    )

def create_squire(name: str) -> Character:
    """Create a new Squire with fixed stats"""
    return Character(
        name=name,
        virtues={
            VirtueType.VIGOUR: 7,
            VirtueType.CLARITY: 7,
            VirtueType.SPIRIT: 2
        },
        guard=6,
        max_guard=6,
        is_knight=False,
        equipment=["dagger", "torches", "rope"]
    )
