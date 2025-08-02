"""
dice.py - Dice Rolling System for Mythic Bastionlands

PLAN:
1. Basic dice rolling functions (d6, d20)
2. Save roll mechanics
3. Luck roll with outcome categories
4. Damage roll calculations
5. Scar table implementation

FRAMEWORK:
- Use random module for dice
- Return structured results (value + context)
- Keep functions pure and testable
"""

import random
from enum import Enum
from typing import List, Tuple, Dict

# STEP 1: Define outcome enums
class LuckOutcome(Enum):
    CRISIS = "crisis"  # 1
    PROBLEM = "problem"  # 2-3
    BLESSING = "blessing"  # 4-6

class ScarType(Enum):
    DISTRESS = "distress"
    DISFIGUREMENT = "disfigurement"
    SMASH = "smash"
    STUN = "stun"
    RUPTURE = "rupture"
    GOUGE = "gouge"
    CONCUSSION = "concussion"
    TEAR = "tear"
    AGONY = "agony"
    MUTILATION = "mutilation"
    DOOM = "doom"
    HUMILIATION = "humiliation"

# STEP 2: Basic dice rolling functions
def roll_d6() -> int:
    """Roll a single d6"""
    return random.randint(1, 6)

def roll_d20() -> int:
    """Roll a single d20"""
    return random.randint(1, 20)

def roll_multiple(dice_count: int, dice_type: int = 6) -> List[int]:
    """Roll multiple dice of the same type"""
    return [random.randint(1, dice_type) for _ in range(dice_count)]

# STEP 3: Save roll mechanics
def make_save(virtue_score: int, difficulty: int = 0) -> Tuple[bool, int]:
    """
    Make a save roll - roll d20 <= virtue score
    Returns (success, roll_value)
    """
    roll = roll_d20()
    # Apply difficulty as penalty to virtue score
    target = virtue_score - difficulty
    success = roll <= target
    return success, roll

# STEP 4: Luck roll system
def luck_roll() -> Tuple[LuckOutcome, int]:
    """
    Make a luck roll on d6
    1: Crisis (immediately bad)
    2-3: Problem (potentially bad)
    4-6: Blessing (welcome result)
    """
    roll = roll_d6()
    if roll == 1:
        outcome = LuckOutcome.CRISIS
    elif roll <= 3:
        outcome = LuckOutcome.PROBLEM
    else:
        outcome = LuckOutcome.BLESSING
    return outcome, roll

# STEP 5: Damage roll calculations
def damage_roll(base_damage: str, bonus_dice: int = 0) -> int:
    """
    Roll damage dice
    base_damage: string like "d6", "d8", "2d6", "d10"
    bonus_dice: additional d8s from Bolster
    """
    # Parse base damage string
    if 'd' not in base_damage:
        return int(base_damage)  # Fixed damage
    
    # Extract number of dice and die type
    parts = base_damage.split('d')
    num_dice = int(parts[0]) if parts[0] else 1
    die_type = int(parts[1])
    
    # Roll base damage
    total = sum(roll_multiple(num_dice, die_type))
    
    # Add bonus d8s
    if bonus_dice > 0:
        total += sum(roll_multiple(bonus_dice, 8))
    
    return total

# STEP 6: Scar table implementation
def scar_roll() -> Tuple[ScarType, Dict[str, any]]:
    """
    Roll on the scar table when taking damage at 0 GD
    Returns scar type and its effects
    """
    roll = roll_d6() + roll_d6()  # 2d6
    
    # STEP 6.1: Map roll to scar type
    scar_table = {
        2: (ScarType.DISTRESS, {"lose_gd": 6, "effect": "lucky escape"}),
        3: (ScarType.DISFIGUREMENT, {"permanent": True, "location": random.choice(["Eye", "Cheek", "Neck", "Torso", "Nose", "Jaw"])}),
        4: (ScarType.SMASH, {"lose_gd": 6, "lose_vig": True}),
        5: (ScarType.STUN, {"lose_gd": 6, "effect": "pain drowns senses"}),
        6: (ScarType.RUPTURE, {"lose_gd": 12, "lose_vig": True}),
        7: (ScarType.GOUGE, {"lose_gd": 6, "effect": "flesh torn from bone"}),
        8: (ScarType.CONCUSSION, {"lose_gd": 12, "lose_cla": True}),
        9: (ScarType.TEAR, {"permanent": True, "location": random.choice(["Nose", "Ear", "Finger", "Thumb", "Eye", "Scalp"])}),
        10: (ScarType.AGONY, {"lose_gd": 12, "lose_spi": True}),
        11: (ScarType.MUTILATION, {"permanent": True, "location": random.choice(["Leg", "Shield Arm", "Sword Arm"])}),
        12: (ScarType.DOOM, {"effect": "death haunts you", "mortal_wound": True}),
    }
    
    # Handle rolls outside normal range
    if roll < 2:
        roll = 2
    elif roll > 12:
        roll = 12
        
    scar_type, effects = scar_table[roll]
    return scar_type, effects

# STEP 7: Attack roll helper
def attack_roll(num_dice: int, impaired: bool = False) -> List[int]:
    """
    Roll attack dice
    If impaired, roll only d4s
    """
    if impaired:
        return roll_multiple(num_dice, 4)
    else:
        return roll_multiple(num_dice, 6)

# STEP 8: Combat damage calculation
def calculate_damage(attack_dice: List[int], armor: int = 0) -> int:
    """
    Calculate damage from attack dice
    Takes highest die, subtracts armor
    """
    if not attack_dice:
        return 0
    
    damage = max(attack_dice) - armor
    return max(0, damage)  # Can't do negative damage
