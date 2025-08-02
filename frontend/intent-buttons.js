// PLAN:
// 1. Handle intent button clicks
// 2. Integrate with game API
// 3. Manage button states
// 4. Coordinate with terminal input

// Step 1: Intent Button Manager
const IntentButtons = {
    selectedIntent: null,
    
    init() {
        this.setupEventListeners();
        this.updateButtonStates();
    },
    
    setupEventListeners() {
        const buttons = document.querySelectorAll('.intent-btn');
        
        buttons.forEach(button => {
            button.addEventListener('click', (e) => {
                this.handleButtonClick(e.target);
            });
        });
        
        // Listen for terminal input to clear selection when typing
        const terminalInput = document.getElementById('terminal-input');
        if (terminalInput) {
            terminalInput.addEventListener('input', () => {
                this.clearSelection();
            });
        }
    },
    
    handleButtonClick(button) {
        const intent = button.dataset.intent;
        
        // Toggle selection
        if (this.selectedIntent === intent) {
            this.clearSelection();
        } else {
            this.selectIntent(intent, button);
        }
    },
    
    selectIntent(intent, button) {
        this.selectedIntent = intent;
        this.updateButtonStates();
        
        // Send intent immediately or set up for next input
        this.sendIntentAction(intent);
    },
    
    clearSelection() {
        this.selectedIntent = null;
        this.updateButtonStates();
    },
    
    updateButtonStates() {
        const buttons = document.querySelectorAll('.intent-btn');
        
        buttons.forEach(button => {
            const intent = button.dataset.intent;
            if (intent === this.selectedIntent) {
                button.classList.add('selected');
            } else {
                button.classList.remove('selected');
            }
        });
    },
    
    async sendIntentAction(intent) {
        try {
            // Use existing API but with selected_intent parameter
            const response = await fetch('/api/v1/input', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    input: `I want to ${intent.toLowerCase()}`,
                    selected_intent: intent
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            
            // Broadcast result to other modules
            this.broadcastResult(result);
            
            // Clear selection after successful action
            this.clearSelection();
            
        } catch (error) {
            console.error('Error sending intent:', error);
            
            // Show error in terminal
            if (window.Terminal) {
                Terminal.addMessage(`Error: ${error.message}`, 'error');
            }
        }
    },
    
    broadcastResult(result) {
        // Update terminal with response
        if (window.Terminal && result.narrative) {
            Terminal.addMessage(result.narrative, 'narrative');
        }
        
        // Update character display if stats changed
        if (window.CharacterDisplay && result.character) {
            CharacterDisplay.updateFromGameState(result.character);
        }
        
        // Update hex map if location changed
        if (window.HexMap && result.world_data) {
            HexMap.updateFromGameState(result.world_data);
        }
        
        // Show options if provided
        if (result.options && result.options.length > 0) {
            if (window.Terminal) {
                Terminal.addMessage("\\nAvailable actions:", 'whisper');
                result.options.forEach((option, index) => {
                    Terminal.addMessage(`${index + 1}. ${option}`, 'option');
                });
            }
        }
        
        // Fire custom event for other modules
        document.dispatchEvent(new CustomEvent('gameStateUpdate', {
            detail: result
        }));
    },
    
    // Public method to send intent with custom input
    async sendIntentWithInput(intent, input) {
        try {
            const response = await fetch('/api/v1/input', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    input: input,
                    selected_intent: intent
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            this.broadcastResult(result);
            
            return result;
            
        } catch (error) {
            console.error('Error sending intent with input:', error);
            throw error;
        }
    }
};

// Step 2: Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    IntentButtons.init();
});

// Step 3: Export for other modules
window.IntentButtons = IntentButtons;