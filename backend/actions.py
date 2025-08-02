"""
actions.py - Action Resolution System for Mythic Bastionlands

PLAN:
1. Define action structure (Intent, Leverage, Cost, Risk)
2. Process actions through the resolution system
3. Determine outcomes based on success/failure
4. Apply consequences to characters
5. Check for virtue loss conditions

FRAMEWORK:
- Follow the game's action procedure strictly
- Keep outcomes clearly defined
- Track consequences and side effects
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict, List, Tuple
from models import Character, VirtueType

# STEP 1: Define action enums and structures
class ActionOutcome(Enum):
    ADVANCE = "advance"  # Move in good direction
    DISRUPT = "disrupt"  # Lessen a threat
    RESOLVE = "resolve"  # Put problem to rest
    THREATEN = "threaten"  # Create new problem
    ESCALATE = "escalate"  # Make problem worse
    EXECUTE = "execute"  # Deliver on threat

class RiskLevel(Enum):
    NO_RISK = "no_risk"
    SAVE = "save"
    LUCK_ROLL = "luck_roll"

@dataclass
class Action:
    """Player action with all components"""
    intent: str  # What are you trying to do?
    leverage: str  # What makes it possible?
    cost: Optional[str] = None  # Resource, cause virtue loss, or side-effect?
    risk: RiskLevel = RiskLevel.NO_RISK  # What's at risk?

@dataclass
class ActionResult:
    """Result of processing an action"""
    success: bool
    outcome: ActionOutcome
    narrative: str
    consequences: Dict[str, any] = None
    virtue_loss: Optional[Tuple[VirtueType, int]] = None

# STEP 2: Process action through resolution system
def process_action(action: Action, character: Character, roll_result: Optional[Tuple[bool, int]] = None) -> ActionResult:
    """
    Process an action following the game's procedure
    roll_result: Optional (success, roll_value) from save/luck roll
    """
    # STEP 2.1: Check if action has risk
    if action.risk == RiskLevel.NO_RISK:
        # No risk = automatic success
        return ActionResult(
            success=True,
            outcome=determine_success_outcome(action),
            narrative=f"You {action.intent} successfully.",
            consequences=apply_cost(action.cost)
        )
    
    # STEP 2.2: Handle risky actions
    if action.risk == RiskLevel.SAVE:
        # Player made a save roll
        if roll_result and roll_result[0]:  # Success
            return ActionResult(
                success=True,
                outcome=determine_success_outcome(action),
                narrative=f"You succeed at {action.intent}.",
                consequences=apply_cost(action.cost)
            )
        else:  # Failure
            return ActionResult(
                success=False,
                outcome=determine_failure_outcome(action),
                narrative=f"You fail to {action.intent}.",
                consequences={"negative_impact": True}
            )
    
    # STEP 2.3: Handle luck roll actions
    if action.risk == RiskLevel.LUCK_ROLL:
        # This would integrate with dice.py luck_roll()
        return ActionResult(
            success=True,  # Luck rolls always "complete"
            outcome=ActionOutcome.ADVANCE,  # Placeholder
            narrative="The whims of fate decide...",
            consequences={"requires_luck_roll": True}
        )

# STEP 3: Determine success outcomes
def determine_success_outcome(action: Action) -> ActionOutcome:
    """Determine which positive outcome applies"""
    # Simple keyword matching for now
    intent_lower = action.intent.lower()
    
    if any(word in intent_lower for word in ["solve", "fix", "heal", "restore"]):
        return ActionOutcome.RESOLVE
    elif any(word in intent_lower for word in ["weaken", "reduce", "lessen", "distract"]):
        return ActionOutcome.DISRUPT
    else:
        return ActionOutcome.ADVANCE

# STEP 4: Determine failure outcomes
def determine_failure_outcome(action: Action) -> ActionOutcome:
    """Determine which negative outcome applies"""
    # Context would determine this - simplified for now
    intent_lower = action.intent.lower()
    
    if any(word in intent_lower for word in ["attack", "fight", "strike"]):
        return ActionOutcome.EXECUTE
    elif any(word in intent_lower for word in ["sneak", "hide", "avoid"]):
        return ActionOutcome.THREATEN
    else:
        return ActionOutcome.ESCALATE

# STEP 5: Apply action costs
def apply_cost(cost: Optional[str]) -> Dict[str, any]:
    """Process the cost of an action"""
    if not cost:
        return {}
    
    consequences = {}
    cost_lower = cost.lower()
    
    # Check for resource costs
    if "coin" in cost_lower or "gold" in cost_lower:
        consequences["spend_resource"] = "coins"
    elif "fatigue" in cost_lower:
        consequences["fatigue"] = True
    elif "virtue" in cost_lower:
        # This triggers virtue loss check
        consequences["check_virtue_loss"] = True
    
    return consequences

# STEP 6: Apply consequences to character
def apply_consequences(result: ActionResult, character: Character) -> None:
    """Apply the results of an action to a character"""
    if not result.consequences:
        return
    
    # STEP 6.1: Handle fatigue
    if result.consequences.get("fatigue"):
        # In full game, this would reduce effectiveness
        pass
    
    # STEP 6.2: Handle virtue loss
    if result.virtue_loss:
        virtue_type, amount = result.virtue_loss
        current = character.virtues[virtue_type]
        character.virtues[virtue_type] = max(0, current - amount)
    
    # STEP 6.3: Handle negative impacts
    if result.consequences.get("negative_impact"):
        # This would trigger appropriate game effects
        pass

# STEP 7: Check for virtue loss conditions
def check_virtue_loss(action_type: str, character: Character) -> Optional[Tuple[VirtueType, int]]:
    """
    Check if an action should cause virtue loss
    Returns (virtue_type, amount) or None
    """
    # Simplified rules for virtue loss
    action_lower = action_type.lower()
    
    # Actions that might reduce Vigour
    if any(word in action_lower for word in ["exhaust", "overexert", "push limits"]):
        return (VirtueType.VIGOUR, 1)
    
    # Actions that might reduce Clarity  
    elif any(word in action_lower for word in ["confuse", "overwhelm", "panic"]):
        return (VirtueType.CLARITY, 1)
    
    # Actions that might reduce Spirit
    elif any(word in action_lower for word in ["despair", "betray", "abandon"]):
        return (VirtueType.SPIRIT, 1)
    
    return None

# STEP 8: Helper function to check virtue status
def get_virtue_status(character: Character) -> Dict[str, str]:
    """Check for exhausted/exposed/impaired conditions"""
    status = {}
    
    if character.virtues[VirtueType.VIGOUR] == 0:
        status["exhausted"] = "Cannot attack if moved this turn"
    
    if character.virtues[VirtueType.CLARITY] == 0:
        status["exposed"] = "Treated as 0 GD"
    
    if character.virtues[VirtueType.SPIRIT] == 0:
        status["impaired"] = "Attacks roll d4 only"
    
    return status

# STEP 9: Create action from player input
def create_action(intent: str, leverage: str, has_cost: bool = False, 
                 is_risky: bool = False) -> Action:
    """Helper to create an action from components"""
    risk = RiskLevel.SAVE if is_risky else RiskLevel.NO_RISK
    cost = "Resources or effort" if has_cost else None
    
    return Action(
        intent=intent,
        leverage=leverage,
        cost=cost,
        risk=risk
    )
