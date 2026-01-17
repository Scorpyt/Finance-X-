/**
 * Terminal Extensions for Volatility and Heatmap Views
 * Add these renderers to terminal.js or include this file separately
 */

// Volatility View Renderer
function renderVolatilityView(response) {
    const output = document.getElementById('detailView');
    const { symbol, current_price, metrics, regime, comparison } = response;

    output.innerHTML = `
        <div style="background: rgba(31,41,55,0.9); border: 1px solid #374151; border-radius: 8px; padding: 20px; margin-bottom: 20px;">
            <div style="color: #10b981; font-size: 24px; font-weight: 700; margin-bottom: 10px;">
                📊 ${symbol} Volatility Analysis
            </div>
            <div style="color: #9ca3af; font-size: 14px; margin-bottom: 20px;">
                Current Price: <span style="color: #fff; font-weight: 600;">₹${current_price.toFixed(2)}</span>
            </div>
            
            <!-- Volatility Regime -->
            <div style="background: ${getRegimeColor(regime)}; border: 2px solid ${getRegimeBorder(regime)}; border-radius: 6px; padding: 15px; margin-bottom: 20px;">
                <div style="color: #fff; font-size: 18px; font-weight: 700; text-align: center;">
                    Volatility Regime: ${regime}
                </div>
            </div>
            
            <!-- Metrics Grid -->
            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; margin-bottom: 20px;">
                ${renderMetricCard('Rolling Vol (20d)', metrics.rolling_vol_20d, '#3b82f6')}
                ${renderMetricCard('Historical Vol (Annual)', metrics.historical_vol_annual, '#8b5cf6')}
                ${renderMetricCard('EWMA Volatility', metrics.ewma_vol, '#ec4899')}
                ${renderMetricCard('Vol Percentile', metrics.vol_percentile, '#f59e0b')}
                ${metrics.parkinson_vol !== 'N/A' ? renderMetricCard('Parkinson Vol', metrics.parkinson_vol, '#10b981') : ''}
                ${metrics.garman_klass_vol !== 'N/A' ? renderMetricCard('Garman-Klass Vol', metrics.garman_klass_vol, '#06b6d4') : ''}
            </div>
            
            <!-- Comparison -->
            <div style="background: rgba(17,24,39,0.5); border: 1px solid #374151; border-radius: 6px; padding: 15px;">
                <div style="color: #10b981; font-size: 14px; font-weight: 600; margin-bottom: 10px;">Volatility Comparison</div>
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px;">
                    <div>
                        <div style="color: #6b7280; font-size: 11px;">20-Day Vol</div>
                        <div style="color: #fff; font-size: 16px; font-weight: 600;">${comparison.vol_20d}</div>
                    </div>
                    <div>
                        <div style="color: #6b7280; font-size: 11px;">50-Day Vol</div>
                        <div style="color: #fff; font-size: 16px; font-weight: 600;">${comparison.vol_50d}</div>
                    </div>
                    <div>
                        <div style="color: #6b7280; font-size: 11px;">Vol Ratio</div>
                        <div style="color: ${parseFloat(comparison.vol_ratio) > 1 ? '#ef4444' : '#10b981'}; font-size: 16px; font-weight: 600;">${comparison.vol_ratio}</div>
                    </div>
                </div>
            </div>
        </div>
    `;
}

// Volatility Scanner View
function renderVolScanView(response) {
    const output = document.getElementById('detailView');
    const { count, data } = response;

    output.innerHTML = `
        <div style="background: rgba(31,41,55,0.9); border: 1px solid #374151; border-radius: 8px; padding: 20px;">
            <div style="color: #ef4444; font-size: 24px; font-weight: 700; margin-bottom: 10px;">
                🔥 High Volatility Scanner
            </div>
            <div style="color: #9ca3af; font-size: 14px; margin-bottom: 20px;">
                Found ${count} stocks with significant volatility
            </div>
            
            <div style="display: grid; gap: 10px;">
                ${data.map((stock, idx) => `
                    <div style="background: rgba(17,24,39,0.5); border: 1px solid ${getRegimeBorder(stock.regime)}; border-radius: 6px; padding: 12px; display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <div style="color: #fff; font-size: 16px; font-weight: 600;">${idx + 1}. ${stock.symbol}</div>
                            <div style="color: #9ca3af; font-size: 12px;">Regime: <span style="color: ${getRegimeColor(stock.regime)};">${stock.regime}</span></div>
                        </div>
                        <div style="text-align: right;">
                            <div style="color: #fff; font-size: 14px; font-weight: 600;">₹${stock.price.toFixed(2)}</div>
                            <div style="color: ${stock.change_pct >= 0 ? '#10b981' : '#ef4444'}; font-size: 13px; font-weight: 600;">
                                ${stock.change_pct >= 0 ? '+' : ''}${stock.change_pct.toFixed(2)}%
                            </div>
                            <div style="color: #f59e0b; font-size: 12px; font-weight: 600;">Vol: ${(stock.volatility * 100).toFixed(2)}%</div>
                        </div>
                    </div>
                `).join('')}
            </div>
        </div>
    `;
}

