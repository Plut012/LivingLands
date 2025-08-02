"""
llm_client.py - LLM Integration for Mythic Bastionlands

PLAN:
1. Setup LLM client wrapper
2. Create prompts for narrative generation
3. Interpret player commands into game actions
4. Generate atmospheric descriptions
5. Maintain context and game state

FRAMEWORK:
- Use simple prompt templates
- Keep context focused and relevant
- Parse LLM responses safely
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import json
import requests
from models import GameSession, Character, WorldHex
from actions import Action, ActionOutcome

class LLMClient:
    """Wrapper for Ollama API calls"""
    def __init__(self, base_url: str = None, model: str = "tohur:latest"):
        # Auto-detect if running in WSL and connect to Windows host
        if base_url is None:
            try:
                with open('/etc/resolv.conf', 'r') as f:
                    for line in f:
                        if 'nameserver' in line:
                            host_ip = line.split()[1]
                            base_url = f"http://{host_ip}:11434"
                            break
                if base_url is None:
                    base_url = "http://localhost:11434"  # fallback
            except:
                base_url = "http://localhost:11434"  # fallback
        
        self.base_url = base_url
        self.model = model
    
    def complete(self, prompt: str, max_tokens: int = 500) -> str:
        """Send prompt to Ollama and get response"""
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "num_predict": max_tokens,
                        "temperature": 0.7
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "No response from LLM")
            else:
                return f"Error: Ollama API returned {response.status_code}"
                
        except requests.exceptions.RequestException as e:
            return f"Connection error: {str(e)}. Is Ollama running?"
        except json.JSONDecodeError:
            return "Error: Invalid response from Ollama"

# STEP 2: Context management
@dataclass
class GameContext:
    """Maintains conversation context"""
    session_id: str
    recent_actions: List[str]  # Last 5 actions
    current_scene: str
    character_states: Dict[str, Dict]
    world_info: str
    
    def to_prompt(self) -> str:
        """Convert context to prompt format"""
        return f"""
Current Scene: {self.current_scene}
Recent Actions: {', '.join(self.recent_actions[-3:])}
Party Status: {json.dumps(self.character_states, indent=2)}
World Context: {self.world_info}
"""

# STEP 3: Prompt templates
class PromptTemplates:
    """Reusable prompt templates"""
    
    INTERPRET_ACTION = """
You are the referee for Mythic Bastionlands, a medieval fantasy game.
A player wants to: "{player_input}"

{context}

Parse this into game terms:
- Intent: What are they trying to do?
- Leverage: What makes it possible?
- Cost: Any resources or consequences?
- Risk: Is there risk? (No risk, Save required, or Luck roll)

Respond in JSON format:
{{"intent": "...", "leverage": "...", "cost": "...", "risk": "..."}}
"""
    
    DESCRIBE_OUTCOME = """
You are narrating Mythic Bastionlands. 
Action: {action}
Outcome: {outcome}
Details: {details}

{context}

Write a brief (2-3 sentence) atmospheric description of what happens.
Keep it dark medieval fantasy. Focus on concrete details.
"""
    
    DESCRIBE_LOCATION = """
You are describing a location in Mythic Bastionlands.
Hex contains: {features}
Time: {time}
Weather: {weather}

