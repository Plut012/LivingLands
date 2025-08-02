"""ollama_client.py - Flexible Ollama Integration

FLEXIBLE PROMPT CONSTRUCTION:
- Modular prompt templates
- Context builders for different scenarios
- Easy to experiment with different approaches
"""

import requests
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

@dataclass
class PromptTemplate:
    """A reusable prompt template"""
    name: str
    system_prompt: str
    user_template: str
    variables: List[str] = field(default_factory=list)
    
    def render(self, **kwargs) -> tuple[str, str]:
        """Render the template with provided variables"""
        rendered_user = self.user_template
        for var, value in kwargs.items():
            rendered_user = rendered_user.replace(f"{{{var}}}", str(value))
        
        return self.system_prompt, rendered_user

class OllamaClient:
    """Flexible Ollama client for game interactions"""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3.1"):
        self.base_url = base_url
        self.model = model
        self.templates = {}
        self._load_default_templates()
    
    def _load_default_templates(self):
        """Load default prompt templates"""
        
        # Game Master template for general narrative
        self.templates["gamemaster"] = PromptTemplate(
            name="gamemaster",
            system_prompt="""You are the Game Master for Mythic Bastionland, a dark fantasy RPG. 
You control the world, NPCs, and consequences of player actions.
Be descriptive but concise. Focus on atmosphere and meaningful choices.
Always end with what the player can do next.""",
            user_template="""GAME STATE:
{game_state}

PLAYER ACTION: {player_action}

Describe what happens and present 2-3 meaningful options for what the player can do next.""",
            variables=["game_state", "player_action"]
        )
        
        # Action interpreter template
        self.templates["action_interpreter"] = PromptTemplate(
            name="action_interpreter",
            system_prompt="""You are an action interpreter for a text RPG. 
Parse player input and determine:
1. What they want to do (intent)
2. How risky it is (low/medium/high)
3. What game mechanics might apply

Respond in JSON format only.""",
            user_template="""CURRENT SITUATION: {situation}
PLAYER INPUT: {player_input}

Analyze this action and respond with JSON:
{
    "intent": "clear description of what player wants to do",
    "risk_level": "low/medium/high",
    "mechanics": ["list", "of", "relevant", "game", "mechanics"],
    "needs_roll": true/false
}""",
            variables=["situation", "player_input"]
        )
        
        # World builder template
        self.templates["world_builder"] = PromptTemplate(
            name="world_builder",
            system_prompt="""You create atmospheric locations and encounters for Mythic Bastionland.
The world is dark, strange, and full of fallen industry and ancient mysteries.
Focus on evocative details that suggest larger stories.""",
            user_template="""Create a {location_type} that the player discovers.
Current context: {context}
Make it mysterious and atmospheric, with potential for interaction.""",
            variables=["location_type", "context"]
        )
    
    def add_template(self, template: PromptTemplate):
        """Add a custom prompt template"""
        self.templates[template.name] = template
    
    def get_template(self, name: str) -> Optional[PromptTemplate]:
        """Get a prompt template by name"""
        return self.templates.get(name)
    
    def list_templates(self) -> List[str]:
        """List available template names"""
        return list(self.templates.keys())
    
    async def generate(self, template_name: str, **kwargs) -> str:
        """Generate text using a template"""
        template = self.get_template(template_name)
        if not template:
            raise ValueError(f"Template '{template_name}' not found")
        
        system_prompt, user_prompt = template.render(**kwargs)
        return await self._call_ollama(system_prompt, user_prompt)
    
    async def generate_raw(self, system_prompt: str, user_prompt: str) -> str:
        """Generate text with raw prompts (no template)"""
        return await self._call_ollama(system_prompt, user_prompt)
    
    async def _call_ollama(self, system_prompt: str, user_prompt: str) -> str:
        """Make the actual API call to Ollama"""
        try:
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "stream": False
            }
            
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            return result["message"]["content"]
            
        except requests.exceptions.RequestException as e:
            return f"Error communicating with Ollama: {e}"
        except Exception as e:
            return f"Unexpected error: {e}"
    
    def build_game_context(self, game_state: Any) -> str:
        """Build context string from game state for prompts"""
        context_parts = []
        
        # Character info
        main_char = game_state.get_main_character()
        if main_char:
            context_parts.append(f"Character: {main_char.name}")
            if main_char.stats:
                stats_str = ", ".join([f"{k}:{v}" for k, v in main_char.stats.items()])
                context_parts.append(f"Stats: {stats_str}")
            if main_char.inventory:
                context_parts.append(f"Inventory: {', '.join(main_char.inventory)}")
        
        # World info
        world_data = game_state.world_data
        if world_data.get("current_location"):
            context_parts.append(f"Location: {world_data['current_location']}")
        
        # Recent history
        if game_state.history:
            recent = game_state.history[-3:]  # Last 3 actions
            history_str = " → ".join([h["action"] for h in recent])
            context_parts.append(f"Recent: {history_str}")
        
        return "\n".join(context_parts)
    
    def create_prompt_experiment(self, name: str, system: str, user: str, variables: List[str]):
        """Quick way to create and test new prompt templates"""
        template = PromptTemplate(
            name=f"experiment_{name}",
            system_prompt=system,
            user_template=user,
            variables=variables
        )
        self.add_template(template)
        return template

# Global instance for easy access
ollama = OllamaClient()