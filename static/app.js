/**
 * FINANCE-X TERMINAL - Application JavaScript
 * Modern, modular architecture for the trading terminal
 */

// ========== STATE MANAGEMENT ==========
const AppState = {
    currentView: 'NIFTY',
    commandHistory: [],
    historyIndex: -1,
    isLoading: false,
    lastUpdate: null,
    viewHistory: [],
    canGoBack: false
};

// ========== DOM REFERENCES ==========
const DOM = {
    cmdInput: null,
    contentBody: null,
    contentTitle: null,
    detailPanel: null,
    marketStatus: null,
    liveClock: null,
    lastUpdate: null,
    backBtn: null,
    niftyPrice: null,
    sensexPrice: null,
    refreshBtn: null,
    navBtns: null
};

// ========== INITIALIZATION ==========
document.addEventListener('DOMContentLoaded', () => {
    initializeDOM();
    initializeEventListeners();
    startClock();
    startPolling();

    // Initial load
    executeCommand('NIFTY');
    updateSystemStatus();
});

function initializeDOM() {
    DOM.cmdInput = document.getElementById('cmdInput');
    DOM.contentBody = document.getElementById('contentBody');
    DOM.contentTitle = document.getElementById('contentTitle');
    DOM.detailPanel = document.getElementById('detailPanel');
    DOM.marketStatus = document.getElementById('marketStatus');
    DOM.liveClock = document.getElementById('liveClock');
    DOM.lastUpdate = document.getElementById('lastUpdate');
    DOM.niftyPrice = document.getElementById('niftyPrice');
    DOM.sensexPrice = document.getElementById('sensexPrice');
    DOM.refreshBtn = document.getElementById('refreshBtn');
    DOM.backBtn = document.getElementById('backBtn');
    DOM.navBtns = document.querySelectorAll('.nav-btn');
}

function initializeEventListeners() {
    // Command input
    DOM.cmdInput.addEventListener('keydown', handleCommandInput);
    DOM.cmdInput.focus();

    // Auto-focus on click
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.nav-btn') && !e.target.closest('.action-btn')) {
            DOM.cmdInput.focus();
        }
    });

    // Navigation buttons
    DOM.navBtns.forEach(btn => {
        btn.addEventListener('click', () => handleNavClick(btn));
    });

    // Refresh button
    if (DOM.refreshBtn) {
        DOM.refreshBtn.addEventListener('click', () => {
            executeCommand(AppState.currentView);
        });
    }

    // Back button
    if (DOM.backBtn) {
        DOM.backBtn.addEventListener('click', goBack);
        updateBackButton();
    }
}

// ========== NAVIGATION HISTORY ==========
function goBack() {
    if (AppState.viewHistory.length > 1) {
        // Remove current view
        AppState.viewHistory.pop();
        // Get previous view
        const previousView = AppState.viewHistory[AppState.viewHistory.length - 1];
        // Execute without adding to history
        executeCommand(previousView, false, true);
    }
    updateBackButton();
}

function updateBackButton() {
    if (DOM.backBtn) {
        AppState.canGoBack = AppState.viewHistory.length > 1;
        DOM.backBtn.disabled = !AppState.canGoBack;
    }
}

