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
            current: '#4a4a2a',
            gridLine: '#333333',
            fog: 'rgba(0, 0, 0, 0.7)',
            barrier: '#ff4444',
            // Terrain colors based on Mythic Bastionlands
            terrain: {
                marsh: '#2d4a2d',
                heath: '#4a3d2d', 
                crag: '#3d3d3d',
                peaks: '#5a5a5a',
                forest: '#1a3d1a',
                valley: '#2d4a3d',
                hills: '#4a4a2d',
                meadow: '#3d5a2d',
                bog: '#1a2d1a',
                lake: '#1a2d4a',
                glade: '#2d4a2d',
                plains: '#4a5a3d'
            },
            // Landmark colors
            landmark: {
                dwelling: '#8b4513',
                sanctum: '#daa520',
                monument: '#708090',
                hazard: '#dc143c',
                curse: '#8b008b',
                ruins: '#696969',
                holding: '#b8860b'
            },
            // Myth colors
            myth: {
                goblin: '#228b22',
                herald: '#4169e1',
                prisoner: '#9932cc',
                tyrant: '#b22222',
                dragon: '#ff4500',
                sleeper: '#2f4f4f'
            }
        }
    },
    
    state: {
        offset: { x: 0, y: 0 },
        zoom: 1,
        hoveredHex: null,
        exploredHexes: new Set(),
        hexData: new Map(),  // Store full hex data
        barriers: new Map()  // Store barriers by coordinate pairs
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
                const hexData = this.state.hexData.get(hexKey);
                
                // Determine hex color based on terrain and exploration status
                let fillColor = this.config.colors.unexplored;
                
                if (hexData && hexData.explored) {
                    // Use terrain-specific color if explored
                    const terrain = hexData.terrain || 'plains';
                    fillColor = this.config.colors.terrain[terrain] || this.config.colors.terrain.plains;
                    
                    // Modify color for current position
                    if (window.GameState && 
                        window.GameState.currentLocation && 
                        window.GameState.currentLocation.q === q && 
                        window.GameState.currentLocation.r === r) {
                        // Brighten current hex
                        fillColor = this.brightenColor(fillColor, 0.3);
                    }
                }
                
                // Draw the hex
                this.drawHex(q, r, fillColor, this.config.colors.gridLine);
                
                // Draw river overlay if present
                if (hexData && hexData.river && hexData.explored) {
                    this.drawRiver(q, r);
                }
                
                // Draw landmarks and myths
                if (hexData && hexData.explored) {
                    if (hexData.landmark) {
                        this.drawLandmark(q, r, hexData);
                    }
                    if (hexData.myth) {
                        this.drawMyth(q, r, hexData);
                    }
                }
            }
        }
        
        // Draw barriers
        this.drawBarriers();
        
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
    
    // Step 8: Enhanced rendering functions
    drawLandmark(q, r, hexData) {
        const { x, y } = this.hexToPixel(q, r);
        const size = this.config.hexSize * this.state.zoom * 0.5;
        
        this.ctx.save();
        this.ctx.translate(x, y);
        
        // Use landmark-specific colors
        const landmarkType = hexData.landmark;
        this.ctx.fillStyle = this.config.colors.landmark[landmarkType] || '#666666';
        
        switch(landmarkType) {
            case 'dwelling':
                // Draw house shape
                this.ctx.fillRect(-size/3, -size/6, size*2/3, size/3);
                this.ctx.beginPath();
                this.ctx.moveTo(-size/3, -size/6);
                this.ctx.lineTo(0, -size/2);
                this.ctx.lineTo(size/3, -size/6);
                this.ctx.closePath();
                this.ctx.fill();
                break;
            case 'holding':
                // Draw castle/town
                this.ctx.fillRect(-size/2, -size/4, size, size/2);
                this.ctx.fillRect(-size/4, -size/2, size/6, size/4);
                this.ctx.fillRect(0, -size/2, size/6, size/4);
                this.ctx.fillRect(size/4, -size/2, size/6, size/4);
                break;
            case 'sanctum':
                // Draw temple/shrine
                this.ctx.beginPath();
                this.ctx.arc(0, 0, size/3, 0, Math.PI * 2);
                this.ctx.fill();
                this.ctx.fillRect(-size/6, -size/2, size/3, size/2);
                break;
            case 'monument':
                // Draw obelisk/statue
                this.ctx.fillRect(-size/6, -size/2, size/3, size);
                this.ctx.fillRect(-size/4, size/3, size/2, size/6);
                break;
            case 'ruins':
                // Draw broken structures
                this.ctx.fillRect(-size/3, -size/6, size/4, size/3);
                this.ctx.fillRect(0, -size/4, size/4, size/6);
                this.ctx.fillRect(size/6, 0, size/6, size/4);
                break;
            case 'hazard':
                // Draw warning symbol
                this.ctx.beginPath();
                this.ctx.moveTo(0, -size/2);
                this.ctx.lineTo(-size/2, size/2);
                this.ctx.lineTo(size/2, size/2);
                this.ctx.closePath();
                this.ctx.fill();
                this.ctx.fillStyle = '#000';
                this.ctx.fillText('!', -size/8, size/8);
                break;
            case 'curse':
                // Draw cursed symbol
                this.ctx.beginPath();
                this.ctx.arc(0, 0, size/3, 0, Math.PI * 2);
                this.ctx.stroke();
                this.ctx.moveTo(-size/4, -size/4);
                this.ctx.lineTo(size/4, size/4);
                this.ctx.moveTo(size/4, -size/4);
                this.ctx.lineTo(-size/4, size/4);
                this.ctx.stroke();
                break;
        }
        
        this.ctx.restore();
    },
    
    drawMyth(q, r, hexData) {
        const { x, y } = this.hexToPixel(q, r);
        const size = this.config.hexSize * this.state.zoom * 0.4;
        
        this.ctx.save();
        this.ctx.translate(x + size/2, y - size/2);  // Offset from landmark if both present
        
        const mythType = hexData.myth;
        this.ctx.fillStyle = this.config.colors.myth[mythType] || '#4169e1';
        
        // Draw myth symbol - all as circles with different fill patterns
        this.ctx.beginPath();
        this.ctx.arc(0, 0, size/2, 0, Math.PI * 2);
        this.ctx.fill();
        
        // Add myth-specific inner symbol
        this.ctx.fillStyle = '#ffffff';
        this.ctx.font = `${size/2}px Arial`;
        this.ctx.textAlign = 'center';
        this.ctx.textBaseline = 'middle';
        
        const mythSymbols = {
            goblin: 'G',
            herald: 'H', 
            prisoner: 'P',
            tyrant: 'T',
            dragon: 'D',
            sleeper: 'S'
        };
        
        this.ctx.fillText(mythSymbols[mythType] || '?', 0, 0);
        
        this.ctx.restore();
    },
    
    drawRiver(q, r) {
        const { x, y } = this.hexToPixel(q, r);
        const size = this.config.hexSize * this.state.zoom;
        
        this.ctx.save();
        this.ctx.strokeStyle = '#4169e1';
        this.ctx.lineWidth = size / 8;
        this.ctx.lineCap = 'round';
        
        // Draw a wavy line across the hex
        this.ctx.beginPath();
        this.ctx.moveTo(x - size/2, y);
        this.ctx.quadraticCurveTo(x - size/4, y - size/4, x, y);
        this.ctx.quadraticCurveTo(x + size/4, y + size/4, x + size/2, y);
        this.ctx.stroke();
        
        this.ctx.restore();
    },
    
    drawBarriers() {
        for (const [barrierKey, barrier] of this.state.barriers) {
            const [hex1, hex2] = barrierKey.split('|').map(coord => {
                const [q, r] = coord.split(',').map(Number);
                return { q, r };
            });
            
            const pos1 = this.hexToPixel(hex1.q, hex1.r);
            const pos2 = this.hexToPixel(hex2.q, hex2.r);
            
            // Draw barrier line between hex centers
            this.ctx.save();
            this.ctx.strokeStyle = this.config.colors.barrier;
            this.ctx.lineWidth = 3 * this.state.zoom;
            this.ctx.lineCap = 'round';
            
            // Draw at midpoint between hexes
            const midX = (pos1.x + pos2.x) / 2;
            const midY = (pos1.y + pos2.y) / 2;
            const angle = Math.atan2(pos2.y - pos1.y, pos2.x - pos1.x);
            const perpAngle = angle + Math.PI / 2;
            const length = this.config.hexSize * this.state.zoom * 0.8;
            
            this.ctx.beginPath();
            this.ctx.moveTo(
                midX + Math.cos(perpAngle) * length / 2,
                midY + Math.sin(perpAngle) * length / 2
            );
            this.ctx.lineTo(
                midX - Math.cos(perpAngle) * length / 2,
                midY - Math.sin(perpAngle) * length / 2
            );
            this.ctx.stroke();
            
            this.ctx.restore();
        }
    },
    
    brightenColor(color, factor) {
        // Simple color brightening - convert hex to RGB, increase values, convert back
        const hex = color.replace('#', '');
        const r = Math.min(255, Math.floor(parseInt(hex.substr(0, 2), 16) * (1 + factor)));
        const g = Math.min(255, Math.floor(parseInt(hex.substr(2, 2), 16) * (1 + factor)));
        const b = Math.min(255, Math.floor(parseInt(hex.substr(4, 2), 16) * (1 + factor)));
        
        return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`;
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
        
        // Update hex data
        if (gameState.world_data.hexes) {
            this.state.hexData.clear();
            Object.entries(gameState.world_data.hexes).forEach(([key, hexData]) => {
                this.state.hexData.set(key, hexData);
            });
        }
        
        // Update barriers
        if (gameState.world_data.barriers) {
            this.state.barriers.clear();
            gameState.world_data.barriers.forEach(barrierData => {
                const key = `${barrierData.hex1[0]},${barrierData.hex1[1]}|${barrierData.hex2[0]},${barrierData.hex2[1]}`;
                this.state.barriers.set(key, barrierData);
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
