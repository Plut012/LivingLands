"""
combat.py - Combat System for Mythic Bastionlands

PLAN:
1. Initiative and turn order
2. Attack resolution with damage calculation
3. Damage application and wound tracking
4. Feat system (Smite, Focus, Deny)
5. Gambit resolution for special attacks

FRAMEWORK:
- Follow the specific combat procedure
- Handle group attacks (multiple vs single target)
- Track combat state throughout encounter
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from models import Character, CombatState
import dice

# STEP 1: Define combat enums
class FeatType(Enum):
    SMITE = "smite"  # +d12 or Blast
    FOCUS = "focus"  # Gambit without die, Save or Fatigue
    DENY = "deny"   # Rebuff attack

class GambitEffect(Enum):
    BOLSTER = "bolster"  # +1 damage
    MOVE = "move"  # Move after attack
    REPEL = "repel"  # Push foe away
    STOP = "stop"  # Stop foe from moving
    IMPAIR = "impair"  # Impair weapon next turn
    TRAP = "trap"  # Trap shield
    DISMOUNT = "dismount"  # Dismount foe
    OTHER = "other"  # Custom effect

@dataclass
class Combatant:
    """A participant in combat"""
    name: str
    character: Optional[Character]  # None for NPCs
    vigor: int  # Current VIG
    clarity: int  # Current CLA
    guard: int  # Current GD
    armor: int  # Armor reduction
    weapons: List[Dict[str, any]]  # Weapon stats
    is_player: bool = True
    has_moved: bool = False

# STEP 2: Initiative and turn order
def initiative_order(combatants: List[Combatant]) -> List[int]:
    """
    Determine turn order for combat
    Players act first in any order they choose
    """
    player_indices = []
    enemy_indices = []
    
    for i, combatant in enumerate(combatants):
        if combatant.is_player:
            player_indices.append(i)
        else:
            enemy_indices.append(i)
    
    # Players first, then enemies
    return player_indices + enemy_indices

# STEP 3: Process attack
def process_attack(attacker: Combatant, target: Combatant, 
                  weapon: Dict[str, any], allies_attacking: int = 0) -> Dict[str, any]:
    """
    Process a single attack following game rules
    allies_attacking: number of other allies also attacking this target
    """
    result = {
        "attacker": attacker.name,
        "target": target.name,
        "dice_rolled": [],
        "damage": 0,
        "description": ""
    }
    
    # STEP 3.1: Determine number of attack dice
    base_dice = weapon.get("damage_dice", 1)
    
    # Check if attacker is impaired (SPI 0)
    impaired = attacker.character and attacker.character.virtues.get("SPI", 1) == 0
    
    # STEP 3.2: Roll attack dice
    if impaired:
        result["dice_rolled"] = dice.roll_multiple(base_dice, 4)  # d4s only
        result["description"] = "Impaired attack (d4s)"
    else:
        result["dice_rolled"] = dice.roll_multiple(base_dice, 6)  # Normal d6s
    
    # STEP 3.3: Take highest die
    if result["dice_rolled"]:
        highest = max(result["dice_rolled"])
        
        # STEP 3.4: Apply armor reduction
        damage = highest - target.armor
        result["damage"] = max(0, damage)
    
    return result

# STEP 4: Apply damage
def apply_damage(target: Combatant, damage: int) -> Dict[str, any]:
    """Apply damage to a target, checking for wounds"""
    result = {
        "damage_taken": damage,
        "guard_remaining": target.guard,
        "wounded": False,
        "mortal_wound": False,
        "scar": None
    }
    
    # STEP 4.1: Deduct from Guard
    target.guard -= damage
    result["guard_remaining"] = target.guard
    
    # STEP 4.2: Check for wounds
    if target.guard < 0:
        # Exceeded guard - wounded
        result["wounded"] = True
        
        if target.guard <= -target.vigor:
            # Mortal wound
            result["mortal_wound"] = True
        
        # Roll for scar if at 0 GD
        if target.is_player and target.guard <= 0:
            scar_type, effects = dice.scar_roll()
            result["scar"] = {
                "type": scar_type.value,
                "effects": effects
            }
    
    elif target.guard == 0:
        # Exactly 0 - potential scar
        if target.is_player:
            scar_type, effects = dice.scar_roll()
            result["scar"] = {
                "type": scar_type.value,
                "effects": effects
            }
    
    return result

# STEP 5: Check and apply feats
def check_feats(character: Character, feat_type: FeatType, fatigued: bool = False) -> bool:
    """
    Check if a character can use a feat
    Feats can only be used once per attack by each combatant
    """
    # In full implementation, track feat usage per combat
    
    if feat_type == FeatType.SMITE:
        # Must be done before rolling attack
        return not fatigued
    
    elif feat_type == FeatType.FOCUS:
        # Can be used after rolling attack
        # Requires SPI save or become fatigued
        return True
    
    elif feat_type == FeatType.DENY:
        # Used after being attacked
        # Requires CLA save or become fatigued
        return True
    
    return False

def apply_feat(feat_type: FeatType, attack_result: Dict = None) -> Dict[str, any]:
    """Apply the effects of a feat"""
    effects = {}
    
    if feat_type == FeatType.SMITE:
        # Add d12 damage die or make attack Blast
        effects["bonus_dice"] = 12  # Roll d12
        effects["or_blast"] = True  # Can choose Blast instead
    
    elif feat_type == FeatType.FOCUS:
        # Perform gambit without using die
        effects["free_gambit"] = True
        effects["requires_save"] = ("SPI", "or_fatigue")
    
    elif feat_type == FeatType.DENY:
        # Can use after attack roll
        effects["options"] = [
            "discard_one_die",
            "pass_spi_save_or_fatigue"
        ]
    
    return effects

# STEP 6: Resolve gambits
def resolve_gambits(dice_results: List[int], target_number: int = 4) -> List[GambitEffect]:
    """
    Check attack dice for gambits (4+)
    Each die of target_number or higher can trigger one gambit effect
    """
    gambit_count = sum(1 for die in dice_results if die >= target_number)
    
    # Return list of available gambit slots
    return [None] * gambit_count  # Player chooses effects

def apply_gambit(effect: GambitEffect, attacker: Combatant, 
                target: Combatant = None) -> Dict[str, any]:
    """Apply a chosen gambit effect"""
    result = {"effect": effect.value}
    
    if effect == GambitEffect.BOLSTER:
        result["damage_bonus"] = 1
        
    elif effect == GambitEffect.MOVE:
        attacker.has_moved = False  # Can move again
        result["can_move"] = True
        
    elif effect == GambitEffect.REPEL:
        result["push_target"] = True
        
    elif effect == GambitEffect.STOP:
        if target:
            target.has_moved = True  # Can't move next turn
        result["target_stopped"] = True
        
    elif effect == GambitEffect.IMPAIR:
        result["target_impaired_next_turn"] = True
        
    elif effect == GambitEffect.TRAP:
        result["shield_trapped"] = True
        
    elif effect == GambitEffect.DISMOUNT:
        result["target_dismounted"] = True
        result["bonus_damage"] = 6  # d6 falling damage
    
    return result

# STEP 7: Handle group combat
def resolve_group_attack(attackers: List[Combatant], target: Combatant, 
                        weapons: List[Dict]) -> Dict[str, any]:
    """
    Resolve multiple attackers vs single target
    All roll simultaneously, take highest + bonuses
    """
    all_dice = []
    
    # Everyone rolls their attack dice
    for i, attacker in enumerate(attackers):
        weapon = weapons[i]
        num_dice = weapon.get("damage_dice", 1)
        
        # Check impairment
        impaired = attacker.character and attacker.character.virtues.get("SPI", 1) == 0
        
        if impaired:
            dice_rolled = dice.roll_multiple(num_dice, 4)
        else:
            dice_rolled = dice.roll_multiple(num_dice, 6)
        
        all_dice.extend(dice_rolled)
    
    # Take highest die
    highest = max(all_dice) if all_dice else 0
    
    # Calculate damage
    damage = highest - target.armor
    
    return {
        "attackers": [a.name for a in attackers],
        "all_dice": all_dice,
        "highest_die": highest,
        "damage": max(0, damage),
        "gambit_dice": sum(1 for d in all_dice if d >= 4)
    }

# STEP 8: Combat state management
def start_combat(player_characters: List[Character], 
                enemies: List[Dict]) -> CombatState:
    """Initialize combat with all combatants"""
    combatants = []
    
    # Add player characters
    for pc in player_characters:
        combatants.append(Combatant(
            name=pc.name,
            character=pc,
            vigor=pc.virtues.get("VIG", 10),
            clarity=pc.virtues.get("CLA", 10),
            guard=pc.guard,
            armor=0,  # Would check equipment
            weapons=[{"type": "sword", "damage_dice": 1}],
            is_player=True
        ))
    
    # Add enemies
    for enemy in enemies:
        combatants.append(Combatant(
            name=enemy["name"],
            character=None,
            vigor=enemy.get("vig", 5),
            clarity=enemy.get("cla", 5),
            guard=enemy.get("gd", 0),
            armor=enemy.get("armor", 0),
            weapons=enemy.get("weapons", [{"type": "claw", "damage_dice": 1}]),
            is_player=False
        ))
    
    # Create combat state
    combat = CombatState(
        combatants=[c.__dict__ for c in combatants],
        initiative_order=initiative_order(combatants)
    )
    
    return combat

# STEP 9: Check morale
def check_morale(combatants: List[Combatant]) -> List[str]:
    """
    Check if any groups need morale saves
    Triggered when wounded or half numbers lost
    """
    routing = []
    
    # Group combatants by side
    player_count = sum(1 for c in combatants if c.is_player and c.guard > 0)
    enemy_count = sum(1 for c in combatants if not c.is_player and c.guard > 0)
    
    # Check if any group lost half members
    # (Would need to track original counts in full implementation)
    
    return routing