// ========== CLOCK & POLLING ==========
function startClock() {
    function updateClock() {
        const now = new Date();
        DOM.liveClock.textContent = now.toLocaleTimeString('en-US', {
            hour12: false,
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
    }
    updateClock();
    setInterval(updateClock, 1000);
}

function startPolling() {
    // Update system status every 5 seconds
    setInterval(updateSystemStatus, 5000);

    // Refresh current view every 30 seconds
    setInterval(() => {
        if (!AppState.isLoading && AppState.currentView) {
            executeCommand(AppState.currentView, true); // silent refresh
        }
    }, 30000);
}

async function updateSystemStatus() {
    try {
        const response = await fetch('/status');
        const data = await response.json();

        const statusText = DOM.marketStatus.querySelector('.status-text');
        if (statusText) {
            statusText.textContent = data.state || 'ACTIVE';
        }

        // Update status dot color based on state
        const statusDot = DOM.marketStatus.querySelector('.status-dot');
        if (statusDot) {
            if (data.state === 'CRASH' || data.state === 'HIGH_VOL') {
                statusDot.style.background = '#ef4444';
            } else if (data.state === 'VOLATILE') {
                statusDot.style.background = '#f59e0b';
            } else {
                statusDot.style.background = '#10b981';
            }
        }
    } catch (error) {
        console.error('Status update failed:', error);
    }
}

// ========== COMMAND HANDLING ==========
function handleCommandInput(e) {
    if (e.key === 'Enter') {
        const cmd = DOM.cmdInput.value.trim().toUpperCase();
        if (cmd) {
            AppState.commandHistory.push(cmd);
            AppState.historyIndex = AppState.commandHistory.length;
            executeCommand(cmd);
            DOM.cmdInput.value = '';
        }
    } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        navigateHistory(-1);
    } else if (e.key === 'ArrowDown') {
        e.preventDefault();
        navigateHistory(1);
    }
}

function navigateHistory(direction) {
    const newIndex = AppState.historyIndex + direction;
    if (newIndex >= 0 && newIndex < AppState.commandHistory.length) {
        AppState.historyIndex = newIndex;
        DOM.cmdInput.value = AppState.commandHistory[newIndex];
    } else if (newIndex >= AppState.commandHistory.length) {
        AppState.historyIndex = AppState.commandHistory.length;
        DOM.cmdInput.value = '';
    }
}

function handleNavClick(btn) {
    const cmd = btn.dataset.cmd;
    const action = btn.dataset.action;

    // Update active state
    DOM.navBtns.forEach(b => b.classList.remove('active'));
    btn.classList.add('active');

    if (cmd) {
        executeCommand(cmd);
    } else if (action) {
        handleSpecialAction(action);
    }
}

function handleSpecialAction(action) {
    switch (action) {
        case 'search':
            showSearch();
            break;
        case 'screener':
            showScreener();
            break;
        default:
            console.log('Unknown action:', action);
    }
}

// ========== API CALLS ==========
async function executeCommand(cmd, silent = false, isBackNavigation = false) {
    if (!silent) {
        AppState.isLoading = true;
        showLoading();
    }

    AppState.currentView = cmd;

    // Add to view history (unless it's a back navigation or silent refresh)
    if (!isBackNavigation && !silent) {
        AppState.viewHistory.push(cmd);
        // Limit history to 50 items
        if (AppState.viewHistory.length > 50) {
            AppState.viewHistory.shift();
        }
        updateBackButton();
    }

    try {
        const response = await fetch('/command', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ command: cmd })
        });

        const data = await response.json();
        renderResponse(data);

        AppState.lastUpdate = new Date();
        DOM.lastUpdate.textContent = `Last update: ${AppState.lastUpdate.toLocaleTimeString()}`;

    } catch (error) {
        showError(`Connection error: ${error.message}`);
    } finally {
        AppState.isLoading = false;
    }
}

// ========== RENDERING ==========
function showLoading() {
    DOM.contentBody.innerHTML = `
        <div class="loading-state">
            <div class="loading-spinner"></div>
            <p>Loading data...</p>
        </div>
    `;
}

function showError(message) {
    DOM.contentBody.innerHTML = `
        <div class="loading-state" style="color: var(--down-color);">
            <p>âš ï¸ ${message}</p>
            <button class="action-btn" onclick="executeCommand('${AppState.currentView}')">
                Retry
            </button>
        </div>
    `;
}

function renderResponse(data) {
    DOM.contentTitle.textContent = data.title || AppState.currentView;

    switch (data.type) {
        case 'OVERVIEW_GRID':
            renderStockGrid(data);
            break;
        case 'FX_VIEW':
            renderFXTable(data);
            break;
        case 'CALENDAR_VIEW':
            renderCalendar(data);
            break;
        case 'SECTORS_VIEW':
            renderSectors(data);
            break;
        case 'MOVERS_VIEW':
            renderMovers(data);
            break;
        case 'HELP':
        case 'TEXT':
            renderHelp(data);
            break;
        case 'ERROR':
            showError(data.content || 'An error occurred');
            break;
        default:
            renderJSON(data);
    }
}

