/**
 * کانفیگ یاب حرفه‌ای - Frontend JavaScript
 * اتصال به Python API Backend
 */

class ConfigFinderApp {
    constructor() {
        this.configs = [];
        this.stats = {
            total: 0,
            active: 0,
            slow: 0,
            dead: 0,
            untested: 0
        };
        this.activeFilter = 'all';
        this.apiBaseUrl = window.location.protocol + '//' + window.location.host + '/api';
        this.websocket = null;
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.connectWebSocket();
        this.loadConfigs();
        this.showWelcomeNotification();
    }
    
    setupEventListeners() {
        // دکمه دریافت کانفیگ‌ها
        document.getElementById('fetchBtn').addEventListener('click', () => {
            this.fetchConfigs();
        });
        
        // دکمه تست همه
        document.getElementById('testAllBtn').addEventListener('click', () => {
            this.testAllConfigs();
        });
        
        // دکمه تلاش مجدد
        document.getElementById('retryBtn').addEventListener('click', () => {
            this.fetchConfigs();
        });
        
        // فیلتر ها
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const filter = e.target.getAttribute('data-filter');
                this.setActiveFilter(filter);
            });
        });
        
        // بستن نوتیفیکیشن خوشامدگویی
        document.getElementById('closeWelcome').addEventListener('click', () => {
            this.hideWelcomeNotification();
        });
        
        document.getElementById('welcomeOkBtn').addEventListener('click', () => {
            this.hideWelcomeNotification();
        });
        
        // مودال ها
        this.setupModals();
    }
    
    setupModals() {
        // مودال تست
        document.getElementById('closeTestModal').addEventListener('click', () => {
            this.hideModal('testModal');
        });
        
        // مودال QR
        document.getElementById('closeQrModal').addEventListener('click', () => {
            this.hideModal('qrModal');
        });
        
        // مودال اطلاعات
        document.getElementById('closeInfoModal').addEventListener('click', () => {
            this.hideModal('infoModal');
        });
        
        // بستن مودال با کلیک روی background
        document.querySelectorAll('.modal').forEach(modal => {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    modal.classList.remove('active');
                }
            });
        });
        
        // بستن مودال با کلید ESC
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                document.querySelectorAll('.modal.active').forEach(modal => {
                    modal.classList.remove('active');
                });
            }
        });
    }
    
    connectWebSocket() {
        try {
            const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${wsProtocol}//${window.location.host}/api/ws`;
            
            this.websocket = new WebSocket(wsUrl);
            
            this.websocket.onopen = () => {
                console.log('✅ WebSocket اتصال برقرار شد');
            };
            
            this.websocket.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.handleWebSocketMessage(data);
                } catch (e) {
                    console.error('خطا در پارس پیام WebSocket:', e);
                }
            };
            
            this.websocket.onclose = () => {
                console.log('🔌 WebSocket اتصال قطع شد');
                // تلاش برای اتصال مجدد بعد از 5 ثانیه
                setTimeout(() => {
                    this.connectWebSocket();
                }, 5000);
            };
            
            this.websocket.onerror = (error) => {
                console.error('خطای WebSocket:', error);
            };
        } catch (e) {
            console.error('خطا در ایجاد WebSocket:', e);
        }
    }
    
    handleWebSocketMessage(data) {
        switch (data.type) {
            case 'connected':
                console.log('📡 اتصال WebSocket برقرار شد');
                break;
                
            case 'fetch_started':
                this.showLoadingState('در حال دریافت کانفیگ‌ها...');
                break;
                
            case 'fetch_completed':
                this.hideLoadingState();
                this.loadConfigs();
                this.showNotification(`✅ ${data.configs_count} کانفیگ دریافت شد`, 'success');
                break;
                
            case 'fetch_error':
                this.hideLoadingState();
                this.showErrorState();
                this.showNotification(`❌ خطا در دریافت: ${data.error}`, 'error');
                break;
                
            case 'test_started':
                this.showNotification(`🔄 شروع تست ${data.configs_count} کانفیگ`, 'info');
                break;
                
            case 'test_progress':
                this.updateTestProgress(data.config_id, data.message);
                break;
                
            case 'test_completed':
                this.updateStats(data.stats);
                this.loadConfigs();
                this.showNotification('✅ تست تمام شد', 'success');
                break;
                
            case 'test_error':
                this.showNotification(`❌ خطا در تست: ${data.error}`, 'error');
                break;
                
            case 'single_test_progress':
                this.updateSingleTestProgress(data.config_id, data.message);
                break;
                
            case 'single_test_completed':
                this.updateConfigResult(data.config_id, data.result);
                break;
        }
    }
    
    async fetchConfigs() {
        try {
            this.showLoadingState('در حال دریافت کانفیگ‌ها...');
            
            const response = await fetch(`${this.apiBaseUrl}/configs/fetch`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    source: document.getElementById('configType').value
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            
            const result = await response.json();
            
            if (result.success) {
                // WebSocket خودش UI رو بروزرسانی می‌کنه
                console.log('✅ درخواست دریافت کانفیگ ارسال شد');
            } else {
                throw new Error(result.error || 'خطای نامشخص');
            }
            
        } catch (error) {
            console.error('خطا در دریافت کانفیگ‌ها:', error);
            this.hideLoadingState();
            this.showErrorState();
            this.showNotification(`❌ خطا: ${error.message}`, 'error');
        }
    }
    
    async loadConfigs() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/configs?limit=50`);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            
            const data = await response.json();
            this.configs = data.configs || [];
            
            this.renderConfigs();
            this.loadStats();
            
        } catch (error) {
            console.error('خطا در بارگذاری کانفیگ‌ها:', error);
        }
    }
    
    async loadStats() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/stats`);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            
            const stats = await response.json();
            this.updateStats(stats);
            
        } catch (error) {
            console.error('خطا در بارگذاری آمار:', error);
        }
    }
    
    async testAllConfigs() {
        if (this.configs.length === 0) {
            this.showNotification('⚠️ ابتدا کانفیگ‌ها را دریافت کنید', 'warning');
            return;
        }
        
        try {
            const response = await fetch(`${this.apiBaseUrl}/configs/test`, {
                method: 'POST'
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            
            const result = await response.json();
            
            if (result.success) {
                console.log('✅ درخواست تست ارسال شد');
            } else {
                throw new Error(result.error || 'خطای نامشخص');
            }
            
        } catch (error) {
            console.error('خطا در تست کانفیگ‌ها:', error);
            this.showNotification(`❌ خطا: ${error.message}`, 'error');
        }
    }
    
    async testSingleConfig(configId) {
        try {
            this.showTestModal(configId);
            
            const response = await fetch(`${this.apiBaseUrl}/configs/${configId}/test`);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            
            const result = await response.json();
            
            if (result.success) {
                console.log(`✅ تست کانفیگ ${configId} تمام شد`);
            } else {
                throw new Error(result.error || 'خطای نامشخص');
            }
            
        } catch (error) {
            console.error('خطا در تست کانفیگ:', error);
            this.showNotification(`❌ خطا: ${error.message}`, 'error');
        }
    }
    
    renderConfigs() {
        const grid = document.getElementById('configsGrid');
        
        if (this.configs.length === 0) {
            document.getElementById('emptyState').classList.remove('hidden');
            document.getElementById('errorState').classList.add('hidden');
            grid.innerHTML = '';
            return;
        }
        
        document.getElementById('emptyState').classList.add('hidden');
        document.getElementById('errorState').classList.add('hidden');
        
        // فیلتر کانفیگ‌ها
        const filteredConfigs = this.activeFilter === 'all' 
            ? this.configs 
            : this.configs.filter(config => config.status === this.activeFilter);
        
        // ایجاد HTML
        const configsHTML = filteredConfigs.map(config => this.createConfigCardHTML(config)).join('');
        grid.innerHTML = configsHTML;
        
        // اضافه کردن event listeners
        this.attachConfigEventListeners();
    }
    
    createConfigCardHTML(config) {
        const statusBadge = this.getStatusBadge(config.status);
        const pingDisplay = this.getPingDisplay(config);
        const configType = this.getConfigType(config.config_url);
        const typeBadge = this.getTypeBadge(configType);
        
        return `
            <div class="config-card fade-in" data-id="${config.id}" data-status="${config.status}">
                <div class="card-content">
                    <div class="flex justify-between items-start mb-4">
                        <div>
                            <h3 class="text-lg font-bold text-white mb-2">${config.name}</h3>
                            <div class="flex items-center gap-2 mb-2">
                                ${typeBadge}
                                ${statusBadge}
                            </div>
                            <div class="text-sm text-gray-400">
                                <div class="flex items-center gap-1 mb-1">
                                    <i class="fas fa-server text-xs"></i>
                                    <span>${config.server}</span>
                                </div>
                                <div class="flex items-center gap-1">
                                    <i class="fas fa-network-wired text-xs"></i>
                                    <span>پورت ${config.port}</span>
                                </div>
                            </div>
                        </div>
                        <div class="flex flex-col gap-1">
                            <button class="tooltip px-2 py-1 text-xs bg-gray-700 hover:bg-gray-600 rounded" 
                                    onclick="configApp.showInfoModal(${config.id})">
                                <i class="fas fa-info-circle"></i>
                                <span class="tooltip-text">جزئیات</span>
                            </button>
                        </div>
                    </div>
                    
                    ${pingDisplay}
                    
                    <div class="flex gap-2 mt-4">
                        <button class="btn btn-primary flex-1 text-sm py-2 copy-btn" 
                                data-config="${encodeURIComponent(config.config_url)}">
                            <i class="fas fa-copy"></i>
                            <span>کپی</span>
                        </button>
                        <button class="btn text-sm px-3 py-2 test-btn" 
                                data-id="${config.id}">
                            <i class="fas fa-tachometer-alt"></i>
                            <span>تست</span>
                        </button>
                        <button class="btn text-sm px-3 py-2 qr-btn" 
                                data-config="${encodeURIComponent(config.config_url)}">
                            <i class="fas fa-qrcode"></i>
                        </button>
                    </div>
                </div>
            </div>
        `;
    }
    
    getStatusBadge(status) {
        const badges = {
            'active': '<span class="status-badge status-good"><i class="fas fa-check-circle"></i> فعال</span>',
            'slow': '<span class="status-badge status-medium"><i class="fas fa-exclamation-circle"></i> کند</span>',
            'dead': '<span class="status-badge status-bad"><i class="fas fa-times-circle"></i> غیرفعال</span>',
            'untested': '<span class="status-badge"><i class="fas fa-question-circle"></i> تست نشده</span>'
        };
        return badges[status] || badges['untested'];
    }
    
    getPingDisplay(config) {
        if (config.status === 'untested' || !config.ping) {
            return '<div class="mt-3"></div>';
        }
        
        const pingClass = config.ping < 100 ? 'bg-green-500' : 
                         config.ping < 300 ? 'bg-yellow-500' : 'bg-red-500';
        
        const percentage = Math.min((config.ping / 1000) * 100, 100);
        
        return `
            <div class="mt-3">
                <div class="flex justify-between items-center mb-1">
                    <span class="text-xs text-gray-400">پینگ</span>
                    <span class="text-xs text-white">${config.ping.toFixed(0)}ms</span>
                </div>
                <div class="ping-bar">
                    <div class="ping-progress ${pingClass}" style="width: ${percentage}%"></div>
                </div>
            </div>
        `;
    }
    
    getConfigType(configUrl) {
        if (configUrl.startsWith('vmess://')) return 'VMess';
        if (configUrl.startsWith('vless://')) return 'VLess';
        if (configUrl.startsWith('ss://')) return 'Shadowsocks';
        if (configUrl.startsWith('trojan://')) return 'Trojan';
        return 'نامشخص';
    }
    
    getTypeBadge(type) {
        const badges = {
            'VMess': 'bg-blue-500 bg-opacity-20 text-blue-400 border-blue-500',
            'VLess': 'bg-purple-500 bg-opacity-20 text-purple-400 border-purple-500',
            'Shadowsocks': 'bg-green-500 bg-opacity-20 text-green-400 border-green-500',
            'Trojan': 'bg-red-500 bg-opacity-20 text-red-400 border-red-500'
        };
        
        const badgeClass = badges[type] || 'bg-gray-500 bg-opacity-20 text-gray-400 border-gray-500';
        return `<span class="text-xs px-2 py-1 rounded-md border border-opacity-30 ${badgeClass}">${type}</span>`;
    }
    
    attachConfigEventListeners() {
        // دکمه‌های کپی
        document.querySelectorAll('.copy-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const configText = decodeURIComponent(btn.getAttribute('data-config'));
                this.copyToClipboard(configText);
                
                const originalText = btn.innerHTML;
                btn.innerHTML = '<i class="fas fa-check"></i><span>کپی شد</span>';
                btn.classList.add('btn-success');
                
                setTimeout(() => {
                    btn.innerHTML = originalText;
                    btn.classList.remove('btn-success');
                }, 2000);
            });
        });
        
        // دکمه‌های تست
        document.querySelectorAll('.test-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const configId = parseInt(btn.getAttribute('data-id'));
                this.testSingleConfig(configId);
            });
        });
        
        // دکمه‌های QR
        document.querySelectorAll('.qr-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const configText = decodeURIComponent(btn.getAttribute('data-config'));
                this.showQrModal(configText);
            });
        });
    }
    
    setActiveFilter(filter) {
        this.activeFilter = filter;
        
        // بروزرسانی UI فیلتر
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-filter="${filter}"]`).classList.add('active');
        
        // اعمال فیلتر
        this.renderConfigs();
    }
    
    updateStats(stats) {
        this.stats = stats;
        
        document.getElementById('activeCount').textContent = stats.active || 0;
        document.getElementById('slowCount').textContent = stats.slow || 0;
        document.getElementById('deadCount').textContent = stats.dead || 0;
        document.getElementById('untestCount').textContent = stats.untested || 0;
    }
    
    showLoadingState(message = 'در حال بارگذاری...') {
        document.getElementById('configsGrid').innerHTML = '';
        document.getElementById('emptyState').classList.add('hidden');
        document.getElementById('errorState').classList.add('hidden');
        document.getElementById('loadingState').classList.remove('hidden');
        document.getElementById('loadingState').querySelector('p').textContent = message;
    }
    
    hideLoadingState() {
        document.getElementById('loadingState').classList.add('hidden');
    }
    
    showErrorState() {
        document.getElementById('configsGrid').innerHTML = '';
        document.getElementById('emptyState').classList.add('hidden');
        document.getElementById('loadingState').classList.add('hidden');
        document.getElementById('errorState').classList.remove('hidden');
    }
    
    showNotification(message, type = 'info') {
        // ایجاد المان نوتیفیکیشن
        const notification = document.createElement('div');
        notification.className = `fixed top-20 right-4 z-50 px-4 py-3 rounded-lg shadow-lg text-white max-w-sm ${
            type === 'success' ? 'bg-green-600' :
            type === 'error' ? 'bg-red-600' :
            type === 'warning' ? 'bg-yellow-600' :
            'bg-blue-600'
        }`;
        notification.innerHTML = `
            <div class="flex items-center justify-between">
                <span>${message}</span>
                <button class="ml-2 text-white hover:text-gray-200">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // بستن خودکار بعد از 5 ثانیه
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 5000);
        
        // بستن با کلیک
        notification.querySelector('button').addEventListener('click', () => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        });
    }
    
    showWelcomeNotification() {
        setTimeout(() => {
            const welcome = document.getElementById('welcomeNotification');
            welcome.style.opacity = '1';
            welcome.style.transform = 'translate(-50%, -50%) scale(1)';
        }, 1000);
    }
    
    hideWelcomeNotification() {
        const welcome = document.getElementById('welcomeNotification');
        welcome.style.opacity = '0';
        welcome.style.transform = 'translate(-50%, -50%) scale(0.95)';
        setTimeout(() => {
            welcome.style.display = 'none';
        }, 500);
    }
    
    showModal(modalId) {
        document.getElementById(modalId).classList.add('active');
    }
    
    hideModal(modalId) {
        document.getElementById(modalId).classList.remove('active');
    }
    
    showTestModal(configId) {
        const config = this.configs.find(c => c.id === configId);
        if (!config) return;
        
        document.getElementById('testServerName').textContent = config.name;
        document.getElementById('testServerAddress').textContent = `${config.server}:${config.port}`;
        document.getElementById('testStatus').textContent = 'در حال اتصال...';
        document.getElementById('testProgressBar').style.width = '0%';
        document.getElementById('testLog').innerHTML = '<div class="terminal-line terminal-info">در حال شروع تست...</div>';
        
        this.showModal('testModal');
    }
    
    showQrModal(configText) {
        const qrContainer = document.getElementById('qrCode');
        qrContainer.innerHTML = '';
        
        QRCode.toCanvas(qrContainer, configText, {
            width: 200,
            margin: 2,
            color: {
                dark: '#000000',
                light: '#FFFFFF'
            }
        }, (error) => {
            if (error) {
                console.error('خطا در ایجاد QR Code:', error);
                qrContainer.innerHTML = '<div class="text-red-500">خطا در ایجاد QR Code</div>';
            }
        });
        
        this.showModal('qrModal');
    }
    
    showInfoModal(configId) {
        const config = this.configs.find(c => c.id === configId);
        if (!config) return;
        
        const details = `
            <div class="space-y-3">
                <div class="flex justify-between">
                    <span class="text-gray-400">نام سرور:</span>
                    <span>${config.name}</span>
                </div>
                <div class="flex justify-between">
                    <span class="text-gray-400">آدرس سرور:</span>
                    <span>${config.server}</span>
                </div>
                <div class="flex justify-between">
                    <span class="text-gray-400">پورت:</span>
                    <span>${config.port}</span>
                </div>
                <div class="flex justify-between">
                    <span class="text-gray-400">پروتکل:</span>
                    <span>${config.protocol}</span>
                </div>
                <div class="flex justify-between">
                    <span class="text-gray-400">وضعیت:</span>
                    <span>${config.status}</span>
                </div>
                ${config.ping ? `
                <div class="flex justify-between">
                    <span class="text-gray-400">پینگ:</span>
                    <span>${config.ping.toFixed(0)}ms</span>
                </div>
                ` : ''}
                ${config.last_tested ? `
                <div class="flex justify-between">
                    <span class="text-gray-400">آخرین تست:</span>
                    <span>${new Date(config.last_tested).toLocaleString('fa-IR')}</span>
                </div>
                ` : ''}
            </div>
        `;
        
        document.getElementById('configDetails').innerHTML = details;
        document.getElementById('rawConfig').textContent = config.config_url;
        
        this.showModal('infoModal');
    }
    
    updateTestProgress(configId, message) {
        const modal = document.getElementById('testModal');
        if (!modal.classList.contains('active')) return;
        
        const currentConfigId = parseInt(document.getElementById('testServerName').getAttribute('data-id') || '0');
        if (configId !== currentConfigId) return;
        
        document.getElementById('testStatus').textContent = message;
        
        // افزایش progress bar
        const progressBar = document.getElementById('testProgressBar');
        const currentWidth = parseInt(progressBar.style.width) || 0;
        progressBar.style.width = Math.min(currentWidth + 25, 90) + '%';
        
        // اضافه کردن به لاگ
        const log = document.getElementById('testLog');
        const logLine = document.createElement('div');
        logLine.className = 'terminal-line terminal-info';
        logLine.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
        log.appendChild(logLine);
        log.scrollTop = log.scrollHeight;
    }
    
    updateSingleTestProgress(configId, message) {
        this.updateTestProgress(configId, message);
    }
    
    updateConfigResult(configId, result) {
        // بروزرسانی کانفیگ در لیست
        const config = this.configs.find(c => c.id === configId);
        if (config) {
            config.status = result.status;
            config.ping = result.ping;
            config.last_tested = new Date().toISOString();
        }
        
        // بروزرسانی UI
        this.renderConfigs();
        this.loadStats();
        
        // بروزرسانی مودال تست
        const modal = document.getElementById('testModal');
        if (modal.classList.contains('active')) {
            document.getElementById('testStatus').textContent = `تست تمام شد - ${result.status}`;
            document.getElementById('testProgressBar').style.width = '100%';
            
            const log = document.getElementById('testLog');
            const logLine = document.createElement('div');
            logLine.className = `terminal-line ${result.status === 'active' ? 'terminal-success' : 'terminal-error'}`;
            logLine.textContent = `[${new Date().toLocaleTimeString()}] نتیجه: ${result.status}`;
            log.appendChild(logLine);
            log.scrollTop = log.scrollHeight;
        }
    }
    
    copyToClipboard(text) {
        if (navigator.clipboard) {
            navigator.clipboard.writeText(text);
        } else {
            const textarea = document.createElement('textarea');
            textarea.value = text;
            document.body.appendChild(textarea);
            textarea.select();
            document.execCommand('copy');
            document.body.removeChild(textarea);
        }
    }
}

// شروع اپلیکیشن
let configApp;
document.addEventListener('DOMContentLoaded', () => {
    configApp = new ConfigFinderApp();
});
