// PLAN:
// 1. Command input handling
// 2. Typewriter text animation
// 3. Command history management
// 4. Text parsing and formatting
// 5. Dramatic text reveal system

const Terminal = {
    // Step 1: Core elements and state
    elements: {
        output: null,
        input: null,
        inputLine: null
    },
    
    history: [],
    historyIndex: -1,
    currentAnimation: null,
    
    // Step 2: Initialization
    init(gameState) {
        this.elements.output = document.getElementById('terminal-output');
        this.elements.input = document.getElementById('terminal-input');
        
        // Set up event listeners
        this.setupInputHandlers();
        
        // Register with module manager
        window.ModuleManager.register('terminal', this);
    },
    
    // Step 3: Input handling
    setupInputHandlers() {
        this.elements.input.addEventListener('keydown', (e) => {
            switch(e.key) {
                case 'Enter':
                    this.handleCommand();
                    break;
                case 'ArrowUp':
                    e.preventDefault();
                    this.navigateHistory(-1);
                    break;
                case 'ArrowDown':
                    e.preventDefault();
                    this.navigateHistory(1);
                    break;
            }
        });
    },
    
    handleCommand() {
        const command = this.elements.input.value.trim();
        if (!command) return;
        
        // Add to history
        this.history.push(command);
        this.historyIndex = this.history.length;
        
        // Clear input
        this.elements.input.value = '';
        
        // Display command
        this.addLine(`> ${command}`, 'command');
        
        // Process through game controller
        window.Game.processCommand(command);
    },
    
    // Step 4: History navigation
    navigateHistory(direction) {
        const newIndex = this.historyIndex + direction;
        
        if (newIndex >= 0 && newIndex < this.history.length) {
            this.historyIndex = newIndex;
            this.elements.input.value = this.history[newIndex];
        } else if (newIndex >= this.history.length) {
            this.historyIndex = this.history.length;
            this.elements.input.value = '';
        }
    },
    
    // Step 5: Output handling with animations
    addLine(text, className = '') {
        const line = document.createElement('div');
        line.className = className;
        line.textContent = text;
        this.elements.output.appendChild(line);
        this.scrollToBottom();
    },
    
    async typewriterText(text, speed = 30, className = '') {
        // Cancel any ongoing animation
        if (this.currentAnimation) {
            this.currentAnimation.cancel = true;
        }
        
        const line = document.createElement('div');
        line.className = `${className} typing`;
        this.elements.output.appendChild(line);
        
        const animation = { cancel: false };
        this.currentAnimation = animation;
        
        // Type each character
        for (let i = 0; i < text.length; i++) {
            if (animation.cancel) break;
            
            line.textContent = text.substring(0, i + 1);
            await this.delay(speed);
        }
        
        this.currentAnimation = null;
        this.scrollToBottom();
    },
    
    async dramaticReveal(lines, pauseBetween = 1000) {
        for (const line of lines) {
            await this.typewriterText(line.text, line.speed || 30, line.className || '');
            await this.delay(pauseBetween);
        }
    },
    
    // Step 6: Text formatting
    formatText(text, style) {
        const styles = {
            dramatic: { className: 'dramatic', speed: 50 },
            fast: { className: 'fast', speed: 10 },
            error: { className: 'error', speed: 0 },
            success: { className: 'success', speed: 20 },
            whisper: { className: 'whisper', speed: 70 }
        };
        
        return styles[style] || { className: '', speed: 30 };
    },
    
    // Step 7: Event handling from other modules
    handleEvent(event, data) {
        switch(event) {
            case 'terminal:output':
                if (data.dramatic) {
                    this.dramaticReveal(data.lines);
                } else if (data.typewriter) {
                    const format = this.formatText(data.text, data.style);
                    this.typewriterText(data.text, format.speed, format.className);
                } else {
                    this.addLine(data.text, data.style || '');
                }
                break;
                
            case 'terminal:clear':
                this.clear();
                break;
                
            case 'render':
                // Update any terminal-specific UI elements
                break;
        }
    },
    
    // Step 8: Utility functions
    clear() {
        this.elements.output.innerHTML = '';
    },
    
    scrollToBottom() {
        this.elements.output.scrollTop = this.elements.output.scrollHeight;
    },
    
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    },
    
    // Step 9: Special effects
    async glitchText(text, duration = 1000) {
        const line = document.createElement('div');
        line.className = 'glitch';
        this.elements.output.appendChild(line);
        
        const chars = '!@#$%^&*()_+-=[]{}|;:,.<>?';
        const endTime = Date.now() + duration;
        
        while (Date.now() < endTime) {
            let glitched = '';
            for (let i = 0; i < text.length; i++) {
                if (Math.random() > 0.7) {
                    glitched += chars[Math.floor(Math.random() * chars.length)];
                } else {
                    glitched += text[i];
                }
            }
            line.textContent = glitched;
            await this.delay(50);
        }
        
        line.textContent = text;
        this.scrollToBottom();
    }
};

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => Terminal.init());
} else {
    Terminal.init();
}