function renderStockGrid(data) {
    const stocks = data.grids || [];

    let html = '<div class="stock-grid fade-in">';

    stocks.forEach(stock => {
        const changeClass = stock.change_pct >= 0 ? 'up' : 'down';
        const sign = stock.change_pct >= 0 ? '+' : '';
        const price = stock.price?.toFixed(2) || '0.00';
        const change = stock.change_pct?.toFixed(2) || '0.00';

        html += `
            <div class="stock-card" onclick="showStockDetail('\', \, \)">
                <div class="stock-symbol">${stock.symbol}</div>
                <div class="stock-price">â‚¹${price}</div>
                <div class="stock-change ${changeClass}">${sign}${change}%</div>
            </div>
        `;
    });

    html += '</div>';
    DOM.contentBody.innerHTML = html;
}

function renderFXTable(data) {
    const rates = data.rates || [];

    let html = `
        <table class="data-table fade-in">
            <thead>
                <tr>
                    <th>Pair</th>
                    <th>Rate</th>
                    <th>Change %</th>
                    <th>Updated</th>
                </tr>
            </thead>
            <tbody>
    `;

    rates.forEach(rate => {
        const changeClass = rate.change_pct >= 0 ? 'positive' : 'negative';
        const sign = rate.change_pct >= 0 ? '+' : '';

        html += `
            <tr>
                <td><strong>${rate.pair}</strong></td>
                <td>${rate.rate?.toFixed(4) || '0.0000'}</td>
                <td class="${changeClass}">${sign}${rate.change_pct?.toFixed(2) || '0.00'}%</td>
                <td>${data.updated || '--'}</td>
            </tr>
        `;
    });

    html += '</tbody></table>';
    DOM.contentBody.innerHTML = html;
}

function renderCalendar(data) {
    const events = data.events || [];

    let html = '<div class="fade-in">';

    events.forEach(evt => {
        const impactClass = evt.impact?.toLowerCase() || 'low';

        html += `
            <div class="event-card">
                <h4>${evt.date} ${evt.time} - ${evt.event}</h4>
                <p>Currency: ${evt.currency || 'N/A'}</p>
                <span class="event-impact ${impactClass}">${evt.impact}</span>
            </div>
        `;
    });

    html += '</div>';
    DOM.contentBody.innerHTML = html;
}

function renderSectors(data) {
    const sectors = data.sectors || [];

    let html = '<div class="stock-grid fade-in">';

    sectors.forEach(sector => {
        const changeClass = sector.change_pct >= 0 ? 'up' : 'down';
        const sign = sector.change_pct >= 0 ? '+' : '';

        html += `
            <div class="stock-card" onclick="executeCommand('SCREEN ${sector.symbol}')">
                <div class="stock-symbol">${sector.name}</div>
                <div class="stock-price">${sector.symbol}</div>
                <div class="stock-change ${changeClass}">${sign}${sector.change_pct?.toFixed(2) || '0.00'}%</div>
            </div>
        `;
    });

    html += '</div>';
    DOM.contentBody.innerHTML = html;
}

