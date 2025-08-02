"""
world.py - World Generation System for Mythic Bastionlands

PLAN:
1. Hex generation with landmarks
2. Myth placement and omen tracking
3. Wilderness roll encounters
4. Landmark generation
5. Travel and exploration mechanics

FRAMEWORK:
- Use hexagonal coordinate system
- Keep world state persistent
- Generate content procedurally
"""

from typing import Tuple, Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import random
from models import WorldHex

# STEP 1: Define world enums
class LandmarkType(Enum):
    RUIN = "ruin"
    FOREST = "forest"
    RIVER = "river"
    MOUNTAIN = "mountain"
    SETTLEMENT = "settlement"
    CAVE = "cave"
    TOWER = "tower"
    BRIDGE = "bridge"

class WildernessResult(Enum):
    NEXT_OMEN = "next_omen"
    LANDMARK = "landmark"
    CLEAR = "clear"

@dataclass
class Myth:
    """A myth with its omens"""
    id: int
    name: str
    description: str
    omens: List[str]  # 6 omens in order
    location: Tuple[int, int]  # Hex coordinates

# STEP 2: Hex generation
def generate_hex(coordinates: Tuple[int, int], 
                force_landmark: bool = False) -> WorldHex:
    """Generate a new hex with potential features"""
    hex = WorldHex(coordinates=coordinates)
    
    # STEP 2.1: Chance of landmark
    if force_landmark or random.random() < 0.3:  # 30% chance
        hex.landmark = generate_landmark()
    
    # STEP 2.2: Chance of myth (rarer)
    if random.random() < 0.1:  # 10% chance
        hex.myth_id = random.randint(1, 12)  # 12 myths in game
    
    return hex

# STEP 3: Place myth in world
def place_myth(world_hexes: Dict[Tuple[int, int], WorldHex], 
               myth: Myth) -> bool:
    """Place a myth at specific coordinates"""
    coords = myth.location
    
    # Create hex if doesn't exist
    if coords not in world_hexes:
        world_hexes[coords] = generate_hex(coords)
    
    # Place myth
    world_hexes[coords].myth_id = myth.id
    world_hexes[coords].current_omen = 1  # First omen active
    
    return True

# STEP 4: Trigger next omen
def trigger_omen(hex: WorldHex, myth_library: Dict[int, Myth]) -> Optional[str]:
    """
    Advance to next omen for a myth
    Returns the omen text or None if no myth/all omens done
    """
    if not hex.myth_id or hex.current_omen >= 6:
        return None
    
    myth = myth_library.get(hex.myth_id)
    if not myth:
        return None
    
    # Get current omen
    omen_text = myth.omens[hex.current_omen - 1]
    
    # Advance to next
    hex.current_omen += 1
    
    return omen_text

# STEP 5: Wilderness roll
def check_wilderness_roll() -> Tuple[WildernessResult, int]:
    """
    Roll d6 for wilderness encounters
    1: Next omen from random realm
    2-3: Next omen from nearest myth  
    4-6: Encounter hex's landmark (or clear)
    """
    roll = random.randint(1, 6)
    
    if roll == 1:
        return WildernessResult.NEXT_OMEN, roll
    elif roll <= 3:
        return WildernessResult.NEXT_OMEN, roll
    else:
        return WildernessResult.LANDMARK, roll

# STEP 6: Generate landmarks
def generate_landmark() -> str:
    """Generate a random landmark"""
    landmark_types = [
        "Ancient ruins of a fallen tower",
        "Dense forest with twisted paths",
        "Swift river with treacherous crossing",
        "Steep mountain pass",
        "Small village clinging to survival",
        "Dark cave mouth yawning open",
        "Crumbling watchtower",
        "Stone bridge over a chasm"
    ]
    
    return random.choice(landmark_types)

# STEP 7: Get adjacent hexes
def get_adjacent_hexes(coords: Tuple[int, int]) -> List[Tuple[int, int]]:
    """
    Get all 6 adjacent hex coordinates
    Using offset coordinates for hexagonal grid
    """
    x, y = coords
    
    # Even row
    if y % 2 == 0:
        adjacent = [
            (x-1, y-1), (x, y-1),    # NW, NE
            (x-1, y),   (x+1, y),    # W, E
            (x-1, y+1), (x, y+1)     # SW, SE
        ]
    # Odd row
    else:
        adjacent = [
            (x, y-1),   (x+1, y-1),  # NW, NE
            (x-1, y),   (x+1, y),    # W, E
            (x, y+1),   (x+1, y+1)   # SW, SE
        ]
    
    return adjacent

# STEP 8: Find nearest myth
def find_nearest_myth(current_hex: Tuple[int, int], 
                     world_hexes: Dict[Tuple[int, int], WorldHex]) -> Optional[Tuple[int, int]]:
    """Find the nearest hex containing a myth"""
    # Simple breadth-first search
    visited = set()
    queue = [current_hex]
    
    while queue:
        coords = queue.pop(0)
        if coords in visited:
            continue
            
        visited.add(coords)
        
        # Check if this hex has a myth
        hex = world_hexes.get(coords)
        if hex and hex.myth_id and hex.current_omen <= 6:
            return coords
        
        # Add adjacent hexes to search
        for adj in get_adjacent_hexes(coords):
            if adj not in visited:
                queue.append(adj)
    
    return None

# STEP 9: Initialize game world
def initialize_world() -> Dict[Tuple[int, int], WorldHex]:
    """Create the starting game world"""
    world = {}
    
    # Create starting hex
    start = (0, 0)
    world[start] = generate_hex(start, force_landmark=True)
    
    # Create some nearby hexes
    for coords in get_adjacent_hexes(start):
        world[coords] = generate_hex(coords)
    
    return world

# STEP 10: Travel mechanics
def travel_cost(method: str, distance: int) -> Dict[str, any]:
    """
    Calculate travel costs
    Trek: 1 hex on foot
    Gallop: 2 hexes on steed (steed loses d6 VIG)
    Cruise: 3 hexes by boat/road
    """
    costs = {
        "time": "1 phase",  # Always takes a phase
        "method": method
    }
    
    if method == "trek":
        costs["max_distance"] = 1
        
    elif method == "gallop":
        costs["max_distance"] = 2
        costs["steed_damage"] = "d6 VIG"
        
    elif method == "cruise":
        costs["max_distance"] = 3
        costs["requires"] = "boat or road"
    
    return costs

# STEP 11: Create myth library
def create_myth_library() -> Dict[int, Myth]:
    """Create the 12 myths referenced in the game"""
    # Simplified version - full game would have detailed myths
    myths = {}
    
    for i in range(1, 13):
        myths[i] = Myth(
            id=i,
            name=f"Myth {i}",
            description=f"Ancient tale of myth {i}",
            omens=[f"Omen {j} of myth {i}" for j in range(1, 7)],
            location=(random.randint(-5, 5), random.randint(-5, 5))
        )
    
    return myths

# STEP 12: Exploration action
def explore_hex(hex: WorldHex, company_size: int) -> Dict[str, any]:
    """
    Explore a hex to search for features
    Takes a whole phase
    """
    result = {
        "time_cost": "1 phase",
        "found": []
    }
    
    # Search roll based on company size
    search_bonus = min(company_size, 3)  # Max +3
    roll = random.randint(1, 6) + search_bonus
    
    if roll >= 5:  # Success
        if hex.landmark:
            result["found"].append(("landmark", hex.landmark))
        if hex.myth_id:
            result["found"].append(("myth", hex.myth_id))
    
    # Mark as explored
    hex.explored = True
    
    return result
