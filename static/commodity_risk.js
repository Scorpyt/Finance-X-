// Commodity Risk Panel JavaScript
// Add this to terminal.js

// Commodity Risk Panel Toggle
const btnCommodityRisk = document.getElementById('btnCommodityRisk');
const commodityRiskPanel = document.getElementById('commodityRiskPanel');
const detailView = document.getElementById('detailView');
let commodityRiskVisible = false;

if (btnCommodityRisk) {
    btnCommodityRisk.addEventListener('click', () => {
        commodityRiskVisible = !commodityRiskVisible;

        if (commodityRiskVisible) {
            // Show commodity risk panel
            detailView.style.display = 'none';
            commodityRiskPanel.style.display = 'block';
            btnCommodityRisk.style.background = '#1f2937';
            btnCommodityRisk.style.color = '#10b981';
            btnCommodityRisk.style.borderColor = '#10b981';
            loadCommodityRiskData();
        } else {
            // Show detail view
            detailView.style.display = 'block';
            commodityRiskPanel.style.display = 'none';
            btnCommodityRisk.style.background = '#111';
            btnCommodityRisk.style.color = '#6b7280';
            btnCommodityRisk.style.borderColor = '#374151';
        }
    });
}

async function loadCommodityRiskData() {
    try {
        const response = await fetch('/api/v2/water-risk/commodities');
        const data = await response.json();

        if (data.regions) {
            renderCommodityRiskPanel(data.regions);
            console.log('[Commodity Risk] Loaded ' + data.regions.length + ' commodity regions');
        }
    } catch (error) {
        console.error('[Commodity Risk] Error loading data:', error);
        commodityRiskPanel.innerHTML = '<div style="color: #ef4444; padding: 20px;">Error loading commodity risk data</div>';
    }
}

function renderCommodityRiskPanel(regions) {
    const html = '<div style="font-family: Inter, sans-serif;">' +
        '<div style="margin-bottom: 16px; padding-bottom: 12px; border-bottom: 2px solid #10b981;">' +
        '<div style="color: #10b981; font-size: 14px; font-weight: 700;">COMMODITY WATER RISK ANALYSIS</div>' +
        '<div style="color: #9ca3af; font-size: 10px; margin-top: 4px;">Monitoring ' + regions.length + ' major production regions</div>' +
        '</div>' +
        regions.map(region => {
            const risk = region.risk_indicators;
            const riskColor = risk.risk_category === 'Extreme' ? '#ef4444' :
                risk.risk_category === 'High' ? '#f97316' :
                    risk.risk_category === 'Medium' ? '#eab308' : '#10b981';
            const alertColor = region.alert_level === 'Critical' ? '#ef4444' :
                region.alert_level === 'Warning' ? '#f59e0b' : '#6b7280';
            const trendIcon = region.trend === 'Deteriorating' ? '📉' :
                region.trend === 'Improving' ? '📈' : '➡️';

            return '<div style="background: linear-gradient(135deg, rgba(31,41,55,0.5), rgba(17,24,39,0.5)); border: 1px solid #374151; border-radius: 6px; padding: 12px; margin-bottom: 12px;">' +
                '<div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 8px;">' +
                '<div>' +
                '<div style="color: #e5e7eb; font-size: 12px; font-weight: 700; margin-bottom: 2px;">' + region.commodity + '</div>' +
                '<div style="color: #9ca3af; font-size: 9px;">' + region.region + ', ' + region.country + '</div>' +
                '</div>' +
                '<div style="text-align: right;">' +
                '<div style="background: ' + alertColor + '; color: #fff; padding: 2px 6px; border-radius: 3px; font-size: 8px; font-weight: 700; margin-bottom: 4px;">' + region.alert_level + '</div>' +
                '<div style="color: #9ca3af; font-size: 9px;">' + trendIcon + ' ' + region.trend + '</div>' +
                '</div>' +
                '</div>' +
                '<div style="background: rgba(0,0,0,0.3); border-radius: 4px; padding: 8px; margin-bottom: 8px;">' +
                '<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 6px; font-size: 9px;">' +
                '<div><span style="color: #9ca3af;">Water Stress:</span> <span style="color: ' + riskColor + '; font-weight: 600;">' + risk.baseline_water_stress.toFixed(2) + '/5.0</span></div>' +
                '<div><span style="color: #9ca3af;">Drought Risk:</span> <span style="color: ' + riskColor + '; font-weight: 600;">' + risk.drought_risk.toFixed(2) + '/5.0</span></div>' +
                '<div><span style="color: #9ca3af;">Flood Risk:</span> <span style="color: ' + riskColor + '; font-weight: 600;">' + risk.flood_risk.toFixed(2) + '/5.0</span></div>' +
                '<div><span style="color: #9ca3af;">2030 Outlook:</span> <span style="color: ' + riskColor + '; font-weight: 600;">' + risk.water_scarcity_2030.toFixed(2) + '/5.0</span></div>' +
                '</div>' +
                '</div>' +
                '<div style="display: flex; justify-content: space-between; align-items: center;">' +
                '<div style="color: #9ca3af; font-size: 9px;">Overall Risk Score</div>' +
                '<div style="color: ' + riskColor + '; font-size: 14px; font-weight: 700; font-family: Roboto Mono, monospace;">' + risk.overall_risk_score.toFixed(2) + '</div>' +
                '</div>' +
                '<div style="margin-top: 4px;">' +
                '<div style="height: 4px; background: #1f2937; border-radius: 2px; overflow: hidden;">' +
                '<div style="width: ' + (risk.overall_risk_score * 20) + '%; height: 100%; background: ' + riskColor + ';"></div>' +
                '</div>' +
                '</div>' +
                '</div>';
        }).join('') +
        '</div>';

    commodityRiskPanel.innerHTML = html;
}
