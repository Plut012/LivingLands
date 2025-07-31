// PLAN:
// 1. Initialize application state
// 2. Set up API communication
// 3. Coordinate between modules
// 4. Handle session persistence
// 5. Main game loop

// Step 1: Game State Management
const GameState = {
    // Current game session
    sessionId: null,
    currentLocation: { x: 0, y: 0 },
    
    // Character state
    character: {
        name: '',
        virtues: {
            vigour: 0,
            clarity: 0,
            spirit: 0
        },
        guard: 0,
        wounds: [],
        equipment: [],
        abilities: []
    },
    
    // World state
    exploredHexes: new Set(),
    currentMythId: null,
    omensRevealed: [],
    
    // UI state
    terminalHistory: [],
    activeTab: null
};

// Step 2: API Communication Layer
const API = {
    baseUrl: '/api',
    
    async sendCommand(command) {
        try {
            const response = await fetch(`${this.baseUrl}/command`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    sessionId: GameState.sessionId,
                    command: command
                })
            });
            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            return { error: 'Connection failed' };
        }
    },
    
    async startSession() {
        try {
            const response = await fetch(`${this.baseUrl}/session/start`, {
                method: 'POST'
            });
            const data = await response.json();
            GameState.sessionId = data.sessionId;
            return data;
        } catch (error) {
            console.error('Session start error:', error);
            return { error: 'Failed to start session' };
        }
    },
    
    async saveSession() {
        try {
            await fetch(`${this.baseUrl}/session/save`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(GameState)
            });
        } catch (error) {
            console.error('Save error:', error);
        }
    }
};

// Step 3: Module Coordination
const ModuleManager = {
    modules: {},
    
    register(name, module) {
        this.modules[name] = module;
    },
    
    initialize() {
        // Initialize all registered modules
        Object.values(this.modules).forEach(module => {
            if (module.init) module.init(GameState);
        });
    },
    
    broadcast(event, data) {
        // Send events to all modules
        Object.values(this.modules).forEach(module => {
            if (module.handleEvent) module.handleEvent(event, data);
        });
    }
};

// Step 4: Session Persistence
const SessionManager = {
    autoSaveInterval: 60000, // 1 minute
    
    async load() {
        const saved = localStorage.getItem('mythic-bastionlands-session');
        if (saved) {
            try {
                const data = JSON.parse(saved);
                Object.assign(GameState, data);
                return true;
            } catch (e) {
                console.error('Failed to load session:', e);
            }
        }
        return false;
    },
    
    save() {
        localStorage.setItem('mythic-bastionlands-session', JSON.stringify(GameState));
        API.saveSession();
    },
    
    startAutoSave() {
        setInterval(() => this.save(), this.autoSaveInterval);
    }
};

// Step 5: Main Game Loop
const Game = {
    initialized: false,
    
    async init() {
        console.log('Initializing Mythic Bastionlands...');
        
        // Load saved session or start new
        const hasSession = await SessionManager.load();
        if (!hasSession) {
            await API.startSession();
        }
        
        // Initialize modules
        ModuleManager.initialize();
        
        // Start autosave
        SessionManager.startAutoSave();
        
        // Initial render
        this.render();
        
        // Mark as initialized
        this.initialized = true;
        
        // Show welcome message
        ModuleManager.broadcast('terminal:output', {
            text: 'Welcome to the Mythic Bastionlands...',
            style: 'dramatic'
        });
    },
    
    render() {
        // Update all visual components
        ModuleManager.broadcast('render', GameState);
    },
    
    async processCommand(command) {
        // Add to history
        GameState.terminalHistory.push({ type: 'input', text: command });
        
        // Send to API
        const response = await API.sendCommand(command);
        
        // Process response
        if (response.error) {
            ModuleManager.broadcast('terminal:output', {
                text: response.error,
                style: 'error'
            });
        } else {
            // Update game state
            if (response.stateChanges) {
                this.updateState(response.stateChanges);
            }
            
            // Display response
            if (response.output) {
                ModuleManager.broadcast('terminal:output', response.output);
            }
            
            // Trigger any special effects
            if (response.effects) {
                response.effects.forEach(effect => {
                    ModuleManager.broadcast(`effect:${effect.type}`, effect.data);
                });
            }
        }
        
        // Re-render
        this.render();
    },
    
    updateState(changes) {
        // Deep merge state changes
        Object.keys(changes).forEach(key => {
            if (typeof changes[key] === 'object' && !Array.isArray(changes[key])) {
                GameState[key] = { ...GameState[key], ...changes[key] };
            } else {
                GameState[key] = changes[key];
            }
        });
    }
};

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    Game.init();
});

// Export for other modules
window.Game = Game;
window.GameState = GameState;
window.ModuleManager = ModuleManager;
