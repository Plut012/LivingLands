// PLAN:
// 1. Ambient text generation
// 2. Mood setting utilities
// 3. Immersive effect triggers
// 4. Sound/visual ambiance coordination
// 5. Environmental storytelling

const Atmosphere = {
    // Step 1: Configuration and text banks
    config: {
        ambientInterval: 30000, // 30 seconds
        moodDuration: 10000, // 10 seconds
        effectIntensity: {
            subtle: 0.3,
            moderate: 0.6,
            intense: 1.0
        }
    },
    
    textBanks: {
        wilderness: {
            day: [
                "A crow caws in the distance.",
                "The wind whispers through ancient trees.",
                "Sunlight filters through the canopy above.",
                "Something rustles in the undergrowth."
            ],
            night: [
                "An owl hoots somewhere in the darkness.",
                "The moon casts long shadows across your path.",
                "Strange lights dance between the trees.",
                "The night is alive with unseen movements."
            ]
        },
        dungeon: [
            "Water drips steadily in the darkness.",
            "Ancient stones groan under their own weight.",
            "A cold draft carries the scent of ages past.",
            "Your footsteps echo into the void."
        ],
        combat: [
            "Your heart pounds in your chest.",
            "Time seems to slow as danger approaches.",
            "The air grows thick with tension.",
            "Every shadow could hide a threat."
        ]
    },
    
    currentMood: 'neutral',
    ambientTimer: null,
    activeEffects: [],
    
    // Step 2: Initialization
    init(gameState) {
        // Register with module manager
        window.ModuleManager.register('atmosphere', this);
        
        // Create atmosphere overlay
        this.createAtmosphereLayer();
        
        // Start ambient text generation
        this.startAmbientText();
    },
    
    createAtmosphereLayer() {
        const layer = document.createElement('div');
        layer.id = 'atmosphere-layer';
        layer.className = 'atmosphere-layer';
        document.body.appendChild(layer);
        this.layer = layer;
    },
    
    // Step 3: Ambient text generation
    startAmbientText() {
        this.ambientTimer = setInterval(() => {
            if (this.shouldGenerateAmbient()) {
                this.generateAmbientText();
            }
        }, this.config.ambientInterval);
    },
    
    shouldGenerateAmbient() {
        // Don't generate during combat or tense moments
        return this.currentMood !== 'combat' && 
               this.currentMood !== 'tension' &&
               !window.GameState.inCombat;
    },
    
    generateAmbientText() {
        const location = window.GameState.currentLocation;
        const timeOfDay = window.GameState.timeOfDay || 'day';
        
        let textPool = [];
        
        // Select appropriate text bank
        if (location.type === 'wilderness') {
            textPool = this.textBanks.wilderness[timeOfDay] || this.textBanks.wilderness.day;
        } else if (location.type === 'dungeon') {
            textPool = this.textBanks.dungeon;
        }
        
        if (textPool.length > 0) {
            const text = textPool[Math.floor(Math.random() * textPool.length)];
            
            window.ModuleManager.broadcast('terminal:output', {
                text: text,
                style: 'ambient',
                typewriter: true
            });
        }
    },
    
    // Step 4: Mood management
    setMood(mood, intensity = 'moderate') {
        this.currentMood = mood;
        
        // Clear previous mood effects
        this.clearMoodEffects();
        
        // Apply new mood
        switch(mood) {
            case 'eerie':
                this.applyEerieMood(intensity);
                break;
            case 'peaceful':
                this.applyPeacefulMood(intensity);
                break;
            case 'tension':
                this.applyTensionMood(intensity);
                break;
            case 'combat':
                this.applyCombatMood(intensity);
                break;
            case 'mystical':
                this.applyMysticalMood(intensity);
                break;
        }
    },
    
    clearMoodEffects() {
        document.body.classList.remove(
            'mood-eerie', 'mood-peaceful', 'mood-tension', 
            'mood-combat', 'mood-mystical'
        );
        
        this.activeEffects.forEach(effect => {
            clearInterval(effect.timer);
        });
        this.activeEffects = [];
    },
    
    // Step 5: Specific mood implementations
    applyEerieMood(intensity) {
        document.body.classList.add('mood-eerie');
        
        // Visual effects
        this.addVisualNoise(intensity);
        this.dimLighting(intensity);
        
        // Text effects
        const eerieTexts = [
            "Something feels wrong here...",
            "The shadows seem to move on their own.",
            "A chill runs down your spine."
        ];
        
        this.scheduleRandomText(eerieTexts, 10000, 20000);
    },
    
    applyPeacefulMood(intensity) {
        document.body.classList.add('mood-peaceful');
        
        // Gentle lighting
        this.addSoftGlow(intensity);
        
        // Calming texts
        const peacefulTexts = [
            "A sense of calm washes over you.",
            "The world feels still and quiet.",
            "Peace settles into your bones."
        ];
        
        this.scheduleRandomText(peacefulTexts, 20000, 40000);
    },
    
    applyTensionMood(intensity) {
        document.body.classList.add('mood-tension');
        
        // Quick flashes
        this.addTensionFlashes(intensity);
        
        // No ambient text during tension
        clearInterval(this.ambientTimer);
    },
    
    applyCombatMood(intensity) {
        document.body.classList.add('mood-combat');
        
        // Combat effects
        this.addCombatShake(intensity);
        this.addRedTint(intensity);
        
        // Stop ambient text
        clearInterval(this.ambientTimer);
    },
    
    applyMysticalMood(intensity) {
        document.body.classList.add('mood-mystical');
        
        // Mystical effects
        this.addMysticalParticles(intensity);
        this.addColorShift(intensity);
        
        // Mystical texts
        const mysticalTexts = [
            "Reality seems to shimmer at the edges.",
            "Ancient power thrums in the air.",
            "The veil between worlds grows thin."
        ];
        
        this.scheduleRandomText(mysticalTexts, 15000, 25000);
    },
    
    // Step 6: Visual effects
    addVisualNoise(intensity) {
        const noise = document.createElement('div');
        noise.className = 'visual-noise';
        noise.style.opacity = this.config.effectIntensity[intensity];
        this.layer.appendChild(noise);
        
        this.activeEffects.push({ element: noise });
    },
    
    dimLighting(intensity) {
        const dimmer = document.createElement('div');
        dimmer.className = 'light-dimmer';
        dimmer.style.opacity = this.config.effectIntensity[intensity] * 0.5;
        this.layer.appendChild(dimmer);
        
        this.activeEffects.push({ element: dimmer });
    },
    
    addSoftGlow(intensity) {
        const glow = document.createElement('div');
        glow.className = 'soft-glow';
        glow.style.opacity = this.config.effectIntensity[intensity] * 0.3;
        this.layer.appendChild(glow);
        
        this.activeEffects.push({ element: glow });
    },
    
    addTensionFlashes(intensity) {
        const flash = () => {
            const flashEl = document.createElement('div');
            flashEl.className = 'tension-flash';
            this.layer.appendChild(flashEl);
            
            setTimeout(() => flashEl.remove(), 100);
        };
        
        const timer = setInterval(flash, 3000 / this.config.effectIntensity[intensity]);
        this.activeEffects.push({ timer });
    },
    
    // Step 7: Environmental storytelling
    describeEnvironment(environment) {
        const descriptions = {
            'ancient-tomb': {
                initial: "Dust motes dance in shafts of pale light. The air tastes of centuries.",
                details: [
                    "Hieroglyphs cover every surface, their meaning lost to time.",
                    "The walls seem to absorb sound, creating an oppressive silence.",
                    "Stone sarcophagi line the walls, their occupants long since turned to dust."
                ]
            },
            'dark-forest': {
                initial: "The canopy above blocks out all but the faintest light.",
                details: [
                    "Gnarled roots twist across the path, eager to trip the unwary.",
                    "Eyes glint in the darkness between the trees.",
                    "The forest seems to close in behind you as you pass."
                ]
            },
            'abandoned-keep': {
                initial: "Once-proud walls now crumble under the weight of neglect.",
                details: [
                    "Tattered banners hang limply in the still air.",
                    "Rust-stained armor lies scattered across the courtyard.",
                    "Nature has begun to reclaim this place, vines creeping through every crack."
                ]
            }
        };
        
        const desc = descriptions[environment];
        if (desc) {
            // Initial description
            window.ModuleManager.broadcast('terminal:output', {
                text: desc.initial,
                style: 'dramatic',
                typewriter: true
            });
            
            // Schedule detail reveals
            desc.details.forEach((detail, index) => {
                setTimeout(() => {
                    window.ModuleManager.broadcast('terminal:output', {
                        text: detail,
                        style: 'ambient',
                        typewriter: true
                    });
                }, (index + 1) * 5000);
            });
        }
    },
    
    // Step 8: Weather effects
    setWeather(weatherType, intensity = 'moderate') {
        // Clear previous weather
        document.body.classList.remove(
            'weather-rain', 'weather-fog', 'weather-storm', 'weather-snow'
        );
        
        // Apply new weather
        document.body.classList.add(`weather-${weatherType}`);
        
        // Weather-specific effects
        switch(weatherType) {
            case 'rain':
                this.createRainEffect(intensity);
                break;
            case 'fog':
                this.createFogEffect(intensity);
                break;
            case 'storm':
                this.createStormEffect(intensity);
                break;
            case 'snow':
                this.createSnowEffect(intensity);
                break;
        }
    },
    
    // Step 9: Event handling
    handleEvent(event, data) {
        switch(event) {
            case 'mood:set':
                this.setMood(data.mood, data.intensity);
                break;
                
            case 'environment:describe':
                this.describeEnvironment(data.type);
                break;
                
            case 'weather:set':
                this.setWeather(data.type, data.intensity);
                break;
                
            case 'atmosphere:clear':
                this.clearAll();
                break;
        }
    },
    
    // Step 10: Utility functions
    scheduleRandomText(texts, minDelay, maxDelay) {
        const scheduleNext = () => {
            const delay = minDelay + Math.random() * (maxDelay - minDelay);
            const timer = setTimeout(() => {
                const text = texts[Math.floor(Math.random() * texts.length)];
                window.ModuleManager.broadcast('terminal:output', {
                    text: text,
                    style: 'whisper',
                    typewriter: true
                });
                scheduleNext();
            }, delay);
            
            this.activeEffects.push({ timer });
        };
        
        scheduleNext();
    },
    
    clearAll() {
        this.clearMoodEffects();
        clearInterval(this.ambientTimer);
        this.layer.innerHTML = '';
        document.body.className = document.body.className
            .replace(/mood-\w+/g, '')
            .replace(/weather-\w+/g, '');
    }
};
