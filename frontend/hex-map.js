// PLAN:
// 1. Canvas hex grid rendering
// 2. Fog of war management
// 3. Hex interaction handling
// 4. Landmark placement
// 5. Visual state updates

const HexMap = {
    // Step 1: Configuration and state
    canvas: null,
    ctx: null,
    
    config: {
        hexSize: 30,
        mapWidth: 20,
        mapHeight: 15,
        colors: {
            unexplored: '#0a0a0a',
            explored: '#1a1a1a',
            current: '#2a2a2a',
            landmark: '#3a3a3a',
            gridLine: '#333333',
            fog: 'rgba(0, 0, 0, 0.7)'
        }
    },
    
    state: {
        offset: { x: 0, y: 0 },
        zoom: 1,
        hoveredHex: null,
        exploredHexes: new Set(),
        landmarks: new Map()
    },
    
    // Step 2: Initialization
    init(gameState) {
        this.canvas = document.getElementById('hex-canvas');
        this.ctx = this.canvas.getContext('2d');
        
        // Set canvas size
        this.resizeCanvas();
        window.addEventListener('resize', () => this.resizeCanvas());
        
        // Set up interaction handlers
        this.setupInteractions();
        
        // Register with module manager
        window.ModuleManager.register('hexMap', this);
        
        // Initial render
        this.render();
    },
    
    // Step 3: Canvas setup
    resizeCanvas() {
        const container = this.canvas.parentElement;
        this.canvas.width = container.clientWidth;
        this.canvas.height = container.clientHeight;
        this.render();
    },
    
    // Step 4: Hex calculations
    hexToPixel(q, r) {
        const size = this.config.hexSize * this.state.zoom;
        const x = size * (3/2 * q) + this.state.offset.x + this.canvas.width/2;
        const y = size * (Math.sqrt(3)/2 * q + Math.sqrt(3) * r) + this.state.offset.y + this.canvas.height/2;
        return { x, y };
    },
    
    pixelToHex(x, y) {
        const size = this.config.hexSize * this.state.zoom;
        const dx = x - this.canvas.width/2 - this.state.offset.x;
        const dy = y - this.canvas.height/2 - this.state.offset.y;
        
        const q = (2/3 * dx) / size;
        const r = (-1/3 * dx + Math.sqrt(3)/3 * dy) / size;
        
        return this.roundHex(q, r);
    },
    
    roundHex(q, r) {
        const s = -q - r;
        let rq = Math.round(q);
        let rr = Math.round(r);
        let rs = Math.round(s);
        
        const q_diff = Math.abs(rq - q);
        const r_diff = Math.abs(rr - r);
        const s_diff = Math.abs(rs - s);
        
        if (q_diff > r_diff && q_diff > s_diff) {
            rq = -rr - rs;
        } else if (r_diff > s_diff) {
            rr = -rq - rs;
        }
        
        return { q: rq, r: rr };
    },
    
    // Step 5: Drawing functions
    drawHex(q, r, fillStyle, strokeStyle = null) {
        const { x, y } = this.hexToPixel(q, r);
        const size = this.config.hexSize * this.state.zoom;
        
        this.ctx.beginPath();
        for (let i = 0; i < 6; i++) {
            const angle = 2 * Math.PI / 6 * i;
            const hx = x + size * Math.cos(angle);
            const hy = y + size * Math.sin(angle);
            
            if (i === 0) {
                this.ctx.moveTo(hx, hy);
            } else {
                this.ctx.lineTo(hx, hy);
            }
        }
        this.ctx.closePath();
        
        if (fillStyle) {
            this.ctx.fillStyle = fillStyle;
            this.ctx.fill();
        }
        
        if (strokeStyle) {
            this.ctx.strokeStyle = strokeStyle;
            this.ctx.stroke();
        }
    },
    
    // Step 6: Main render loop
    render() {
        // Clear canvas
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Calculate visible hex range
        const viewRadius = Math.ceil(
            Math.max(this.canvas.width, this.canvas.height) / 
            (this.config.hexSize * this.state.zoom)
        );
        
        // Draw hexes
        for (let q = -viewRadius; q <= viewRadius; q++) {
            for (let r = -viewRadius; r <= viewRadius; r++) {
                const hexKey = `${q},${r}`;
                
                // Determine hex color
                let fillColor = this.config.colors.unexplored;
                if (this.state.exploredHexes.has(hexKey)) {
                    fillColor = this.config.colors.explored;
                }
                if (window.GameState && 
                    window.GameState.currentLocation && 
                    window.GameState.currentLocation.q === q && 
                    window.GameState.currentLocation.r === r) {
                    fillColor = this.config.colors.current;
                }
                
                // Draw the hex
                this.drawHex(q, r, fillColor, this.config.colors.gridLine);
                
                // Draw landmarks
                if (this.state.landmarks.has(hexKey)) {
                    this.drawLandmark(q, r, this.state.landmarks.get(hexKey));
                }
            }
        }
        
        // Draw fog of war
        this.drawFogOfWar();
    },
    
    // Step 7: Fog of War
    drawFogOfWar() {
        const gradient = this.ctx.createRadialGradient(
            this.canvas.width / 2,
            this.canvas.height / 2,
            this.config.hexSize * 3 * this.state.zoom,
            this.canvas.width / 2,
            this.canvas.height / 2,
            Math.max(this.canvas.width, this.canvas.height) / 2
        );
        
        gradient.addColorStop(0, 'transparent');
        gradient.addColorStop(0.5, 'rgba(0, 0, 0, 0.3)');
        gradient.addColorStop(1, this.config.colors.fog);
        
        this.ctx.fillStyle = gradient;
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
    },
    
    // Step 8: Landmark rendering
    drawLandmark(q, r, landmark) {
        const { x, y } = this.hexToPixel(q, r);
        const size = this.config.hexSize * this.state.zoom * 0.6;
        
        this.ctx.save();
        this.ctx.translate(x, y);
        
        // Simple landmark icons
        this.ctx.fillStyle = '#666666';
        switch(landmark.type) {
            case 'city':
                // Draw simple city icon
                this.ctx.fillRect(-size/2, -size/2, size/3, size);
                this.ctx.fillRect(-size/6, -size/2, size/3, size*0.8);
                this.ctx.fillRect(size/6, -size/2, size/3, size*0.9);
                break;
            case 'myth':
                // Draw myth marker
                this.ctx.beginPath();
                this.ctx.arc(0, 0, size/2, 0, Math.PI * 2);
                this.ctx.fill();
                break;
            case 'omen':
                // Draw omen symbol
                this.ctx.beginPath();
                this.ctx.moveTo(0, -size/2);
                this.ctx.lineTo(-size/2, size/2);
                this.ctx.lineTo(size/2, size/2);
                this.ctx.closePath();
                this.ctx.fill();
                break;
        }
        
        this.ctx.restore();
    },
    
    // Step 9: Interaction handling
    setupInteractions() {
        let isDragging = false;
        let dragStart = { x: 0, y: 0 };
        
        this.canvas.addEventListener('mousedown', (e) => {
            isDragging = true;
            dragStart = { x: e.clientX, y: e.clientY };
        });
        
        this.canvas.addEventListener('mousemove', (e) => {
            if (isDragging) {
                this.state.offset.x += e.clientX - dragStart.x;
                this.state.offset.y += e.clientY - dragStart.y;
                dragStart = { x: e.clientX, y: e.clientY };
                this.render();
            } else {
                // Hover detection
                const rect = this.canvas.getBoundingClientRect();
                const hex = this.pixelToHex(
                    e.clientX - rect.left,
                    e.clientY - rect.top
                );
                this.state.hoveredHex = hex;
            }
        });
        
        this.canvas.addEventListener('mouseup', () => {
            isDragging = false;
        });
        
        this.canvas.addEventListener('click', (e) => {
            const rect = this.canvas.getBoundingClientRect();
            const hex = this.pixelToHex(
                e.clientX - rect.left,
                e.clientY - rect.top
            );
            
            // Send movement command through main API
            this.handleHexClick(hex);
            
            // Broadcast hex click event for other modules
            window.ModuleManager.broadcast('hex:clicked', hex);
        });
        
        // Zoom handling
        this.canvas.addEventListener('wheel', (e) => {
            e.preventDefault();
            const zoomSpeed = 0.1;
            const delta = e.deltaY > 0 ? -zoomSpeed : zoomSpeed;
            this.state.zoom = Math.max(0.5, Math.min(2, this.state.zoom + delta));
            this.render();
        });
    },
    
    // Step 10: Event handling
    handleEvent(event, data) {
        switch(event) {
            case 'render':
                // Use the new updateFromGameState method for full state updates
                if (data && data.world_data) {
                    this.updateFromGameState(data);
                } else {
                    // Fallback for old format
                    this.state.exploredHexes = new Set(data.exploredHexes || []);
                    this.render();
                }
                break;
                
            case 'hex:explore':
                this.state.exploredHexes.add(`${data.q},${data.r}`);
                this.render();
                break;
                
            case 'landmark:reveal':
                this.state.landmarks.set(`${data.q},${data.r}`, data.landmark);
                this.render();
                break;
                
            case 'map:center':
                this.centerOn(data.q, data.r);
                break;
        }
    },
    
    // Step 11: Hex click handling
    async handleHexClick(hex) {
        // Don't move if clicking current position
        if (window.GameState && 
            window.GameState.currentLocation && 
            window.GameState.currentLocation.q === hex.q && 
            window.GameState.currentLocation.r === hex.r) {
            return;
        }
        
        // Send movement command through main game API
        if (window.Game && window.Game.processCommand) {
            const command = `move to ${hex.q},${hex.r}`;
            await window.Game.processCommand(command);
        }
    },
    
    // Update game state integration
    updateFromGameState(gameState) {
        if (!gameState || !gameState.world_data) return;
        
        // Update current position
        if (gameState.world_data.position) {
            window.GameState.currentLocation = {
                q: gameState.world_data.position.q,
                r: gameState.world_data.position.r
            };
        }
        
        // Update explored hexes
        if (gameState.world_data.hexes) {
            this.state.exploredHexes.clear();
            Object.entries(gameState.world_data.hexes).forEach(([key, hexData]) => {
                if (hexData.explored) {
                    this.state.exploredHexes.add(key);
                }
            });
        }
        
        this.render();
    },

    // Step 12: Utility functions
    centerOn(q, r) {
        const { x, y } = this.hexToPixel(q, r);
        this.state.offset.x = -x + this.canvas.width / 2;
        this.state.offset.y = -y + this.canvas.height / 2;
        this.render();
    }
};

// Export for other modules
window.HexMap = HexMap;
