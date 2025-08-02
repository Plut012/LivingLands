# Mythic Bastionlands - Development Setup

## Quick Start

1. **Install Ollama** (if not already installed):
   ```bash
   # Download from https://ollama.ai/download
   # Or on Linux/Mac:
   curl -fsSL https://ollama.ai/install.sh | sh
   ```

2. **Start Ollama and pull model**:
   ```bash
   ollama serve
   ollama pull llama3.2
   ```

3. **Start the development server**:
   ```bash
   python start_dev.py
   ```

4. **Open your browser**:
   - Game: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - API Status: http://localhost:8000/api/status

## What This Sets Up

- **Backend**: FastAPI server with SQLite database
- **Frontend**: Static web interface served by FastAPI
- **LLM**: Ollama integration for narrative generation
- **CORS**: Configured for local development
- **Auto-reload**: Backend restarts on code changes

## Testing the Setup

1. Visit http://localhost:8000 - should show the game interface
2. Check http://localhost:8000/api/status - should return API info
3. Test Ollama: http://localhost:8000/docs and try the endpoints

## Troubleshooting

- **Port 8000 busy**: Change port in `start_dev.py`
- **Ollama connection failed**: Ensure `ollama serve` is running
- **Import errors**: Run `pip install -r backend/requirements.txt`
- **Database errors**: Delete `backend/mythic_bastionlands.db` to reset

## Development Workflow

1. Backend code changes trigger auto-reload
2. Frontend changes need browser refresh
3. Database persists between restarts
4. Logs show in terminal

## Architecture

```
├── backend/           # FastAPI application
│   ├── api/          # API routes
│   ├── main.py       # App entry point
│   ├── models.py     # Game data models
│   ├── database.py   # SQLite integration
│   └── llm_client.py # Ollama connection
├── frontend/         # Web interface
└── start_dev.py      # Development launcher
```