// Heatmap View Renderer
function renderHeatmapView(response) {
    const output = document.getElementById('detailView');
    const { heatmap_type, data } = response;

    if (heatmap_type === 'sector') {
        renderSectorHeatmap(output, data);
    } else if (heatmap_type === 'market' || heatmap_type === 'volume') {
        renderMarketHeatmap(output, data, heatmap_type);
    }
}

function renderSectorHeatmap(output, heatmapData) {
    output.innerHTML = `
        <div style="background: rgba(31,41,55,0.9); border: 1px solid #374151; border-radius: 8px; padding: 20px;">
            <div style="color: #10b981; font-size: 24px; font-weight: 700; margin-bottom: 20px;">
                🗺️ Sector Performance Heatmap
            </div>
            
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
                ${heatmapData.data.map(sector => `
                    <div style="
                        background: ${getHeatmapColor(sector.color_class, sector.intensity)};
                        border: 2px solid ${getHeatmapBorder(sector.color_class)};
                        border-radius: 8px;
                        padding: 20px;
                        text-align: center;
                        transition: transform 0.2s;
                        cursor: pointer;
                    " onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">
                        <div style="color: #fff; font-size: 14px; font-weight: 600; margin-bottom: 8px;">${sector.sector}</div>
                        <div style="color: #fff; font-size: 24px; font-weight: 700; font-family: 'Roboto Mono', monospace;">
                            ${sector.display_value}
                        </div>
                    </div>
                `).join('')}
            </div>
        </div>
    `;
}

function renderMarketHeatmap(output, heatmapData, type) {
    const gridSize = heatmapData.grid_size;

    output.innerHTML = `
        <div style="background: rgba(31,41,55,0.9); border: 1px solid #374151; border-radius: 8px; padding: 20px;">
            <div style="color: #10b981; font-size: 24px; font-weight: 700; margin-bottom: 20px;">
                🗺️ ${type === 'volume' ? 'Volume' : 'Market'} Heatmap
            </div>
            
            <div style="display: grid; grid-template-columns: repeat(${gridSize[1]}, 1fr); gap: 10px;">
                ${heatmapData.data.map(stock => `
                    <div style="
                        background: ${getHeatmapColor(stock.color_class, stock.intensity)};
                        border: 1px solid ${getHeatmapBorder(stock.color_class)};
                        border-radius: 6px;
                        padding: 12px;
                        text-align: center;
                        min-height: 80px;
                        display: flex;
                        flex-direction: column;
                        justify-content: center;
                        transition: transform 0.2s;
                        cursor: pointer;
                    " onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'" onclick="executeCommand('QUOTE ${stock.symbol}')">
                        <div style="color: #fff; font-size: 12px; font-weight: 600; margin-bottom: 4px;">${stock.symbol}</div>
                        <div style="color: #fff; font-size: 16px; font-weight: 700; font-family: 'Roboto Mono', monospace; margin-bottom: 4px;">
                            ${stock.display_value}
                        </div>
                        <div style="color: #9ca3af; font-size: 10px;">₹${stock.price.toFixed(2)}</div>
                    </div>
                `).join('')}
            </div>
        </div>
    `;
}