function renderMovers(data) {
    let html = '<div class="fade-in" style="display: grid; grid-template-columns: 1fr 1fr; gap: 24px;">';

    // Gainers
    html += `
        <div>
            <h3 style="color: var(--up-color); margin-bottom: 16px;">ðŸ“ˆ TOP GAINERS</h3>
            <table class="data-table">
                <thead><tr><th>Symbol</th><th>Change %</th></tr></thead>
                <tbody>
    `;

    (data.gainers || []).forEach(stock => {
        html += `
            <tr onclick="showStockDetail('\', \, \)">
                <td><strong>${stock.symbol}</strong></td>
                <td class="positive">+${stock.change_pct?.toFixed(2) || '0.00'}%</td>
            </tr>
        `;
    });

    html += '</tbody></table></div>';

    // Losers
    html += `
        <div>
            <h3 style="color: var(--down-color); margin-bottom: 16px;">ðŸ“‰ TOP LOSERS</h3>
            <table class="data-table">
                <thead><tr><th>Symbol</th><th>Change %</th></tr></thead>
                <tbody>
    `;

    (data.losers || []).forEach(stock => {
        html += `
            <tr onclick="showStockDetail('\', \, \)">
                <td><strong>${stock.symbol}</strong></td>
                <td class="negative">${stock.change_pct?.toFixed(2) || '0.00'}%</td>
            </tr>
        `;
    });

    html += '</tbody></table></div></div>';
    DOM.contentBody.innerHTML = html;
}

function renderHelp(data) {
    const content = data.content || data.text || '';

    let html = `
        <div class="fade-in">
            <div class="help-section">
                <h3>Available Commands</h3>
                <div class="help-command"><span class="help-cmd">NIFTY</span><span class="help-desc">View NIFTY 50 stocks</span></div>
                <div class="help-command"><span class="help-cmd">MOVERS</span><span class="help-desc">Top gainers and losers</span></div>
                <div class="help-command"><span class="help-cmd">FX</span><span class="help-desc">Foreign exchange rates</span></div>
                <div class="help-command"><span class="help-cmd">SECTORS</span><span class="help-desc">Sector performance</span></div>
                <div class="help-command"><span class="help-cmd">CALENDAR</span><span class="help-desc">Economic calendar</span></div>
                <div class="help-command"><span class="help-cmd">CHART [SYMBOL]</span><span class="help-desc">Price chart for a stock</span></div>
                <div class="help-command"><span class="help-cmd">EVAL [SYMBOL]</span><span class="help-desc">Stock analysis</span></div>
                <div class="help-command"><span class="help-cmd">SCREEN [CRITERIA]</span><span class="help-desc">Stock screener</span></div>
            </div>
            ${content ? `<pre style="color: var(--text-secondary); font-size: 11px; white-space: pre-wrap;">${content}</pre>` : ''}
        </div>
    `;

    DOM.contentBody.innerHTML = html;
}

function renderJSON(data) {
    DOM.contentBody.innerHTML = `
        <pre class="fade-in" style="color: var(--text-secondary); font-size: 11px; white-space: pre-wrap; overflow: auto;">
${JSON.stringify(data, null, 2)}
        </pre>
    `;
}

// ========== SPECIAL VIEWS ==========
function showSearch() {
    DOM.contentTitle.textContent = 'STOCK SEARCH';

    DOM.contentBody.innerHTML = `
        <div class="search-container fade-in">
            <input 
                type="text" 
                class="search-input" 
                id="searchInput" 
                placeholder="Enter stock symbol or name (RELIANCE, TATA, INFY...)"
                autofocus
            >
        </div>
        <div id="searchResults"></div>
    `;

    const searchInput = document.getElementById('searchInput');
    searchInput.focus();

    searchInput.addEventListener('keyup', async (e) => {
        const query = e.target.value;
        if (query.length >= 2) {
            try {
                const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
                const result = await response.json();

                if (result.success && result.data.length > 0) {
                    let html = `
                        <table class="data-table">
                            <thead><tr><th>Symbol</th><th>Category</th><th>Type</th></tr></thead>
                            <tbody>
                    `;

                    result.data.forEach(stock => {
                        html += `
                            <tr onclick="showStockDetail('\', \, \)" style="cursor: pointer;">
                                <td><strong>${stock.symbol}</strong></td>
                                <td>${stock.category}</td>
                                <td>${stock.type}</td>
                            </tr>
                        `;
                    });

                    html += '</tbody></table>';
                    document.getElementById('searchResults').innerHTML = html;
                } else {
                    document.getElementById('searchResults').innerHTML = `
                        <p style="color: var(--text-muted); margin-top: 20px;">No stocks found</p>
                    `;
                }
            } catch (error) {
                console.error('Search error:', error);
            }
        }
    });
}

