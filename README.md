# The Living Lands
With each step upon the dry gravel road. The world seems to shake around you. With this you know. you have entered The Living Lands.

You are a Knight of the Realm, sworn to seek out the myths that plague the land and put them to rest with steel and flame.

What is your name - and what myths will you find?

---
### What is this really?

Living Lands is my intepretation of TTRPG Mythic Bastionlands into a digital environment, where npcs, myths, and more is "played" by AI. Can you outwit it? 


Mythic Bastionlands - System Overview

  Core Components

  Frontend (Web Interface)
  ├── game.js - Main state & API communication
  ├── terminal.js - Command input/output
  ├── character-display.js - Character stats UI
  └── index.html - Main game interface

  Backend (FastAPI Server)
  ├── main.py - Server entry point
  ├── api/routes.py - HTTP endpoints
  ├── models.py - Game data structures
  ├── database.py - SQLite persistence
  ├── llm_client.py - Ollama integration
  ├── actions.py - Game mechanics
  ├── combat.py - Combat system
  ├── world.py - Map generation
  └── dice.py - Random mechanics

  External Services
  └── Ollama (LLM) - Narrative generation

  Data Flow

  1. Player Input
     Browser → Terminal → game.js → API

  2. Game Processing
     API → Game Logic → Database → LLM → Response

  3. Output Display
     Response → game.js → Terminal → Browser

  Component Links

  - Frontend ↔ Backend: REST API (/api/v1/command)
  - Backend ↔ Database: SQLAlchemy ORM (SQLite file)
  - Backend ↔ LLM: HTTP requests (Ollama API)
  - Game Logic: Actions → Dice → World → Combat (internal)

  Game Flow

  1. Start: Player opens browser → Auto-creates session
  2. Input: Player types command → Sent to backend
  3. Process: Backend interprets command → Applies game rules
  4. Generate: LLM creates narrative response
  5. Store: Save state to database
  6. Display: Return narrative + game state to frontend
  7. Repeat: Next player command

  Current State

  - ✅ All components exist and connected
  - ✅ Basic command processing works
  - ✅ Database auto-creates sessions
  - ⚠️ LLM integration needs testing
  - ⚠️ Frontend cache issues (use Ctrl+F5)

  Entry Point: python3 start_dev.py → http://localhost:8000