// Correlation Matrix View
function renderCorrelationView(response) {
    const output = document.getElementById('detailView');
    const { data } = response;

    output.innerHTML = `
        <div style="background: rgba(31,41,55,0.9); border: 1px solid #374151; border-radius: 8px; padding: 20px;">
            <div style="color: #10b981; font-size: 24px; font-weight: 700; margin-bottom: 20px;">
                🔗 Correlation Matrix
            </div>
            
            <div style="overflow-x: auto;">
                <table style="width: 100%; border-collapse: collapse;">
                    <thead>
                        <tr>
                            <th style="padding: 10px; border: 1px solid #374151; background: rgba(17,24,39,0.5); color: #9ca3af; font-size: 12px;"></th>
                            ${data.symbols.map(sym => `
                                <th style="padding: 10px; border: 1px solid #374151; background: rgba(17,24,39,0.5); color: #9ca3af; font-size: 11px;">${sym.replace('.NS', '')}</th>
                            `).join('')}
                        </tr>
                    </thead>
                    <tbody>
                        ${data.data.map(row => `
                            <tr>
                                <td style="padding: 10px; border: 1px solid #374151; background: rgba(17,24,39,0.5); color: #9ca3af; font-size: 11px; font-weight: 600;">${row.symbol.replace('.NS', '')}</td>
                                ${row.correlations.map(corr => `
                                    <td style="
                                        padding: 10px;
                                        border: 1px solid #374151;
                                        background: ${getCorrelationColor(corr.value, corr.intensity)};
                                        color: #fff;
                                        text-align: center;
                                        font-size: 11px;
                                        font-weight: 600;
                                        font-family: 'Roboto Mono', monospace;
                                    ">${corr.display}</td>
                                `).join('')}
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
            
            <div style="margin-top: 20px; padding: 15px; background: rgba(17,24,39,0.5); border: 1px solid #374151; border-radius: 6px;">
                <div style="color: #9ca3af; font-size: 12px; margin-bottom: 10px;">Legend:</div>
                <div style="display: flex; gap: 15px; flex-wrap: wrap;">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <div style="width: 20px; height: 20px; background: rgba(16,185,129,0.8); border-radius: 3px;"></div>
                        <span style="color: #9ca3af; font-size: 11px;">Strong Positive (&gt;0.5)</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <div style="width: 20px; height: 20px; background: rgba(239,68,68,0.8); border-radius: 3px;"></div>
                        <span style="color: #9ca3af; font-size: 11px;">Strong Negative (&lt;-0.5)</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <div style="width: 20px; height: 20px; background: rgba(107,114,128,0.3); border-radius: 3px;"></div>
                        <span style="color: #9ca3af; font-size: 11px;">Weak Correlation</span>
                    </div>
                </div>
            </div>
        </div>
    `;
}

// Helper Functions
function getRegimeColor(regime) {
    const colors = {
        'LOW_VOL': 'rgba(16,185,129,0.2)',
        'MEDIUM_VOL': 'rgba(245,158,11,0.2)',
        'HIGH_VOL': 'rgba(239,68,68,0.2)',
        'UNKNOWN': 'rgba(107,114,128,0.2)'
    };
    return colors[regime] || colors['UNKNOWN'];
}

function getRegimeBorder(regime) {
    const colors = {
        'LOW_VOL': '#10b981',
        'MEDIUM_VOL': '#f59e0b',
        'HIGH_VOL': '#ef4444',
        'UNKNOWN': '#6b7280'
    };
    return colors[regime] || colors['UNKNOWN'];
}

function renderMetricCard(label, value, color) {
    return `
        <div style="background: rgba(17,24,39,0.5); border: 1px solid #374151; border-radius: 6px; padding: 12px;">
            <div style="color: #9ca3af; font-size: 11px; margin-bottom: 6px;">${label}</div>
            <div style="color: ${color}; font-size: 18px; font-weight: 700; font-family: 'Roboto Mono', monospace;">${value}</div>
        </div>
    `;
}

function getHeatmapColor(colorClass, intensity) {
    const baseColors = {
        'green': `rgba(16,185,129,${intensity * 0.8})`,
        'red': `rgba(239,68,68,${intensity * 0.8})`,
        'blue': `rgba(59,130,246,${intensity * 0.8})`,
        'orange': `rgba(245,158,11,${intensity * 0.8})`,
        'neutral': 'rgba(107,114,128,0.3)'
    };
    return baseColors[colorClass] || baseColors['neutral'];
}

function getHeatmapBorder(colorClass) {
    const colors = {
        'green': '#10b981',
        'red': '#ef4444',
        'blue': '#3b82f6',
        'orange': '#f59e0b',
        'neutral': '#6b7280'
    };
    return colors[colorClass] || colors['neutral'];
}

function getCorrelationColor(value, intensity) {
    if (value > 0.5) return `rgba(16,185,129,${intensity})`;
    if (value < -0.5) return `rgba(239,68,68,${intensity})`;
    if (value > 0) return `rgba(59,130,246,${intensity * 0.5})`;
    return `rgba(107,114,128,${intensity * 0.3})`;
}

// Add these case handlers to the main executeCommand response switch statement:
/*
case 'VOLATILITY_VIEW':
    renderVolatilityView(response);
    break;

case 'VOLSCAN_VIEW':
    renderVolScanView(response);
    break;

case 'HEATMAP_VIEW':
    renderHeatmapView(response);
    break;

case 'CORRELATION_VIEW':
    renderCorrelationView(response);
    break;
*/