function showScreener() {
    DOM.contentTitle.textContent = 'STOCK SCREENER';

    const criteria = ['GAINERS', 'LOSERS', 'VOLUME', 'VOLATILITY'];
    const sectors = ['BANK', 'IT', 'PHARMA', 'AUTO', 'FMCG', 'METAL', 'ENERGY'];

    let html = `
        <div class="fade-in">
            <h3 style="color: var(--accent-cyan); margin-bottom: 16px;">SCREEN BY CRITERIA</h3>
            <div class="sector-grid" style="margin-bottom: 32px;">
    `;

    criteria.forEach(c => {
        html += `<button class="sector-btn" onclick="executeCommand('SCREEN ${c}')">${c}</button>`;
    });

    html += `
            </div>
            <h3 style="color: var(--accent-cyan); margin-bottom: 16px;">SCREEN BY SECTOR</h3>
            <div class="sector-grid">
    `;

    sectors.forEach(s => {
        html += `<button class="sector-btn" onclick="executeCommand('SCREEN ${s}')">${s}</button>`;
    });

    html += '</div></div>';
    DOM.contentBody.innerHTML = html;
}

// Make executeCommand available globally for onclick handlers
window.executeCommand = executeCommand;

// ========== DETAIL PANEL WITH CHARTS & INFO ==========
let activeChart = null;

function showStockDetail(symbol, price, changePct) {
    const isUp = changePct >= 0;
    const sign = isUp ? '+' : '';
    const trendClass = isUp ? 'positive' : 'negative';
    const trendIcon = isUp ? '[UP]' : '[DOWN]';

    DOM.detailPanel.innerHTML = `
        <div class="detail-content fade-in" style="padding: 16px;">
            <div style="margin-bottom: 16px;">
                <h2 style="font-size: 20px; color: var(--text-primary); margin-bottom: 4px;">${symbol}</h2>
                <div style="font-size: 24px; font-weight: 700; color: var(--accent-cyan); font-family: var(--font-mono);">Rs.${price.toFixed(2)}</div>
                <div class="${trendClass}" style="font-size: 14px; margin-top: 4px;">
                    ${trendIcon} ${sign}${changePct.toFixed(2)}% Today
                </div>
            </div>
            
            <div style="height: 120px; margin-bottom: 16px; background: var(--bg-elevated); border-radius: 8px; padding: 8px;">
                <canvas id="detailChart"></canvas>
            </div>
            
            <div style="margin-bottom: 16px;">
                <h4 style="color: var(--accent-cyan); font-size: 12px; margin-bottom: 8px;">QUICK ANALYSIS</h4>
                <p style="font-size: 11px; color: var(--text-secondary); line-height: 1.6;">${getStockAnalysis(symbol, changePct)}</p>
            </div>
            
            <div style="margin-bottom: 16px;">
                <h4 style="color: var(--accent-cyan); font-size: 12px; margin-bottom: 8px;">RELATED NEWS</h4>
                <div style="display: flex; flex-direction: column; gap: 6px;">
                    <a href="https://www.google.com/search?q=${symbol}+NSE+stock+news&tbm=nws" target="_blank" 
                       style="color: var(--accent-emerald); font-size: 11px; text-decoration: none;">
                        -> Google News: ${symbol}
                    </a>
                    <a href="https://www.moneycontrol.com/india/stockpricequote/" target="_blank" 
                       style="color: var(--accent-emerald); font-size: 11px; text-decoration: none;">
                        -> MoneyControl Analysis
                    </a>
                    <a href="https://economictimes.indiatimes.com/markets/stocks" target="_blank" 
                       style="color: var(--accent-emerald); font-size: 11px; text-decoration: none;">
                        -> Economic Times Markets
                    </a>
                </div>
            </div>
            
            <div style="display: flex; gap: 8px;">
                <button class="action-btn" onclick="executeCommand('CHART ${symbol}')" style="flex: 1;">
                    View Chart
                </button>
                <button class="action-btn" onclick="executeCommand('EVAL ${symbol}')" style="flex: 1;">
                    Deep Analysis
                </button>
            </div>
        </div>
    `;

    setTimeout(() => drawMiniChart(symbol, changePct), 100);
}

