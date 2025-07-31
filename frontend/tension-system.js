// PLAN:
// 1. Dramatic pause timing
// 2. Suspense text generation
// 3. Outcome reveal choreography
// 4. Atmospheric effect coordination
// 5. Dice roll animations

const TensionSystem = {
    // Step 1: Configuration and state
    config: {
        basePause: 500,
        maxPause: 3000,
        tensionMultiplier: 1.5,
        effectDurations: {
            shake: 500,
            flash: 300,
            pulse: 1000
        }
    },
    
    currentTension: 0,
    activeEffects: new Set(),
    
    // Step 2: Initialization
    init(gameState) {
        // Register with module manager
        window.ModuleManager.register('tension', this);
        
        // Create effect overlay
        this.createEffectOverlay();
    },
    
    createEffectOverlay() {
        const overlay = document.createElement('div');
        overlay.id = 'tension-overlay';
        overlay.className = 'tension-overlay';
        document.body.appendChild(overlay);
        this.overlay = overlay;
    },
    
    // Step 3: Tension building
    async buildTension(level = 1) {
        this.currentTension = Math.min(level, 5);
        
        // Add visual effects based on tension level
        if (level >= 2) {
            this.addEffect('dim-lights');
        }
        if (level >= 3) {
            this.addEffect('heartbeat');
        }
        if (level >= 4) {
            this.addEffect('shake');
        }
        
        // Calculate pause duration
        const pauseDuration = Math.min(
            this.config.basePause * Math.pow(this.config.tensionMultiplier, level),
            this.config.maxPause
        );
        
        await this.pause(pauseDuration);
    },
    
    // Step 4: Dramatic reveals
    async dramaticReveal(options) {
        const {
            buildUp = [],
            revelation,
            aftermath = [],
            tensionLevel = 3
        } = options;
        
        // Build up phase
        for (const line of buildUp) {
            await this.revealText(line);
            await this.pause(this.config.basePause);
        }
        
        // Peak tension
        await this.buildTension(tensionLevel);
        
        // The reveal
        await this.revealText(revelation, true);
        
        // Release tension
        this.releaseTension();
        
        // Aftermath
        for (const line of aftermath) {
            await this.revealText(line);
            await this.pause(this.config.basePause / 2);
        }
    },
    
    // Step 5: Text reveal coordination
    async revealText(textData, isClimax = false) {
        const { text, style = 'normal', speed = 30 } = 
            typeof textData === 'string' ? { text: textData } : textData;
        
        // Add pre-reveal effects for climax
        if (isClimax) {
            this.addEffect('flash');
            await this.pause(100);
        }
        
        // Send to terminal with appropriate styling
        window.ModuleManager.broadcast('terminal:output', {
            text,
            style: isClimax ? 'dramatic' : style,
            typewriter: true
        });
        
        // Wait for text to complete
        await this.pause(text.length * speed);
    },
    
    // Step 6: Dice roll animations
    async animateDiceRoll(options) {
        const {
            diceType = 'd20',
            target,
            modifier = 0,
            advantage = false,
            disadvantage = false
        } = options;
        
        // Create dice display
        const diceDisplay = this.createDiceDisplay();
        
        // Roll animation
        const rolls = advantage || disadvantage ? 2 : 1;
        const results = [];
        
        for (let i = 0; i < rolls; i++) {
            const result = await this.animateSingleDie(diceDisplay, diceType);
            results.push(result);
        }
        
        // Determine final result
        let finalResult;
        if (advantage) {
            finalResult = Math.max(...results);
            await this.highlightResult(diceDisplay, finalResult, 'advantage');
        } else if (disadvantage) {
            finalResult = Math.min(...results);
            await this.highlightResult(diceDisplay, finalResult, 'disadvantage');
        } else {
            finalResult = results[0];
        }
        
        // Show modifier and total
        if (modifier !== 0) {
            await this.showModifier(diceDisplay, modifier, finalResult);
        }
        
        // Check against target
        if (target !== undefined) {
            await this.showSuccess(diceDisplay, finalResult + modifier, target);
        }
        
        // Clean up
        setTimeout(() => diceDisplay.remove(), 3000);
        
        return {
            roll: finalResult,
            total: finalResult + modifier,
            success: target ? (finalResult + modifier) >= target : null
        };
    },
    
    // Step 7: Visual effects
    addEffect(effectName) {
        this.activeEffects.add(effectName);
        document.body.classList.add(`effect-${effectName}`);
        
        // Auto-remove timed effects
        const duration = this.config.effectDurations[effectName];
        if (duration) {
            setTimeout(() => this.removeEffect(effectName), duration);
        }
    },
    
    removeEffect(effectName) {
        this.activeEffects.delete(effectName);
        document.body.classList.remove(`effect-${effectName}`);
    },
    
    releaseTension() {
        this.currentTension = 0;
        this.activeEffects.forEach(effect => this.removeEffect(effect));
    },
    
    // Step 8: Dice display helpers
    createDiceDisplay() {
        const display = document.createElement('div');
        display.className = 'dice-display';
        display.innerHTML = `
            <div class="dice-container">
                <div class="die" id="die-1"></div>
                <div class="die" id="die-2" style="display: none;"></div>
            </div>
            <div class="dice-info"></div>
        `;
        document.body.appendChild(display);
        return display;
    },
    
    async animateSingleDie(display, diceType) {
        const die = display.querySelector('.die');
        const max = parseInt(diceType.substring(1));
        
        // Rapid number changes
        for (let i = 0; i < 20; i++) {
            die.textContent = Math.floor(Math.random() * max) + 1;
            await this.pause(50 + i * 5); // Slow down
        }
        
        // Final result
        const result = Math.floor(Math.random() * max) + 1;
        die.textContent = result;
        die.classList.add('final');
        
        return result;
    },
    
    // Step 9: Event handling
    handleEvent(event, data) {
        switch(event) {
            case 'tension:build':
                this.buildTension(data.level);
                break;
                
            case 'tension:reveal':
                this.dramaticReveal(data);
                break;
                
            case 'dice:roll':
                return this.animateDiceRoll(data);
                
            case 'effect:add':
                this.addEffect(data.effect);
                break;
                
            case 'effect:remove':
                this.removeEffect(data.effect);
                break;
        }
    },
    
    // Step 10: Utility functions
    pause(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    },
    
    async highlightResult(display, result, type) {
        const die = display.querySelector('.die');
        die.classList.add(`highlight-${type}`);
        await this.pause(500);
    },
    
    async showModifier(display, modifier, base) {
        const info = display.querySelector('.dice-info');
        const sign = modifier >= 0 ? '+' : '';
        info.innerHTML = `${base} ${sign}${modifier} = ${base + modifier}`;
        info.classList.add('fade-in');
    },
    
    async showSuccess(display, total, target) {
        const info = display.querySelector('.dice-info');
        const success = total >= target;
        info.innerHTML += `<div class="${success ? 'success' : 'failure'}">
            ${success ? 'SUCCESS' : 'FAILURE'} (needed ${target})
        </div>`;
    }
};
