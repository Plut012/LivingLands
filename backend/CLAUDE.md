Architecture Plan
Backend: FastAPI + SQLite + Ollama

FastAPI for the API layer (clean, fast, great docs)
SQLite for game state (simple, serverless, perfect for single-player adventures)
Ollama for LLM calls (you already have this working)

Frontend: Simple Web Interface

Pure HTML/CSS/JavaScript or lightweight framework like Alpine.js
Focus on readability and atmosphere over flashy UI
Terminal/book aesthetic would fit the game perfectly

Key Components:

Game State Manager - tracks character virtues, inventory, location, company status
Action Processor - handles the 5-step action procedure from the rules
Dice System - manages all rolls (saves, luck rolls, damage, etc.)
World Generator - creates hexes, myths, omens using the exploration rules
Combat Engine - handles the detailed combat mechanics
Referee AI - uses LLM to interpret rules and generate narrative

Database Schema (Simple):

Characters (virtues, guard, equipment, scars)
Game Sessions (current state, location, active myths)
World State (discovered hexes, active omens, company relationships)

This keeps it simple but robust - you can start with core mechanics and gradually add the richer systems like warfare, travel, and myth generation. The beauty is that Mythic Bastionlands' systems are modular, so you can implement them incrementally.
Would you like me to elaborate on any of these components or discuss the data models for the game state?
