# The Living Lands
With each step upon the dry gravel road. The world seems to shake around you. With this you know. you have entered The Living Lands.

You are a Knight of the Realm, sworn to seek out the myths that plague the land and put them to rest with steel and flame.

What is your name - and what myths will you find?

---
### What is this really?

Living Lands is my intepretation of TTRPG Mythic Bastionlands into a digital environment, where npcs, myths, and more is "played" by AI. Can you outwit it? 


Mythic Bastionlands - System Overview
Core Components:

  📁 models.py - Simple game state
  - Character - flexible stats, inventory, status
  - GameState - holds characters, world data, action history
  - Easy to extend with new properties

  📁 game/ollama_client.py - Flexible AI integration
  - PromptTemplate system for different scenarios
  - Built-in templates: gamemaster, action_interpreter, world_builder
  - Easy prompt experimentation with /experiment endpoint

  📁 game/flow_controller.py - Game flow management
  - Processes player actions → AI interpretation → game response
  - Pluggable action handlers (explore, travel, rest, etc.)
  - Coordinates between game systems and AI

  📁 api/routes.py - Clean API endpoints
  - /new-game - start sessions
  - /action - process player input
  - /templates - view AI prompts
  - /experiment - test new prompts

  Where to Start Developing:

  1. Game Mechanics → Add handlers in flow_controller.py:_setup_default_handlers()
  2. AI Prompts → Create templates in ollama_client.py or via /experiment endpoint
  3. New Systems → Extend GameState in models.py, add handler functions
  4. Testing Ideas → Use /test-prompt and /experiment endpoints

  Development Flow:

  Player Input → AI Interpretation → Action Handler → Game State Update → AI Response
