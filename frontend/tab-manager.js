// PLAN:
// 1. Overlay panel system
// 2. Tab switching logic
// 3. Content loading for panels
// 4. Animation coordination
// 5. State management per tab

const TabManager = {
    // Step 1: State and configuration
    state: {
        isOpen: false,
        activeTab: null,
        tabContents: {},
        tabHistory: []
    },
    
    tabs: {
        inventory: {
            title: 'Inventory',
            loader: 'loadInventory'
        },
        company: {
            title: 'Company',
            loader: 'loadCompany'
        },
        journal: {
            title: 'Journal',
            loader: 'loadJournal'
        },
        rules: {
            title: 'Rules Reference',
            loader: 'loadRules'
        }
    },
    
    // Step 2: Initialization
    init(gameState) {
        this.overlay = document.getElementById('tab-overlay');
        this.content = document.getElementById('tab-content');
        
        // Set up event listeners
        this.setupEventListeners();
        
        // Register with module manager
        window.ModuleManager.register('tabManager', this);
        
        // Set up keyboard shortcuts
        this.setupKeyboardShortcuts();
    },
    
    // Step 3: Event listeners
    setupEventListeners() {
        // Tab buttons
        document.querySelectorAll('.tab-button').forEach(button => {
            button.addEventListener('click', (e) => {
                const tabName = e.target.dataset.tab;
                this.switchTab(tabName);
            });
        });
        
        // Close button
        document.querySelector('.tab-close').addEventListener('click', () => {
            this.close();
        });
        
        // Click outside to close
        this.overlay.addEventListener('click', (e) => {
            if (e.target === this.overlay) {
                this.close();
            }
        });
    },
    
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // ESC to close
            if (e.key === 'Escape' && this.state.isOpen) {
                this.close();
                return;
            }
            
            // Tab shortcuts (Alt + key)
            if (e.altKey) {
                switch(e.key) {
                    case 'i':
                        this.toggle('inventory');
                        break;
                    case 'c':
                        this.toggle('company');
                        break;
                    case 'j':
                        this.toggle('journal');
                        break;
                    case 'r':
                        this.toggle('rules');
                        break;
                }
            }
        });
    },
    
    // Step 4: Open/close functionality
    open(tabName = null) {
        if (!this.state.isOpen) {
            this.overlay.style.display = 'block';
            setTimeout(() => {
                this.overlay.classList.add('open');
            }, 10);
            this.state.isOpen = true;
        }
        
        if (tabName) {
            this.switchTab(tabName);
        } else if (!this.state.activeTab) {
            // Open first tab by default
            this.switchTab('inventory');
        }
    },
    
    close() {
        this.overlay.classList.remove('open');
        setTimeout(() => {
            this.overlay.style.display = 'none';
        }, 300);
        this.state.isOpen = false;
    },
    
    toggle(tabName) {
        if (this.state.isOpen && this.state.activeTab === tabName) {
            this.close();
        } else {
            this.open(tabName);
        }
    },
    
    // Step 5: Tab switching
    switchTab(tabName) {
        if (!this.tabs[tabName]) return;
        
        // Update active state
        document.querySelectorAll('.tab-button').forEach(button => {
            button.classList.toggle('active', button.dataset.tab === tabName);
        });
        
        // Add to history
        if (this.state.activeTab !== tabName) {
            this.state.tabHistory.push(tabName);
        }
        
        this.state.activeTab = tabName;
        
        // Load content
        this.loadTabContent(tabName);
    },
    
    // Step 6: Content loading
    async loadTabContent(tabName) {
        // Show loading state
        this.content.innerHTML = '<div class="loading">Loading...</div>';
        
        // Check cache
        if (this.state.tabContents[tabName]) {
            this.content.innerHTML = this.state.tabContents[tabName];
            return;
        }
        
        // Load fresh content
        const loader = this[this.tabs[tabName].loader];
        if (loader) {
            const content = await loader.call(this);
            this.state.tabContents[tabName] = content;
            this.content.innerHTML = content;
        }
    },
    
    // Step 7: Content loaders
    async loadInventory() {
        const character = window.GameState.character;
        const equipment = character.equipment || [];
        
        let html = '<div class="inventory-grid">';
        
        // Equipment slots
        html += `
            <div class="equipment-slots">
                <h3>Equipped</h3>
                <div class="slot" data-slot="weapon">
                    <div class="slot-label">Weapon</div>
                    <div class="slot-item">${this.getEquipped('weapon') || 'Empty'}</div>
                </div>
                <div class="slot" data-slot="armor">
                    <div class="slot-label">Armor</div>
                    <div class="slot-item">${this.getEquipped('armor') || 'Empty'}</div>
                </div>
                <div class="slot" data-slot="shield">
                    <div class="slot-label">Shield</div>
                    <div class="slot-item">${this.getEquipped('shield') || 'Empty'}</div>
                </div>
            </div>
        `;
        
        // Inventory list
        html += `
            <div class="inventory-list">
                <h3>Carried Items</h3>
                <div class="items">
        `;
        
        equipment.forEach((item, index) => {
            html += `
                <div class="item" data-index="${index}">
                    <span class="item-name">${item.name}</span>
                    <span class="item-weight">${item.weight || 0}</span>
                </div>
            `;
        });
        
        html += `
                </div>
            </div>
        </div>`;
        
        return html;
    },
    
    async loadCompany() {
        const company = window.GameState.company || [];
        
        let html = '<div class="company-view">';
        html += '<h2>Your Company</h2>';
        
        if (company.length === 0) {
            html += '<p class="empty-state">You travel alone...</p>';
        } else {
            html += '<div class="company-grid">';
            
            company.forEach(knight => {
                html += `
                    <div class="knight-card">
                        <h3>${knight.name}</h3>
                        <div class="knight-virtues">
                            <div>Vigour: ${knight.virtues.vigour}</div>
                            <div>Clarity: ${knight.virtues.clarity}</div>
                            <div>Spirit: ${knight.virtues.spirit}</div>
                        </div>
                        <div class="knight-status">
                            <div>Guard: ${knight.guard}</div>
                            <div>Wounds: ${knight.wounds.length}</div>
                        </div>
                    </div>
                `;
            });
            
            html += '</div>';
        }
        
        html += '</div>';
        return html;
    },
    
    async loadJournal() {
        const journal = window.GameState.journal || [];
        
        let html = '<div class="journal-view">';
        html += '<h2>Journal</h2>';
        
        if (journal.length === 0) {
            html += '<p class="empty-state">Your journey has just begun...</p>';
        } else {
            html += '<div class="journal-entries">';
            
            journal.reverse().forEach(entry => {
                html += `
                    <div class="journal-entry">
                        <div class="entry-date">${entry.date}</div>
                        <div class="entry-content">${entry.content}</div>
                    </div>
                `;
            });
            
            html += '</div>';
        }
        
        html += '</div>';
        return html;
    },
    
    async loadRules() {
        // Basic rules reference
        let html = '<div class="rules-view">';
        html += `
            <h2>Quick Reference</h2>
            
            <section class="rule-section">
                <h3>Actions</h3>
                <div class="rule-item">
                    <strong>Intent:</strong> What are you trying to do?
                </div>
                <div class="rule-item">
                    <strong>Leverage:</strong> What makes it possible?
                </div>
                <div class="rule-item">
                    <strong>Cost:</strong> What's the resource, cause, or side-effect?
                </div>
                <div class="rule-item">
                    <strong>Risk:</strong> No risk = no roll. Otherwise, Save or Luck Roll.
                </div>
            </section>
            
            <section class="rule-section">
                <h3>Saves</h3>
                <div class="rule-item">
                    Roll d20 ≤ relevant Virtue to succeed
                </div>
                <div class="rule-item">
                    <strong>Vigour:</strong> Physical challenges
                </div>
                <div class="rule-item">
                    <strong>Clarity:</strong> Mental challenges
                </div>
                <div class="rule-item">
                    <strong>Spirit:</strong> Social/emotional challenges
                </div>
            </section>
            
            <section class="rule-section">
                <h3>Combat</h3>
                <div class="rule-item">
                    <strong>Attack:</strong> Roll weapon damage + modifiers
                </div>
                <div class="rule-item">
                    <strong>Damage:</strong> Reduced by target's Guard (GD)
                </div>
                <div class="rule-item">
                    <strong>Wounds:</strong> Damage > remaining Vigour
                </div>
            </section>
        `;
        
        html += '</div>';
        return html;
    },
    
    // Step 8: Helper functions
    getEquipped(slot) {
        const character = window.GameState.character;
        const equipped = character.equipment.find(item => 
            item.equipped && item.slot === slot
        );
        return equipped ? equipped.name : null;
    },
    
    // Step 9: Event handling
    handleEvent(event, data) {
        switch(event) {
            case 'tab:open':
                this.open(data.tab);
                break;
                
            case 'tab:close':
                this.close();
                break;
                
            case 'tab:refresh':
                // Clear cache for specific tab
                if (data.tab && this.state.tabContents[data.tab]) {
                    delete this.state.tabContents[data.tab];
                    if (this.state.activeTab === data.tab) {
                        this.loadTabContent(data.tab);
                    }
                }
                break;
                
            case 'inventory:update':
            case 'company:update':
            case 'journal:update':
                // Clear relevant cache
                const tabName = event.split(':')[0];
                delete this.state.tabContents[tabName];
                if (this.state.activeTab === tabName) {
                    this.loadTabContent(tabName);
                }
                break;
        }
    },
    
    // Step 10: Animations
    animateTabSwitch(fromTab, toTab) {
        this.content.style.opacity = '0';
        
        setTimeout(() => {
            this.loadTabContent(toTab);
            this.content.style.opacity = '1';
        }, 200);
    }
};
