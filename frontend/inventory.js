// PLAN:
// 1. Equipment list display
// 2. Item interaction handling
// 3. Trade interface
// 4. Weight/encumbrance tracking
// 5. Drag and drop support

const Inventory = {
    // Step 1: State and configuration
    state: {
        selectedItem: null,
        isDragging: false,
        tradeMode: false,
        currentTrade: null
    },
    
    config: {
        maxWeight: 10, // Standard carrying capacity
        slotTypes: ['weapon', 'armor', 'shield'],
        itemCategories: {
            weapon: ['hefty', 'long', 'slow'],
            armor: ['common', 'uncommon', 'rare'],
            tool: ['common', 'uncommon', 'rare'],
            consumable: ['remedy', 'sustenance', 'sacrament', 'stimulant']
        }
    },
    
    // Step 2: Initialization
    init(gameState) {
        // Register with module manager
        window.ModuleManager.register('inventory', this);
        
        // Set up event delegation for dynamic content
        this.setupEventDelegation();
    },
    
    // Step 3: Event delegation
    setupEventDelegation() {
        // Handle clicks on inventory items when tab is open
        document.addEventListener('click', (e) => {
            if (e.target.closest('.item')) {
                this.handleItemClick(e.target.closest('.item'));
            }
            
            if (e.target.closest('.slot')) {
                this.handleSlotClick(e.target.closest('.slot'));
            }
        });
        
        // Set up drag and drop
        this.setupDragAndDrop();
    },
    
    // Step 4: Item interaction
    handleItemClick(itemElement) {
        const index = parseInt(itemElement.dataset.index);
        const item = window.GameState.character.equipment[index];
        
        if (!item) return;
        
        // Toggle selection
        if (this.state.selectedItem === index) {
            this.deselectItem();
        } else {
            this.selectItem(index, itemElement);
        }
    },
    
    selectItem(index, element) {
        // Deselect previous
        this.deselectItem();
        
        // Select new
        this.state.selectedItem = index;
        element.classList.add('selected');
        
        // Show item actions
        this.showItemActions(index);
    },
    
    deselectItem() {
        if (this.state.selectedItem !== null) {
            const selected = document.querySelector('.item.selected');
            if (selected) selected.classList.remove('selected');
            
            this.state.selectedItem = null;
            this.hideItemActions();
        }
    },
    
    // Step 5: Item actions menu
    showItemActions(index) {
        const item = window.GameState.character.equipment[index];
        
        const actions = document.createElement('div');
        actions.className = 'item-actions';
        actions.innerHTML = `
            <button onclick="Inventory.equipItem(${index})">Equip</button>
            <button onclick="Inventory.dropItem(${index})">Drop</button>
            <button onclick="Inventory.examineItem(${index})">Examine</button>
            ${item.usable ? `<button onclick="Inventory.useItem(${index})">Use</button>` : ''}
        `;
        
        const itemElement = document.querySelector(`[data-index="${index}"]`);
        itemElement.appendChild(actions);
    },
    
    hideItemActions() {
        const actions = document.querySelector('.item-actions');
        if (actions) actions.remove();
    },
    
    // Step 6: Equipment management
    equipItem(index) {
        const item = window.GameState.character.equipment[index];
        if (!item || !item.slot) return;
        
        // Unequip current item in slot
        const currentEquipped = window.GameState.character.equipment.find(
            i => i.equipped && i.slot === item.slot
        );
        
        if (currentEquipped) {
            currentEquipped.equipped = false;
        }
        
        // Equip new item
        item.equipped = true;
        
        // Update display
        window.ModuleManager.broadcast('inventory:update', {});
        
        // Notify
        window.ModuleManager.broadcast('terminal:output', {
            text: `You equip the ${item.name}.`,
            style: 'success'
        });
    },
    
    dropItem(index) {
        const item = window.GameState.character.equipment[index];
        if (!item) return;
        
        // Confirm drop
        window.ModuleManager.broadcast('terminal:output', {
            text: `Drop ${item.name}? This cannot be undone. (y/n)`,
            style: 'warning'
        });
        
        // Set up confirmation handler
        this.awaitConfirmation((confirmed) => {
            if (confirmed) {
                window.GameState.character.equipment.splice(index, 1);
                window.ModuleManager.broadcast('inventory:update', {});
                window.ModuleManager.broadcast('terminal:output', {
                    text: `You drop the ${item.name}.`
                });
            }
        });
    },
    
    examineItem(index) {
        const item = window.GameState.character.equipment[index];
        if (!item) return;
        
        window.ModuleManager.broadcast('terminal:output', {
            text: item.description || `A ${item.quality || 'common'} ${item.name}.`,
            typewriter: true
        });
    },
    
    useItem(index) {
        const item = window.GameState.character.equipment[index];
        if (!item || !item.usable) return;
        
        // Send use command to backend
        window.Game.processCommand(`use ${item.name}`);
    },
    
    // Step 7: Weight tracking
    calculateWeight() {
        const equipment = window.GameState.character.equipment || [];
        return equipment.reduce((total, item) => total + (item.weight || 0), 0);
    },
    
    isEncumbered() {
        return this.calculateWeight() > this.config.maxWeight;
    },
    
    getEncumbranceDisplay() {
        const current = this.calculateWeight();
        const max = this.config.maxWeight;
        const percentage = (current / max) * 100;
        
        return {
            current,
            max,
            percentage,
            status: percentage > 100 ? 'overloaded' : 
                    percentage > 80 ? 'heavy' : 
                    percentage > 60 ? 'medium' : 'light'
        };
    },
    
    // Step 8: Drag and drop
    setupDragAndDrop() {
        // Make items draggable
        document.addEventListener('dragstart', (e) => {
            if (e.target.closest('.item')) {
                this.handleDragStart(e);
            }
        });
        
        // Handle drop zones
        document.addEventListener('dragover', (e) => {
            if (e.target.closest('.slot') || e.target.closest('.trade-slot')) {
                e.preventDefault();
            }
        });
        
        document.addEventListener('drop', (e) => {
            if (e.target.closest('.slot')) {
                this.handleDropOnSlot(e);
            } else if (e.target.closest('.trade-slot')) {
                this.handleDropOnTrade(e);
            }
        });
    },
    
    handleDragStart(e) {
        const item = e.target.closest('.item');
        const index = item.dataset.index;
        
        e.dataTransfer.effectAllowed = 'move';
        e.dataTransfer.setData('text/html', index);
        
        this.state.isDragging = true;
        item.classList.add('dragging');
    },
    
    handleDropOnSlot(e) {
        e.preventDefault();
        
        const slot = e.target.closest('.slot');
        const slotType = slot.dataset.slot;
        const itemIndex = e.dataTransfer.getData('text/html');
        
        // Validate and equip
        const item = window.GameState.character.equipment[itemIndex];
        if (item && item.slot === slotType) {
            this.equipItem(itemIndex);
        }
        
        this.state.isDragging = false;
    },
    
    // Step 9: Trading interface
    initiateTrade(npcData) {
        this.state.tradeMode = true;
        this.state.currentTrade = {
            npc: npcData,
            offering: [],
            requesting: []
        };
        
        // Show trade interface
        this.showTradeInterface();
    },
    
    showTradeInterface() {
        // Create trade overlay
        const tradeUI = document.createElement('div');
        tradeUI.className = 'trade-interface';
        tradeUI.innerHTML = `
            <div class="trade-header">
                <h3>Trading with ${this.state.currentTrade.npc.name}</h3>
                <button onclick="Inventory.cancelTrade()">Cancel</button>
            </div>
            <div class="trade-grid">
                <div class="your-offer">
                    <h4>Your Offer</h4>
                    <div class="trade-slots" id="your-offer"></div>
                </div>
                <div class="their-offer">
                    <h4>Their Goods</h4>
                    <div class="trade-slots" id="their-goods"></div>
                </div>
            </div>
            <button onclick="Inventory.proposeTrade()">Propose Trade</button>
        `;
        
        document.body.appendChild(tradeUI);
    },
    
    // Step 10: Event handling
    handleEvent(event, data) {
        switch(event) {
            case 'trade:initiate':
                this.initiateTrade(data);
                break;
                
            case 'inventory:add':
                this.addItem(data.item);
                break;
                
            case 'inventory:remove':
                this.removeItem(data.index);
                break;
                
            case 'weight:check':
                return this.getEncumbranceDisplay();
        }
    },
    
    // Utility functions
    awaitConfirmation(callback) {
        const handler = (e) => {
            if (e.key === 'y' || e.key === 'Y') {
                callback(true);
                document.removeEventListener('keydown', handler);
            } else if (e.key === 'n' || e.key === 'N') {
                callback(false);
                document.removeEventListener('keydown', handler);
            }
        };
        
        document.addEventListener('keydown', handler);
    },
    
    addItem(item) {
        window.GameState.character.equipment.push(item);
        window.ModuleManager.broadcast('inventory:update', {});
    },
    
    removeItem(index) {
        window.GameState.character.equipment.splice(index, 1);
        window.ModuleManager.broadcast('inventory:update', {});
    }
};