Write a brief (2-3 sentence) description of what the knights see.
Medieval dark fantasy tone. Focus on atmosphere and potential danger.
"""

# Global client instance
llm_client = LLMClient()

# STEP 4: Send prompt with context
def send_prompt(context: GameContext, action: Action, 
                rules_reference: str) -> str:
    """
    Send contextualized prompt to LLM
    Returns narrative response
    """
    # Build the prompt
    prompt = PromptTemplates.DESCRIBE_OUTCOME.format(
        action=f"{action.intent} using {action.leverage}",
        outcome="Success" if action.risk else "Automatic success",
        details=rules_reference,
        context=context.to_prompt()
    )
    
    # Get LLM response
    response = llm_client.complete(prompt)
    
    # Update context
    context.recent_actions.append(action.intent)
    if len(context.recent_actions) > 5:
        context.recent_actions.pop(0)
    
    return response

# STEP 5: Generate narrative for outcomes
def generate_narrative(game_state: GameSession, 
                      outcome: ActionOutcome,
                      details: Dict = None) -> str:
    """Generate narrative text for a game outcome"""
    
    # Build context from game state
    context = build_context(game_state)
    
    # Map outcome to narrative guidance
    narrative_hints = {
        ActionOutcome.ADVANCE: "progress toward goal",
        ActionOutcome.DISRUPT: "weaken the threat", 
        ActionOutcome.RESOLVE: "solve the problem",
        ActionOutcome.THREATEN: "new danger emerges",
        ActionOutcome.ESCALATE: "situation worsens",
        ActionOutcome.EXECUTE: "threat strikes"
    }
    
    prompt = PromptTemplates.DESCRIBE_OUTCOME.format(
        action="Recent action",
        outcome=outcome.value,
        details=narrative_hints.get(outcome, ""),
        context=context.to_prompt()
    )
    
    return llm_client.complete(prompt)

# STEP 6: Interpret player input
def interpret_player_input(raw_command: str, 
                          context: GameContext) -> Dict[str, str]:
    """
    Parse player's natural language into game action
    Returns dict with intent, leverage, cost, risk
    """
    prompt = PromptTemplates.INTERPRET_ACTION.format(
        player_input=raw_command,
        context=context.to_prompt()
    )
    
    # Get LLM interpretation
    response = llm_client.complete(prompt, max_tokens=200)
    
    # Parse JSON response safely
    try:
        parsed = json.loads(response)
        # Validate required fields
        required = ["intent", "leverage", "cost", "risk"]
        if all(field in parsed for field in required):
            return parsed
    except:
        pass
    
    # Fallback if parsing fails
    return {
        "intent": raw_command,
        "leverage": "your skills and equipment",
        "cost": None,
        "risk": "no_risk"
    }

# STEP 7: Create atmospheric descriptions
def create_atmospheric_text(situation: str, 
                           details: Dict = None) -> str:
    """Generate atmospheric text for various situations"""
    
    situation_prompts = {
        "combat_start": "Knights draw steel as danger emerges...",
        "exploration": "The company ventures into unknown lands...",
        "camp": "Night falls and the knights make camp...",
        "myth_encounter": "Ancient power stirs in this place..."
    }
    
    base_description = situation_prompts.get(situation, "")
    
    if details:
        # Enhance with specific details
        if "weather" in details:
            base_description += f" {details['weather']}."
        if "landmark" in details:
            base_description += f" {details['landmark']} looms ahead."
    
    return base_description

# STEP 8: Build context from game state
def build_context(game_state: GameSession) -> GameContext:
    """Extract relevant context from game state"""
    
    # Get character states
    char_states = {}
    for knight in game_state.company.knights:
        char_states[knight.name] = {
            "guard": knight.guard,
            "wounds": len(knight.wounds),
            "virtues": {k.value: v for k, v in knight.virtues.items()}
        }
    
    # Get current location info
    current_hex = game_state.get_current_hex()
    world_info = "Unknown territory"
    if current_hex:
        if current_hex.landmark:
            world_info = f"Near {current_hex.landmark}"
        elif current_hex.explored:
            world_info = "Familiar territory"
    
    return GameContext(
        session_id=game_state.session_id,
        recent_actions=[],
        current_scene="Exploration",
        character_states=char_states,
        world_info=world_info
    )

# STEP 9: Generate location descriptions
def describe_location(hex: WorldHex, time_of_day: str = "day",
                     weather: str = "clear") -> str:
    """Generate description for a hex location"""
    
    features = []
    if hex.landmark:
        features.append(hex.landmark)
    if hex.myth_id:
        features.append("an aura of ancient power")
    if not hex.explored:
        features.append("unexplored wilderness")
    
    prompt = PromptTemplates.DESCRIBE_LOCATION.format(
        features=", ".join(features) if features else "empty wilderness",
        time=time_of_day,
        weather=weather
    )
    
    return llm_client.complete(prompt, max_tokens=150)

# STEP 10: Validate and sanitize LLM outputs
def sanitize_response(response: str, max_length: int = 500) -> str:
    """Clean and validate LLM responses"""
    # Remove any potential prompt injection
    response = response.strip()
    
    # Truncate if too long
    if len(response) > max_length:
        response = response[:max_length] + "..."
    
    # Remove any JSON or code blocks
    if "```" in response:
        response = response.split("```")[0]
    
    return response