function getStockAnalysis(symbol, changePct) {
    if (changePct > 3) {
        return symbol + ' is showing strong bullish momentum with gains over 3%. Consider watching for resistance levels.';
    } else if (changePct > 0) {
        return symbol + ' is trading positive. Moderate gains suggest steady buying interest.';
    } else if (changePct > -3) {
        return symbol + ' has mild selling pressure. Watch support levels for reversal.';
    } else {
        return symbol + ' is under significant selling pressure. Check for fundamental news.';
    }
}

function drawMiniChart(symbol, changePct) {
    const canvas = document.getElementById('detailChart');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (activeChart) activeChart.destroy();

    const dataPoints = [];
    const labels = [];
    let baseValue = 100;
    const trend = changePct >= 0 ? 0.3 : -0.3;

    for (let i = 0; i < 20; i++) {
        baseValue += (Math.random() - 0.5 + trend) * 2;
        dataPoints.push(baseValue);
        labels.push(i);
    }

    const chartColor = changePct >= 0 ? '#10b981' : '#ef4444';

    activeChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{ data: dataPoints, borderColor: chartColor, backgroundColor: chartColor + '20', fill: true, tension: 0.4, pointRadius: 0, borderWidth: 2 }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: { x: { display: false }, y: { display: false } }
        }
    });
}

function showViewExplanation(view) {
    const info = {
        'NIFTY': { title: 'NIFTY 50 Index', icon: '[INDEX]', desc: 'India benchmark index: 50 largest NSE companies.', tips: ['Click stocks for details', 'Green=Up, Red=Down'], links: [['NSE India', 'https://www.nseindia.com/']] },
        'FX': { title: 'Forex Rates', icon: '[FX]', desc: 'Live currency rates including crypto.', tips: ['Watch USD/INR exposure'], links: [['Forex Factory', 'https://www.forexfactory.com/']] },
        'CALENDAR': { title: 'Economic Calendar', icon: '[CAL]', desc: 'Market-moving events: Fed, GDP, RBI.', tips: ['HIGH = major volatility'], links: [['Investing Calendar', 'https://www.investing.com/economic-calendar/']] },
        'SECTORS': { title: 'Sector Performance', icon: '[SEC]', desc: 'Track sector rotation.', tips: ['Strong sectors = bullish'], links: [['MoneyControl', 'https://www.moneycontrol.com/']] },
        'MOVERS': { title: 'Top Movers', icon: '[MOV]', desc: 'Biggest gainers/losers today.', tips: ['Check news first'], links: [['NSE Movers', 'https://www.nseindia.com/market-data/top-gainers-losers']] }
    }[view];
    if (!info) return;

    DOM.detailPanel.innerHTML = `
        <div style="padding: 16px;">
            <div style="font-size: 24px; margin-bottom: 8px; color: var(--accent-cyan);">${info.icon}</div>
            <h2 style="font-size: 16px; color: var(--text-primary); margin-bottom: 16px;">${info.title}</h2>
            <p style="font-size: 12px; color: var(--text-secondary); margin-bottom: 12px;">${info.desc}</p>
            <h4 style="color: var(--accent-cyan); font-size: 11px; margin-bottom: 6px;">TIPS</h4>
            <ul style="font-size: 11px; color: var(--text-secondary); padding-left: 16px; margin-bottom: 12px;">${info.tips.map(t => '<li>' + t + '</li>').join('')}</ul>
            <h4 style="color: var(--accent-cyan); font-size: 11px; margin-bottom: 6px;">LINKS</h4>
            ${info.links.map(l => '<a href="' + l[1] + '" target="_blank" style="color: var(--accent-emerald); font-size: 11px; display: block;">-> ' + l[0] + '</a>').join('')}
        </div>
    `;
}

window.showStockDetail = showStockDetail;
window.showViewExplanation = showViewExplanation;
