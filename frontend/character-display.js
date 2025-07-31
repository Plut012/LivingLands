// PLAN:
// 1. Virtue bar animations
// 2. Status indicator updates
// 3. Equipment display
// 4. Wound/scar visualization
// 5. Character art management

const CharacterDisplay = {
    // Step 1: Element references and state
    elements: {
        portrait: null,
        virtues: {},
        guard: null,
        wounds: null,
        equipment: null
    },
    
    animationQueue: [],
    currentVirtues: { vigour: 0, clarity: 0, spirit: 0 },
    
    // Step 2: Initialization
    init(gameState) {
        // Cache DOM elements
        this.elements.portrait = document.getElementById('character-art');
        this.elements.guard = document.getElementById('guard-value');
        this.elements.wounds = document.getElementById('wounds-value');
        
        // Cache virtue bars
        ['vigour', 'clarity', 'spirit'].forEach(virtue => {
            this.elements.virtues[virtue] = {
                bar: document.querySelector(`[data-virtue="${virtue}"] .fill`),
                value: document.querySelector(`[data-virtue="${virtue}"] .value`)
            };
        });
        
        // Register with module manager
        window.ModuleManager.register('characterDisplay', this);
        
        // Initial render
        this.render(gameState);
    },
    
    // Step 3: Main render function
    render(state) {
        if (!state.character) return;
        
        // Update virtues with animation
        this.updateVirtues(state.character.virtues);
        
        // Update status
        this.updateStatus(state.character);
        
        // Update portrait if changed
        if (state.character.portraitUrl) {
            this.updatePortrait(state.character.portraitUrl);
        }
    },
    
    // Step 4: Virtue bar animations
    updateVirtues(virtues) {
        Object.keys(virtues).forEach(virtue => {
            const newValue = virtues[virtue];
            const oldValue = this.currentVirtues[virtue];
            
            if (newValue !== oldValue) {
                this.animateVirtue(virtue, oldValue, newValue);
                this.currentVirtues[virtue] = newValue;
            }
        });
    },
    
    animateVirtue(virtue, from, to) {
        const elements = this.elements.virtues[virtue];
        if (!elements) return;
        
        // Calculate percentage
        const maxVirtue = 20; // d20 max
        const fromPercent = (from / maxVirtue) * 100;
        const toPercent = (to / maxVirtue) * 100;
        
        // Animate bar
        elements.bar.style.width = `${fromPercent}%`;
        
        // Add animation class
        elements.bar.classList.add('animating');
        
        // Use requestAnimationFrame for smooth animation
        const duration = 1000; // 1 second
        const startTime = performance.now();
        
        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            // Easing function
            const easeOutQuad = 1 - (1 - progress) * (1 - progress);
            
            const currentPercent = fromPercent + (toPercent - fromPercent) * easeOutQuad;
            elements.bar.style.width = `${currentPercent}%`;
            
            // Update value
            const currentValue = Math.round(from + (to - from) * easeOutQuad);
            elements.value.textContent = currentValue;
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            } else {
                elements.bar.classList.remove('animating');
                
                // Flash effect for significant changes
                if (Math.abs(to - from) >= 3) {
                    this.flashVirtue(virtue, to > from ? 'gain' : 'loss');
                }
            }
        };
        
        requestAnimationFrame(animate);
    },
    
    flashVirtue(virtue, type) {
        const bar = document.querySelector(`[data-virtue="${virtue}"]`);
        bar.classList.add(`flash-${type}`);
        setTimeout(() => bar.classList.remove(`flash-${type}`), 500);
    },
    
    // Step 5: Status updates
    updateStatus(character) {
        // Update Guard
        if (this.elements.guard) {
            const guardText = character.guard || 'None';
            if (this.elements.guard.textContent !== guardText.toString()) {
                this.animateTextChange(this.elements.guard, guardText);
            }
        }
        
        // Update Wounds
        if (this.elements.wounds) {
            const woundCount = character.wounds ? character.wounds.length : 0;
            this.elements.wounds.textContent = woundCount;
            
            // Add visual indicator for wounds
            if (woundCount > 0) {
                this.elements.wounds.parentElement.classList.add('wounded');
            } else {
                this.elements.wounds.parentElement.classList.remove('wounded');
            }
        }
    },
    
    // Step 6: Portrait management
    updatePortrait(url) {
        if (this.elements.portrait && this.elements.portrait.src !== url) {
            // Fade out old portrait
            this.elements.portrait.style.opacity = '0';
            
            setTimeout(() => {
                this.elements.portrait.src = url;
                this.elements.portrait.onload = () => {
                    // Fade in new portrait
                    this.elements.portrait.style.opacity = '1';
                };
            }, 300);
        }
    },
    
    // Step 7: Text change animations
    animateTextChange(element, newText) {
        element.style.transform = 'scale(1.5)';
        element.style.color = 'var(--accent-green)';
        
        setTimeout(() => {
            element.textContent = newText;
            element.style.transform = 'scale(1)';
            element.style.color = '';
        }, 200);
    },
    
    // Step 8: Wound/Scar visualization
    showWound(wound) {
        // Create wound notification
        const notification = document.createElement('div');
        notification.className = 'wound-notification';
        notification.innerHTML = `
            <div class="wound-title">Wounded!</div>
            <div class="wound-desc">${wound.description}</div>
            <div class="wound-location">${wound.location}</div>
        `;
        
        document.body.appendChild(notification);
        
        // Animate in
        setTimeout(() => notification.classList.add('visible'), 10);
        
        // Remove after delay
        setTimeout(() => {
            notification.classList.remove('visible');
            setTimeout(() => notification.remove(), 500);
        }, 3000);
    },
    
    // Step 9: Event handling
    handleEvent(event, data) {
        switch(event) {
            case 'render':
                this.render(data);
                break;
                
            case 'virtue:change':
                this.animateVirtue(data.virtue, data.from, data.to);
                break;
                
            case 'wound:received':
                this.showWound(data);
                break;
                
            case 'scar:gained':
                this.showScar(data);
                break;
                
            case 'effect:virtue-flash':
                this.flashVirtue(data.virtue, data.type);
                break;
        }
    },
    
    // Step 10: Special effects
    showScar(scar) {
        // Similar to wound but permanent
        const notification = document.createElement('div');
        notification.className = 'scar-notification';
        notification.innerHTML = `
            <div class="scar-title">Scarred!</div>
            <div class="scar-desc">${scar.description}</div>
            <div class="scar-effect">${scar.effect}</div>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => notification.classList.add('visible'), 10);
        setTimeout(() => {
            notification.classList.remove('visible');
            setTimeout(() => notification.remove(), 500);
        }, 5000);
    }
};
