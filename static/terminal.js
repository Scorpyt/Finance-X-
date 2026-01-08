document.addEventListener('DOMContentLoaded', () => {
    const cmdInput = document.getElementById('cmdInput');
    const marketList = document.getElementById('marketList');
    const eventLog = document.getElementById('eventLog');
    const detailView = document.getElementById('detailView');
    const mainChart = document.getElementById('mainChart');
    const ctx = mainChart.getContext('2d');

    // State
    let activeMode = 'LANDING'; // 'LANDING', 'CHART', 'MAP_CANVAS', 'MAP_HD'
    let activeSymbol = 'SPX';
    let chartData = [];
    let chartBands = null;
    let mapAssets = [];
    let mapTitle = "GLOBAL ASSET MAP";

    // Leaflet Map
    let leafletMap = null;
    let vesselMarkers = [];

    // Landing page data
    let landingData = null;

    // Locomotive Scroll instance
    let locomotiveScroll = null;

    // Auto-focus logic
    cmdInput.focus();
    document.addEventListener('click', () => cmdInput.focus());

    // Init
    resizeChart();
    window.addEventListener('resize', resizeChart);

    // Polling Loop
    setInterval(updateMarketData, 10000);
    setInterval(updateSystemState, 15000);
    setInterval(updateLandingPage, 30000); // Update landing every 30s
    updateMarketData();
    updateSystemState();
    updateLandingPage(); // Load landing page data on init

    // Navigation buttons
    const btnOverview = document.getElementById('btnOverview');
    const btnTankerMap = document.getElementById('btnTankerMap');
    const btnMarketMap = document.getElementById('btnMarketMap');

    if (btnOverview) {
        btnOverview.addEventListener('click', () => {
            disableTankerAnalysisMode();
            switchView('LANDING');

            // Scroll landing page to top
            const landingView = document.getElementById('landingView');
            if (landingView) {
                landingView.scrollTop = 0;
            }

            // Always fetch fresh landing page data
            updateLandingPage();
        });
    }

    // Dual Map System
    let mapMode = null; // 'TANKER' or 'MARKET'
    let marketData = [];

    if (btnTankerMap) {
        btnTankerMap.addEventListener('click', async () => {
            if (mapAssets.length === 0) {
                console.log('[Tanker Map] Loading vessel data...');
                await executeCommand('TANKERS');
                await new Promise(resolve => setTimeout(resolve, 500));
            }
            mapMode = 'TANKER';
            switchView('MAP_HD');

            // Enable full-screen analysis mode
            enableTankerAnalysisMode();

            // Force map to fit container
            setTimeout(() => {
                if (leafletMap) leafletMap.invalidateSize();
                renderTankerMap();
                updateTankerRiskMetrics();
            }, 100);
        });
    }

    if (btnMarketMap) {
        btnMarketMap.addEventListener('click', async () => {
            console.log('[Market Map] Loading market data...');
            await executeCommand('MARKETS');
            await new Promise(resolve => setTimeout(resolve, 500));
            mapMode = 'MARKET';
            switchView('MAP_HD');

            // Force map to fit container
            setTimeout(() => {
                if (leafletMap) leafletMap.invalidateSize();
                renderMarketMap();
            }, 100);
        });
    }

    // Water Risk Toggle
    let waterRiskEnabled = false;
    let waterRiskMarkers = [];
    const btnWaterRisk = document.getElementById('btnWaterRisk');

    if (btnWaterRisk) {
        btnWaterRisk.addEventListener('click', () => {
            waterRiskEnabled = !waterRiskEnabled;

            // Update button style
            if (waterRiskEnabled) {
                btnWaterRisk.style.background = '#1f2937';
                btnWaterRisk.style.color = '#3b82f6';
                btnWaterRisk.style.borderColor = '#3b82f6';
                loadWaterRiskData();
            } else {
                btnWaterRisk.style.background = '#111';
                btnWaterRisk.style.color = '#6b7280';
                btnWaterRisk.style.borderColor = '#374151';
                clearWaterRiskOverlay();
            }
        });
    }


    // View switching function
    function switchView(mode) {
        activeMode = mode;
        const landingView = document.getElementById('landingView');
        const chartCanvas = document.getElementById('mainChart');
        const leafletMapEl = document.getElementById('leafletMap');

        // Hide all views
        landingView.style.display = 'none';
        chartCanvas.style.display = 'none';
        leafletMapEl.style.display = 'none';

        // Update button states
        updateButtonStates(mode);

        // Show active view
        if (mode === 'LANDING') {
            landingView.style.display = 'block';
            document.getElementById('chartSymbol').innerText = 'MARKET OVERVIEW';
            // Initialize Locomotive Scroll for landing page
            setTimeout(() => initLocomotiveScroll(), 100);
        } else if (mode === 'CHART') {
            chartCanvas.style.display = 'block';
            document.getElementById('chartSymbol').innerText = activeSymbol;
            // Destroy Locomotive Scroll when not on landing page
            destroyLocomotiveScroll();
        } else if (mode === 'MAP_HD') {
            leafletMapEl.style.display = 'block';
            if (!leafletMap) initLeafletMap();
            document.getElementById('chartSymbol').innerText = mapMode === 'TANKER' ? 'TANKER MAP' : 'MARKET MAP';
            // Destroy Locomotive Scroll when not on landing page
            destroyLocomotiveScroll();
        }
    }

    function updateButtonStates(mode) {
        const buttons = {
            'LANDING': btnOverview,
            'MAP_HD': mapMode === 'TANKER' ? btnTankerMap : btnMarketMap
        };

        // Reset all buttons
        [btnOverview, btnTankerMap, btnMarketMap].forEach(btn => {
            if (btn) {
                btn.style.background = '#111';
                btn.style.color = '#6b7280';
                btn.style.borderColor = '#374151';
                btn.style.fontWeight = '400';
            }
        });

        // Highlight active button
        const activeBtn = buttons[mode];
        if (activeBtn) {
            activeBtn.style.background = '#1f2937';
            activeBtn.style.color = '#10b981';
            activeBtn.style.borderColor = '#10b981';
            activeBtn.style.fontWeight = '600';
        }
    }

    // Tanker Analysis Mode - Full Screen
    function enableTankerAnalysisMode() {
        // Hide terminal elements
        const sidebar = document.querySelector('.sidebar');
        const eventLog = document.querySelector('.event-log');
        const detailView = document.querySelector('.detail-view');
        const commandBar = document.querySelector('.command-bar');
        const header = document.querySelector('.header');

        if (sidebar) sidebar.style.display = 'none';
        if (eventLog) eventLog.style.display = 'none';
        if (detailView) detailView.style.display = 'none';
        if (commandBar) commandBar.style.display = 'none';
        if (header) header.style.display = 'none';

        // Show analysis panel
        const analysisPanel = document.getElementById('tankerAnalysisPanel');
        if (analysisPanel) analysisPanel.style.display = 'block';

        // Make chart area full screen
        const chartArea = document.querySelector('.chart-area');
        if (chartArea) {
            chartArea.style.gridColumn = '1 / -1';
            chartArea.style.height = '100vh';
        }

        console.log('[Tanker Analysis] Full-screen mode enabled');
    }

    function disableTankerAnalysisMode() {
        // Show terminal elements
        const sidebar = document.querySelector('.sidebar');
        const eventLog = document.querySelector('.event-log');
        const detailView = document.querySelector('.detail-view');
        const commandBar = document.querySelector('.command-bar');
        const header = document.querySelector('.header');

        if (sidebar) sidebar.style.display = 'block';
        if (eventLog) eventLog.style.display = 'block';
        if (detailView) detailView.style.display = 'block';
        if (commandBar) commandBar.style.display = 'flex';
        if (header) header.style.display = 'flex';

        // Hide analysis panel
        const analysisPanel = document.getElementById('tankerAnalysisPanel');
        if (analysisPanel) analysisPanel.style.display = 'none';

        // Reset chart area
        const chartArea = document.querySelector('.chart-area');
        if (chartArea) {
            chartArea.style.gridColumn = '';
            chartArea.style.height = '';
        }

        console.log('[Tanker Analysis] Full-screen mode disabled');
    }

    // Locomotive Scroll initialization
    function initLocomotiveScroll() {
        // Destroy existing instance if any
        if (locomotiveScroll) {
            locomotiveScroll.destroy();
            locomotiveScroll = null;
        }

        // Initialize Locomotive Scroll on landing view
        const scrollContainer = document.querySelector('[data-scroll-container]');
        if (scrollContainer && typeof LocomotiveScroll !== 'undefined') {
            locomotiveScroll = new LocomotiveScroll({
                el: scrollContainer,
                smooth: true,
                multiplier: 1.0,
                lerp: 0.1,
                smartphone: {
                    smooth: true
                },
                tablet: {
                    smooth: true
                }
            });

            console.log('[Locomotive Scroll] Initialized');
        }
    }

    function destroyLocomotiveScroll() {
        if (locomotiveScroll) {
            locomotiveScroll.destroy();
            locomotiveScroll = null;
            console.log('[Locomotive Scroll] Destroyed');
        }
    }

    function updateTankerRiskMetrics() {
        if (!mapAssets || mapAssets.length === 0) return;

        // Calculate risk metrics from tanker movements
        const metrics = calculateTankerRisk(mapAssets);

        const metricsPanel = document.getElementById('tankerMetrics');
        if (!metricsPanel) return;

        metricsPanel.innerHTML = `
            <div style="margin-bottom: 14px;">
                <div style="color: #9ca3af; font-size: 10px; margin-bottom: 4px; font-weight: 500;">SUPPLY FLOW RISK</div>
                <div style="display: flex; align-items: center; gap: 8px;">
                    <div style="flex: 1; height: 8px; background: #1f2937; border-radius: 4px; overflow: hidden;">
                        <div style="width: ${metrics.supplyRisk}%; height: 100%; background: ${getRiskColor(metrics.supplyRisk)}; transition: width 0.3s;"></div>
                    </div>
                    <div style="color: ${getRiskColor(metrics.supplyRisk)}; font-size: 14px; font-weight: 700; font-family: 'Roboto Mono', monospace; min-width: 45px;">${metrics.supplyRisk}%</div>
                </div>
            </div>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 14px;">
                <div style="background: rgba(16,185,129,0.1); border: 1px solid #10b98140; border-radius: 4px; padding: 10px; text-align: center;">
                    <div style="color: #6b7280; font-size: 9px; margin-bottom: 4px;">MOVING</div>
                    <div style="color: #10b981; font-size: 18px; font-weight: 700; font-family: 'Roboto Mono', monospace;">${metrics.moving}</div>
                </div>
                <div style="background: rgba(245,158,11,0.1); border: 1px solid #f59e0b40; border-radius: 4px; padding: 10px; text-align: center;">
                    <div style="color: #6b7280; font-size: 9px; margin-bottom: 4px;">ANCHORED</div>
                    <div style="color: #f59e0b; font-size: 18px; font-weight: 700; font-family: 'Roboto Mono', monospace;">${metrics.anchored}</div>
                </div>
            </div>
            
            <div style="background: rgba(31,41,55,0.5); border: 1px solid #374151; border-radius: 6px; padding: 12px; margin-bottom: 14px;">
                <div style="color: #10b981; font-size: 11px; font-weight: 600; margin-bottom: 8px;">CARGO ANALYSIS</div>
                ${Object.entries(metrics.cargoBreakdown).map(([cargo, count]) => `
                    <div style="display: flex; justify-content: space-between; padding: 4px 0; border-bottom: 1px solid #1f2937;">
                        <span style="color: #9ca3af; font-size: 10px;">${cargo}</span>
                        <span style="color: #e5e7eb; font-size: 10px; font-weight: 600;">${count} vessels</span>
                    </div>
                `).join('')}
            </div>
            
            <div style="background: rgba(31,41,55,0.5); border: 1px solid #374151; border-radius: 6px; padding: 12px; margin-bottom: 14px;">
                <div style="color: #3b82f6; font-size: 11px; font-weight: 600; margin-bottom: 8px;">TOP ROUTES</div>
                ${metrics.topRoutes.map((route, idx) => `
                    <div style="display: flex; justify-content: space-between; padding: 4px 0; border-bottom: 1px solid #1f2937;">
                        <span style="color: #9ca3af; font-size: 9px;">${route.origin} → ${route.dest}</span>
                        <span style="color: #3b82f6; font-size: 10px; font-weight: 600;">${route.count}</span>
                    </div>
                `).join('')}
            </div>
            
            <div style="background: ${metrics.priceImpact >= 0 ? 'rgba(239,68,68,0.1)' : 'rgba(16,185,129,0.1)'}; border: 1px solid ${metrics.priceImpact >= 0 ? '#ef444440' : '#10b98140'}; border-radius: 6px; padding: 12px;">
                <div style="color: #9ca3af; font-size: 10px; margin-bottom: 4px;">ESTIMATED PRICE IMPACT</div>
                <div style="color: ${metrics.priceImpact >= 0 ? '#ef4444' : '#10b981'}; font-size: 20px; font-weight: 700; font-family: 'Roboto Mono', monospace;">
                    ${metrics.priceImpact >= 0 ? '+' : ''}${metrics.priceImpact.toFixed(2)}%
                </div>
                <div style="color: #6b7280; font-size: 9px; margin-top: 4px;">Based on supply flow</div>
            </div>
        `;
    }

    function calculateTankerRisk(tankers) {
        const moving = tankers.filter(t => t.status === 'MOVING').length;
        const anchored = tankers.filter(t => t.status === 'ANCHORED').length;
        const total = tankers.length;

        // Calculate supply risk (higher when more anchored)
        const supplyRisk = Math.round((anchored / total) * 100);

        // Cargo breakdown
        const cargoBreakdown = {};
        tankers.forEach(t => {
            const cargo = t.cargo_grade || 'UNKNOWN';
            cargoBreakdown[cargo] = (cargoBreakdown[cargo] || 0) + 1;
        });

        // Top routes
        const routeMap = {};
        tankers.forEach(t => {
            if (t.origin_port && t.dest) {
                const routeKey = `${t.origin_port}-${t.dest}`;
                if (!routeMap[routeKey]) {
                    routeMap[routeKey] = {
                        origin: t.origin_port,
                        dest: t.dest,
                        count: 0
                    };
                }
                routeMap[routeKey].count++;
            }
        });
        const topRoutes = Object.values(routeMap)
            .sort((a, b) => b.count - a.count)
            .slice(0, 5);

        // Estimate price impact (simplified)
        // More anchored = supply disruption = price increase
        // More moving = supply flowing = price decrease
        const priceImpact = (anchored - moving) / total * 5; // Scale to ±5%

        return {
            supplyRisk,
            moving,
            anchored,
            cargoBreakdown,
            topRoutes,
            priceImpact
        };
    }

    function getRiskColor(risk) {
        if (risk >= 70) return '#ef4444'; // High risk - red
        if (risk >= 40) return '#f59e0b'; // Medium risk - amber
        return '#10b981'; // Low risk - green
    }

    // Comprehensive Vessel Investment Analysis
    function updateVesselInvestmentAnalysis(tanker) {
        const metricsPanel = document.getElementById('tankerMetrics');
        if (!metricsPanel) return;

        // Calculate investment impact
        const analysis = calculateInvestmentImpact(tanker);
        const statusColor = tanker.status === 'MOVING' ? '#10b981' : '#f59e0b';

        metricsPanel.innerHTML = `
            <!-- Vessel Header -->
            <div style="background: linear-gradient(135deg, rgba(16,185,129,0.1), rgba(59,130,246,0.1)); border: 1px solid ${statusColor}; border-radius: 6px; padding: 12px; margin-bottom: 14px;">
                <div style="color: ${statusColor}; font-size: 16px; font-weight: 700; margin-bottom: 6px;">
                    ${tanker.origin_flag} ${tanker.name}
                </div>
                <div style="color: #9ca3af; font-size: 10px;">
                    ${tanker.vessel_type} | ${tanker.dwt.toLocaleString()} DWT | ${tanker.cargo_grade}
                </div>
            </div>
            
            <!-- Investment Impact Overview -->
            <div style="background: ${analysis.impact >= 0 ? 'rgba(239,68,68,0.15)' : 'rgba(16,185,129,0.15)'}; border: 2px solid ${analysis.impact >= 0 ? '#ef4444' : '#10b981'}; border-radius: 6px; padding: 14px; margin-bottom: 14px;">
                <div style="color: #9ca3af; font-size: 10px; margin-bottom: 6px; font-weight: 500;">💰 INVESTMENT IMPACT</div>
                <div style="color: ${analysis.impact >= 0 ? '#ef4444' : '#10b981'}; font-size: 28px; font-weight: 700; font-family: 'Roboto Mono', monospace; margin-bottom: 6px;">
                    ${analysis.impact >= 0 ? '+' : ''}${analysis.impact.toFixed(2)}%
                </div>
                <div style="color: #e5e7eb; font-size: 11px; line-height: 1.5;">
                    ${analysis.impactDescription}
                </div>
            </div>
            
            <!-- Route & Status -->
            <div style="background: rgba(31,41,55,0.5); border: 1px solid #374151; border-radius: 6px; padding: 12px; margin-bottom: 14px;">
                <div style="color: #3b82f6; font-size: 11px; font-weight: 600; margin-bottom: 8px;">📍 ROUTE DETAILS</div>
                <div style="display: grid; grid-template-columns: auto 1fr; gap: 6px 10px; font-size: 10px;">
                    <span style="color: #6b7280;">Origin:</span>
                    <span style="color: #e5e7eb;">${tanker.origin_flag} ${tanker.origin_port}, ${tanker.origin_country}</span>
                    
                    <span style="color: #6b7280;">Destination:</span>
                    <span style="color: #e5e7eb;">${tanker.destination_flag} ${tanker.dest}, ${tanker.destination_country}</span>
                    
                    <span style="color: #6b7280;">ETA:</span>
                    <span style="color: ${statusColor}; font-weight: 600;">${tanker.eta_hours} hours</span>
                    
                    <span style="color: #6b7280;">Speed:</span>
                    <span style="color: ${statusColor}; font-weight: 600;">${tanker.speed_knots} knots</span>
                    
                    <span style="color: #6b7280;">Status:</span>
                    <span style="color: ${statusColor}; font-weight: 600;">${tanker.status}</span>
                </div>
            </div>
            
            <!-- Proof & Evidence -->
            <div style="background: rgba(31,41,55,0.5); border: 1px solid #374151; border-radius: 6px; padding: 12px; margin-bottom: 14px;">
                <div style="color: #fbbf24; font-size: 11px; font-weight: 600; margin-bottom: 8px;">📊 PROOF & EVIDENCE</div>
                ${analysis.proof.map(item => `
                    <div style="padding: 6px 0; border-bottom: 1px solid #1f2937;">
                        <div style="color: #e5e7eb; font-size: 10px; font-weight: 600; margin-bottom: 2px;">✓ ${item.title}</div>
                        <div style="color: #9ca3af; font-size: 9px;">${item.detail}</div>
                    </div>
                `).join('')}
            </div>
            
            <!-- Risk Assessment -->
            <div style="background: rgba(31,41,55,0.5); border: 1px solid #374151; border-radius: 6px; padding: 12px; margin-bottom: 14px;">
                <div style="color: #ef4444; font-size: 11px; font-weight: 600; margin-bottom: 8px;">⚠️ RISK ASSESSMENT</div>
                <div style="margin-bottom: 8px;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                        <span style="color: #9ca3af; font-size: 9px;">Overall Risk</span>
                        <span style="color: ${getRiskColor(analysis.riskScore)}; font-size: 10px; font-weight: 700;">${analysis.riskScore}%</span>
                    </div>
                    <div style="height: 6px; background: #1f2937; border-radius: 3px; overflow: hidden;">
                        <div style="width: ${analysis.riskScore}%; height: 100%; background: ${getRiskColor(analysis.riskScore)}; transition: width 0.3s;"></div>
                    </div>
                </div>
                ${analysis.risks.map(risk => `
                    <div style="padding: 4px 0; border-bottom: 1px solid #1f2937;">
                        <div style="color: #ef4444; font-size: 9px;">⚡ ${risk}</div>
                    </div>
                `).join('')}
            </div>
            
            <!-- Actionable Recommendations -->
            <div style="background: linear-gradient(135deg, rgba(16,185,129,0.1), rgba(34,197,94,0.1)); border: 1px solid #10b981; border-radius: 6px; padding: 12px;">
                <div style="color: #10b981; font-size: 11px; font-weight: 600; margin-bottom: 8px;">💡 RECOMMENDATIONS</div>
                ${analysis.recommendations.map((rec, idx) => `
                    <div style="padding: 6px 0; ${idx < analysis.recommendations.length - 1 ? 'border-bottom: 1px solid #1f2937;' : ''}">
                        <div style="color: #e5e7eb; font-size: 10px; font-weight: 600; margin-bottom: 2px;">${idx + 1}. ${rec.action}</div>
                        <div style="color: #9ca3af; font-size: 9px;">${rec.reason}</div>
                        <div style="color: #10b981; font-size: 9px; margin-top: 2px;">💰 ${rec.benefit}</div>
                    </div>
                `).join('')}
            </div>
        `;
    }

    function calculateInvestmentImpact(tanker) {
        // Calculate impact based on cargo, route, and status
        let impact = 0;
        const proof = [];
        const risks = [];
        const recommendations = [];

        // Cargo impact
        const cargoMultiplier = {
            'WTI': 1.2,
            'Brent': 1.1,
            'Dubai': 1.0,
            'Maya': 0.9,
            'Urals': 0.8
        };
        const cargoImpact = (cargoMultiplier[tanker.cargo_grade] || 1.0) * (tanker.cargo_level / 100);

        // Status impact
        if (tanker.status === 'ANCHORED') {
            impact += 1.5; // Supply disruption = price increase
            proof.push({
                title: 'Supply Disruption Detected',
                detail: `Vessel anchored with ${tanker.cargo_level}% ${tanker.cargo_grade} cargo. Delayed delivery increases spot prices.`
            });
            risks.push('Prolonged anchorage may indicate port congestion or geopolitical issues');
            recommendations.push({
                action: 'Consider Long Position on Oil Futures',
                reason: 'Supply disruption typically drives prices up',
                benefit: 'Potential 2-3% gain if disruption persists'
            });
        } else {
            impact -= 0.8; // Supply flowing = price decrease
            proof.push({
                title: 'Normal Supply Flow',
                detail: `Vessel moving at ${tanker.speed_knots} knots. ETA ${tanker.eta_hours} hours. Supply chain functioning normally.`
            });
            recommendations.push({
                action: 'Monitor for Route Changes',
                reason: 'Smooth delivery reduces price volatility',
                benefit: 'Avoid unnecessary hedging costs'
            });
        }

        // Route impact (high-demand destinations)
        const highDemandPorts = ['Singapore', 'Rotterdam', 'Houston', 'Qingdao'];
        if (highDemandPorts.some(port => tanker.dest.includes(port))) {
            impact += 0.5;
            proof.push({
                title: 'High-Demand Destination',
                detail: `Destination ${tanker.dest} is a major trading hub. Delivery affects regional pricing.`
            });
        }

        // ETA impact
        if (tanker.eta_hours < 48) {
            proof.push({
                title: 'Imminent Delivery',
                detail: `Vessel arriving in ${tanker.eta_hours} hours. Short-term price impact expected.`
            });
            recommendations.push({
                action: 'Execute Short-Term Trades',
                reason: 'Delivery within 48 hours affects spot market',
                benefit: 'Capitalize on immediate price movements'
            });
        } else {
            recommendations.push({
                action: 'Position for Medium-Term',
                reason: `${tanker.eta_hours} hours until delivery allows strategic positioning`,
                benefit: 'Better entry points and reduced slippage'
            });
        }

        // Cargo grade impact
        proof.push({
            title: `${tanker.cargo_grade} Grade Analysis`,
            detail: `${tanker.cargo_grade} crude represents ${(cargoImpact * 100).toFixed(1)}% of current market demand. DWT: ${tanker.dwt.toLocaleString()}`
        });

        // Risk calculation
        let riskScore = 30; // Base risk
        if (tanker.status === 'ANCHORED') riskScore += 25;
        if (tanker.eta_hours > 100) riskScore += 15;
        if (tanker.cargo_level < 50) riskScore += 10;

        risks.push(`Cargo level at ${tanker.cargo_level}% - ${tanker.cargo_level < 70 ? 'Below optimal capacity' : 'Good utilization'}`);
        risks.push(`ETA ${tanker.eta_hours} hours - ${tanker.eta_hours > 100 ? 'Extended timeline increases uncertainty' : 'Reasonable delivery window'}`);

        // Final impact calculation
        impact = impact * cargoImpact;

        // Add time-saving recommendation
        recommendations.push({
            action: 'Set Price Alerts',
            reason: `Monitor ${tanker.cargo_grade} prices around ETA (${tanker.eta_hours}h)`,
            benefit: 'Save time by automating market monitoring'
        });

        return {
            impact,
            impactDescription: impact >= 0
                ? `This vessel's movement suggests upward price pressure on ${tanker.cargo_grade} crude.`
                : `This vessel's movement suggests downward price pressure on ${tanker.cargo_grade} crude.`,
            proof,
            risks,
            riskScore: Math.min(riskScore, 100),
            recommendations
        };
    }

    // Landing page data fetching and rendering
    async function updateLandingPage() {
        try {
            const res = await fetch('/api/v2/landing');
            landingData = await res.json();
            if (activeMode === 'LANDING') {
                renderLandingPage();
            }
        } catch (err) {
            console.error('Error loading landing page:', err);
        }
    }

    function renderLandingPage() {
        if (!landingData) return;

        const content = document.getElementById('landingContent');
        content.innerHTML = `
            <div style="font-family: 'Inter', sans-serif;">
                ${renderIndices(landingData.indices)}
                ${renderMovers(landingData.movers)}
                ${renderSectors(landingData.sectors)}
                ${renderSummary(landingData.summary)}
            </div>
        `;

        // Update Locomotive Scroll after content changes
        if (locomotiveScroll && activeMode === 'LANDING') {
            setTimeout(() => {
                locomotiveScroll.update();
            }, 100);
        }
    }

    function renderIndices(indices) {
        if (!indices || indices.length === 0) return '';

        return `
            <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 20px;">
                ${indices.map(idx => {
            const color = idx.change_pct >= 0 ? '#10b981' : '#ef4444';
            const sign = idx.change_pct >= 0 ? '+' : '';
            return `
                        <div style="
                            background: linear-gradient(135deg, rgba(31,41,55,0.9), rgba(17,24,39,0.9));
                            border: 1px solid #374151;
                            border-radius: 6px;
                            padding: 14px;
                            cursor: pointer;
                        " onclick="executeCommand('CHART ${idx.symbol}')">
                            <div style="color: #9ca3af; font-size: 10px; font-weight: 500; margin-bottom: 4px;">${idx.name}</div>
                            <div style="color: #ffffff; font-size: 20px; font-weight: 700; font-family: 'Roboto Mono', monospace; margin-bottom: 6px;">
                                ${idx.price.toLocaleString()}
                            </div>
                            <div style="color: ${color}; font-size: 13px; font-weight: 600;">
                                ${sign}${idx.change.toFixed(2)} (${sign}${idx.change_pct.toFixed(2)}%)
                            </div>
                        </div>
                    `;
        }).join('')}
            </div>
        `;
    }

    function renderMovers(movers) {
        if (!movers) return '';

        return `
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 20px;">
                ${renderMoverColumn('Top Gainers', movers.gainers, '#10b981')}
                ${renderMoverColumn('Top Losers', movers.losers, '#ef4444')}
                ${renderMoverColumn('Most Active', movers.active, '#3b82f6')}
            </div>
        `;
    }

    function renderMoverColumn(title, stocks, color) {
        return `
            <div style="background: rgba(31,41,55,0.5); border: 1px solid #374151; border-radius: 6px; padding: 12px;">
                <div style="color: ${color}; font-size: 12px; font-weight: 600; margin-bottom: 10px; border-bottom: 1px solid #374151; padding-bottom: 6px;">
                    ${title}
                </div>
                ${stocks.map(stock => `
                    <div style="display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid #1f2937; cursor: pointer;" onclick="executeCommand('QUOTE ${stock.symbol}')">
                        <div>
                            <div style="color: #e5e7eb; font-size: 11px; font-weight: 600;">${stock.symbol}</div>
                            <div style="color: #6b7280; font-size: 9px;">${stock.name}</div>
                        </div>
                        <div style="text-align: right;">
                            <div style="color: #e5e7eb; font-size: 11px; font-family: 'Roboto Mono', monospace;">$${stock.price.toFixed(2)}</div>
                            <div style="color: ${stock.change_pct >= 0 ? '#10b981' : '#ef4444'}; font-size: 10px; font-weight: 600;">
                                ${stock.change_pct >= 0 ? '+' : ''}${stock.change_pct.toFixed(2)}%
                            </div>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }

    function renderSectors(sectors) {
        if (!sectors || sectors.length === 0) return '';

        return `
            <div style="background: rgba(31,41,55,0.5); border: 1px solid #374151; border-radius: 6px; padding: 12px; margin-bottom: 20px;">
                <div style="color: #10b981; font-size: 12px; font-weight: 600; margin-bottom: 10px;">Sector Performance</div>
                <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px;">
                    ${sectors.map(sector => {
            const color = sector.change_pct >= 0 ? '#10b981' : '#ef4444';
            const bgColor = sector.change_pct >= 0 ? 'rgba(16,185,129,0.1)' : 'rgba(239,68,68,0.1)';
            return `
                            <div style="background: ${bgColor}; border: 1px solid ${color}40; border-radius: 4px; padding: 8px; text-align: center;">
                                <div style="color: #9ca3af; font-size: 9px; margin-bottom: 4px;">${sector.name}</div>
                                <div style="color: ${color}; font-size: 13px; font-weight: 600; font-family: 'Roboto Mono', monospace;">
                                    ${sector.change_pct >= 0 ? '+' : ''}${sector.change_pct.toFixed(2)}%
                                </div>
                            </div>
                        `;
        }).join('')}
                </div>
            </div>
        `;
    }

    function renderSummary(summary) {
        if (!summary) return '';

        const vixColor = summary.vix > 20 ? '#ef4444' : summary.vix > 15 ? '#f59e0b' : '#10b981';

        return `
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px;">
                <div style="background: rgba(31,41,55,0.5); border: 1px solid #374151; border-radius: 6px; padding: 12px; text-align: center;">
                    <div style="color: #9ca3af; font-size: 10px; margin-bottom: 4px;">VIX (Volatility)</div>
                    <div style="color: ${vixColor}; font-size: 18px; font-weight: 700; font-family: 'Roboto Mono', monospace;">${summary.vix.toFixed(2)}</div>
                </div>
                <div style="background: rgba(31,41,55,0.5); border: 1px solid #374151; border-radius: 6px; padding: 12px; text-align: center;">
                    <div style="color: #9ca3af; font-size: 10px; margin-bottom: 4px;">Market Volume</div>
                    <div style="color: #3b82f6; font-size: 18px; font-weight: 700; font-family: 'Roboto Mono', monospace;">${(summary.volume / 1e9).toFixed(2)}B</div>
                </div>
                <div style="background: rgba(31,41,55,0.5); border: 1px solid #374151; border-radius: 6px; padding: 12px; text-align: center;">
                    <div style="color: #9ca3af; font-size: 10px; margin-bottom: 4px;">Market Status</div>
                    <div style="color: ${summary.market_state === 'REGULAR' ? '#10b981' : '#6b7280'}; font-size: 18px; font-weight: 700;">${summary.market_state}</div>
                </div>
            </div>
        `;
    }

    function initLeafletMap() {
        leafletMap = L.map('leafletMap', { center: [20, 0], zoom: 2 });
        L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
            attribution: '© OpenStreetMap © CartoDB'
        }).addTo(leafletMap);
        console.log('[HD Map] Initialized');

        // Force resize after initialization
        setTimeout(() => {
            if (leafletMap) leafletMap.invalidateSize();
        }, 100);
    }


    let activeRoute = null; // Track currently displayed route

    function renderTankerMap() {
        if (!leafletMap) return;
        vesselMarkers.forEach(m => leafletMap.removeLayer(m));
        vesselMarkers = [];

        // Remove active route if exists
        if (activeRoute) {
            leafletMap.removeLayer(activeRoute);
            activeRoute = null;
        }

        mapAssets.forEach(tanker => {
            // Vessel marker (smaller, cleaner)
            const icon = L.divIcon({
                html: `<div style="width:10px;height:10px;background:${tanker.status === 'MOVING' ? '#0f0' : '#fa0'};border-radius:50%;box-shadow:0 0 8px ${tanker.status === 'MOVING' ? '#0f0' : '#fa0'}"></div>`,
                iconSize: [10, 10],
                iconAnchor: [5, 5]
            });
            const marker = L.marker([tanker.lat, tanker.lon], { icon }).addTo(leafletMap);

            // Small persistent label with arrow, name, and speed
            const heading = tanker.heading || 0;
            const arrowChar = getArrowForHeading(heading);
            const statusColor = tanker.status === 'MOVING' ? '#10b981' : '#f59e0b'; // emerald-500 / amber-500
            const labelIcon = L.divIcon({
                html: `
                    <div style="
                        background: linear-gradient(135deg, rgba(17,24,39,0.95), rgba(31,41,55,0.95));
                        border: 1px solid ${statusColor};
                        color: #f3f4f6;
                        padding: 3px 8px;
                        font-family: 'Inter', -apple-system, sans-serif;
                        font-size: 10px;
                        font-weight: 500;
                        letter-spacing: 0.3px;
                        white-space: nowrap;
                        border-radius: 4px;
                        box-shadow: 0 2px 8px rgba(0,0,0,0.4), 0 0 0 1px rgba(255,255,255,0.05);
                        pointer-events: none;
                        backdrop-filter: blur(4px);
                    ">
                        <span style="color:${statusColor};font-size:12px;margin-right:4px;">${arrowChar}</span>
                        <span style="color:#e5e7eb;font-weight:600;">${tanker.name}</span>
                        <span style="color:#9ca3af;margin:0 4px;">|</span>
                        <span style="color:${statusColor};font-weight:500;">${tanker.speed_knots}kn</span>
                    </div>
                `,
                iconSize: [140, 24],
                iconAnchor: [-15, 12],
                className: 'vessel-label'
            });
            const label = L.marker([tanker.lat, tanker.lon], {
                icon: labelIcon,
                interactive: false
            }).addTo(leafletMap);

            // Click handler - show route and investment analysis
            marker.on('click', () => {
                // Remove previous route
                if (activeRoute) {
                    leafletMap.removeLayer(activeRoute);
                }

                // Draw trade route (red polyline)
                if (tanker.origin_lat && tanker.dest_lat) {
                    activeRoute = L.polyline([
                        [tanker.origin_lat, tanker.origin_lon],
                        [tanker.lat, tanker.lon],
                        [tanker.dest_lat, tanker.dest_lon]
                    ], {
                        color: 'red',
                        weight: 3,
                        opacity: 0.8,
                        dashArray: '10, 5'
                    }).addTo(leafletMap);

                    // Add origin and destination markers
                    const originMarker = L.circleMarker([tanker.origin_lat, tanker.origin_lon], {
                        radius: 6,
                        fillColor: '#00ff00',
                        color: '#fff',
                        weight: 2,
                        opacity: 1,
                        fillOpacity: 0.8
                    }).addTo(leafletMap);
                    originMarker.bindTooltip(`${tanker.origin_flag} ${tanker.origin_port}`, { permanent: true, direction: 'top' });

                    const destMarker = L.circleMarker([tanker.dest_lat, tanker.dest_lon], {
                        radius: 6,
                        fillColor: '#ff0000',
                        color: '#fff',
                        weight: 2,
                        opacity: 1,
                        fillOpacity: 0.8
                    }).addTo(leafletMap);
                    destMarker.bindTooltip(`${tanker.destination_flag} ${tanker.dest}`, { permanent: true, direction: 'top' });

                    // Store route with markers for cleanup
                    activeRoute = L.layerGroup([activeRoute, originMarker, destMarker]).addTo(leafletMap);
                }

                // Update analysis panel with comprehensive investment analysis
                updateVesselInvestmentAnalysis(tanker);
            });

            vesselMarkers.push(marker, label);
        });

        console.log(`[Tanker Map] Rendered ${mapAssets.length} vessels with on-demand routes`);
    }

    // Helper function to get arrow character based on heading
    function getArrowForHeading(heading) {
        if (heading >= 337.5 || heading < 22.5) return '↑';
        if (heading >= 22.5 && heading < 67.5) return '↗';
        if (heading >= 67.5 && heading < 112.5) return '→';
        if (heading >= 112.5 && heading < 157.5) return '↘';
        if (heading >= 157.5 && heading < 202.5) return '↓';
        if (heading >= 202.5 && heading < 247.5) return '↙';
        if (heading >= 247.5 && heading < 292.5) return '←';
        if (heading >= 292.5 && heading < 337.5) return '↖';
        return '●';
    }

    function renderMarketMap() {
        if (!leafletMap) return;
        vesselMarkers.forEach(m => leafletMap.removeLayer(m));
        vesselMarkers = [];

        if (!marketData || marketData.length === 0) return;

        marketData.forEach(market => {
            // Sentiment color
            let color = '#0af';
            if (market.sentiment === 'BULLISH') color = '#0f0';
            if (market.sentiment === 'BEARISH') color = '#f00';

            // Country card marker
            const icon = L.divIcon({
                html: `
                    <div style="background:rgba(0,0,0,0.9);border:2px solid ${color};padding:8px;font-family:Inconsolata;font-size:10px;min-width:120px;box-shadow:0 0 15px ${color};">
                        <div style="font-size:12px;font-weight:bold;color:${color};">${market.flag} ${market.country}</div>
                        <div style="color:#fff;margin-top:4px;">${market.index_name}</div>
                        <div style="color:${market.change_pct >= 0 ? '#0f0' : '#f00'};font-size:11px;font-weight:bold;">
                            ${market.current_value.toLocaleString()} (${market.change_pct >= 0 ? '+' : ''}${market.change_pct}%)
                        </div>
                        <div style="color:#888;font-size:9px;margin-top:4px;">${market.local_time} ${market.timezone.split('/')[1]}</div>
                        <div style="color:${market.is_open ? '#0f0' : '#f00'};font-size:9px;">${market.is_open ? '● OPEN' : '○ CLOSED'}</div>
                    </div>
                `,
                iconSize: [140, 90],
                className: 'market-card'
            });

            const marker = L.marker([market.lat, market.lon], { icon }).addTo(leafletMap);

            // Click handler - transfer to terminal
            marker.on('click', () => {
                console.log(`[Market Map] Loading ${market.country} market data...`);
                executeCommand(`QUOTE ${market.index_symbol}`);
                detailView.innerHTML = `
                    <div style="font-size:14px;font-weight:bold;margin-bottom:10px;">${market.flag} ${market.country} MARKET</div>
                    <div style="color:#0af;">INDEX: ${market.index_name}</div>
                    <div style="color:${market.change_pct >= 0 ? '#0f0' : '#f00'};font-size:16px;margin:8px 0;">
                        ${market.current_value.toLocaleString()} (${market.change_pct >= 0 ? '+' : ''}${market.change_pct}%)
                    </div>
                    <div>SENTIMENT: <span style="color:${color}">${market.sentiment}</span></div>
                    <div>LOCAL TIME: ${market.local_time} (${market.timezone})</div>
                    <div>STATUS: <span style="color:${market.is_open ? '#0f0' : '#f00'}">${market.is_open ? 'OPEN' : 'CLOSED'}</span></div>
                    <div style="margin-top:10px;color:#888;">Loading detailed market data...</div>
                `;
            });

            vesselMarkers.push(marker);

            // Regional sentiment overlay
            const circle = L.circle([market.lat, market.lon], {
                color: color,
                fillColor: color,
                fillOpacity: 0.1,
                radius: 1500000,
                weight: 1
            }).addTo(leafletMap);
            vesselMarkers.push(circle);
        });

        console.log(`[Market Map] Rendered ${marketData.length} markets`);
    }

    function renderHDMap() {
        if (mapMode === 'TANKER') renderTankerMap();
        else if (mapMode === 'MARKET') renderMarketMap();
    }

    // Command Input
    cmdInput.addEventListener('keydown', async (e) => {
        if (e.key === 'Enter') {
            const command = cmdInput.value;
            cmdInput.value = '';
            if (command.trim() === '') return;
            await executeCommand(command);
        }
    });

    function resizeChart() {
        mainChart.width = mainChart.parentElement.clientWidth;
        mainChart.height = mainChart.parentElement.clientHeight;
        renderMainView();
    }

    function renderMainView() {
        if (activeMode === 'CHART') drawChart();
        if (activeMode === 'MAP_CANVAS') drawMap();
        if (activeMode === 'MAP_HD') renderHDMap();
    }

    async function updateMarketData() {
        try {
            const res = await fetch('/market');
            const data = await res.json();

            marketList.innerHTML = data.map(ticker => {
                const colorClass = ticker.change >= 0 ? 'up' : 'down';
                const sign = ticker.change >= 0 ? '+' : '';
                return `
                <div class="dense-row" onclick="executeCommand('QUOTE ${ticker.symbol}')">
                    <span style="width: 40px; font-weight:bold">${ticker.symbol}</span>
                    <span style="flex-grow:1; text-align:right">${ticker.price.toFixed(2)}</span>
                    <span class="${colorClass}" style="width: 60px; text-align:right">${sign}${ticker.change.toFixed(2)}%</span>
                </div>`;
            }).join('');

            // Only silent update chart if in chart mode
            if (activeMode === 'CHART' && activeSymbol) {
                silentUpdateChart(activeSymbol);
            }
        } catch (err) { console.error(err); }
    }

    async function updateSystemState() {
        try {
            const res = await fetch('/status');
            const data = await res.json();
            document.getElementById('regimeDisplay').innerText = `REGIME: ${data.regime}`;
            document.getElementById('riskDisplay').innerText = `RISK: ${data.risk}`;

            // Fetch Log - wrapped in try-catch to prevent errors
            try {
                const logRes = await fetch('/command', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ command: 'TODAY' })
                });
                if (logRes.ok) {
                    const logData = await logRes.json();
                    if (logData.data) {
                        eventLog.innerHTML = logData.data.map(e =>
                            `[${e.Time}] ${e.Description} <span style="color:#555">(R:${e.Relevance})</span>`
                        ).join('\n');
                    }
                }
            } catch (logErr) {
                console.warn('Event log update failed:', logErr);
            }

        } catch (err) {
            console.warn('Status update failed:', err);
        }
    }

    async function silentUpdateChart(symbol) {
        try {
            const res = await fetch('/command', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ command: `CHART ${symbol}` })
            });
            const data = await res.json();
            if (data.type === 'CHART_FULL') {
                chartData = data.history;
                chartBands = data.bands || null;
                renderMainView();
            }
        } catch (e) { }
    }

    async function executeCommand(cmd) {
        detailView.innerHTML = "PROCESSING...";
        try {
            const res = await fetch('/command', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ command: cmd })
            });
            const data = await res.json();
            handleResponse(data);
        } catch (err) {
            detailView.innerText = "ERROR";
        }
    }

    function handleResponse(data) {
        if (data.type === 'QUOTE' || data.type === 'CHART_FULL') {
            activeMode = 'CHART';
            activeSymbol = data.symbol;
            document.getElementById('chartSymbol').innerText = data.symbol;
            if (data.history) chartData = data.history;
            if (data.bands) chartBands = data.bands;
            renderMainView();

            if (data.type === 'QUOTE') {
                detailView.innerHTML = `
                <div style="font-size: 14px; font-weight:bold; margin-bottom:10px">${data.title}</div>
                PRICE: ${data.price}<br>
                CHANGE: ${data.change}%<br>
                REGIME: ${document.getElementById('regimeDisplay').innerText}
                `;
            }
        }
        else if (data.type === 'MAP_DATA') {
            if (data.map_mode === 'MARKET') {
                // Market map data
                marketData = data.markets || [];
                document.getElementById('chartSymbol').innerText = "MARKET MAP";
                detailView.innerHTML = `
                <div style="font-size: 14px; font-weight:bold; margin-bottom:10px">${data.title}</div>
                TRACKING: ${marketData.length} GLOBAL MARKETS<br>
                CLICK COUNTRY CARD → LOAD MARKET DATA<br>
                <div style="margin-top:10px;color:#888;">Markets: USA, UK, Germany, Japan, China, India, Brazil</div>`;
            } else {
                // Tanker map data
                activeMode = 'MAP_CANVAS';
                mapAssets = data.assets || [];
                mapTitle = data.title;
                if (data.metrics) mapTitle += ` [${data.metrics}]`;
                document.getElementById('chartSymbol').innerText = "ASSET MAP";
                renderMainView();
                detailView.innerHTML = `
                <div style="font-size: 14px; font-weight:bold; margin-bottom:10px">${data.title}</div>
                STATUS: ACTIVE MONITORING<br>
                FLEET: ${mapAssets.length} VESSELS<br>
                LOGIC: SUPPLY CHAIN MONITORING ENABLED`;
            }
        }
        else if (data.type === 'NEWS_FEED') {
            let html = `<div style="font-size: 14px; font-weight:bold; margin-bottom:10px">${data.title}</div>`;
            data.data.forEach(item => {
                html += `
                <div style="margin-bottom:10px; border-bottom:1px solid #333; padding-bottom:5px">
                    <span style="color:#00aaff">${item.source} ${item.time}</span><br>
                    ${item.headline} <span style="color:#ff3300">[IMPACT: ${item.impact}]</span>
                </div>`;
            });
            detailView.innerHTML = html;
        }
        else if (data.type === 'TEXT' || data.type === 'REPORT' || data.type === 'SCAN') {
            detailView.innerHTML = `
            <div class="report-card">
                <div class="report-title">${data.title}</div>
                ${data.state ? `<div style="margin-bottom:10px">ANALYSIS: <span class="state-badge">${data.state}</span></div>` : ''}
                <div style="white-space: pre-wrap; line-height: 1.5;">${data.content || data.details}</div>
            </div>`;
        } else {
            detailView.innerText = JSON.stringify(data, null, 2);
        }
    }

    function drawChart() {
        if (!chartData.length) return;
        const w = mainChart.width;
        const h = mainChart.height;
        ctx.clearRect(0, 0, w, h);

        const prices = chartData.map(d => d.p);
        let min = Math.min(...prices);
        let max = Math.max(...prices);

        // Adjust scale for bands if present
        if (chartBands) {
            const lower = chartBands.lower.filter(v => v);
            const upper = chartBands.upper.filter(v => v);
            if (lower.length) min = Math.min(min, ...lower);
            if (upper.length) max = Math.max(max, ...upper);
        }

        min *= 0.999;
        max *= 1.001;
        const range = max - min;

        // 1. Draw Bollinger Bands (Area)
        if (chartBands && chartBands.upper.length) {
            ctx.beginPath();
            chartBands.upper.forEach((v, i) => {
                const x = (i / (chartData.length - 1)) * w;
                const y = h - ((v - min) / range) * h;
                if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
            });
            // Reverse down lower band
            for (let i = chartBands.lower.length - 1; i >= 0; i--) {
                const v = chartBands.lower[i];
                const x = (i / (chartData.length - 1)) * w;
                const y = h - ((v - min) / range) * h;
                ctx.lineTo(x, y);
            }
            ctx.closePath();
            ctx.fillStyle = 'rgba(0, 80, 200, 0.15)'; // Blue tint
            ctx.fill();

            // Draw Edges
            ctx.strokeStyle = 'rgba(0, 80, 200, 0.3)';
            ctx.stroke();
        }

        // 2. Draw Price Line
        ctx.beginPath();
        ctx.strokeStyle = '#00aaff';
        ctx.lineWidth = 2;
        chartData.forEach((d, i) => {
            const x = (i / (chartData.length - 1)) * w;
            const y = h - ((d.p - min) / range) * h;
            if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
        });
        ctx.stroke();

        // 3. Grid & Labels
        ctx.strokeStyle = '#222'; ctx.lineWidth = 1; ctx.beginPath();
        for (let i = 1; i < 5; i++) { const y = (i / 5) * h; ctx.moveTo(0, y); ctx.lineTo(w, y); }
        ctx.stroke();

        // Last Price
        const last = chartData[chartData.length - 1];
        const lastY = h - ((last.p - min) / range) * h;
        ctx.fillStyle = '#ff9900';
        ctx.font = '11px Inconsolata';
        ctx.fillText(last.p.toFixed(2), w - 50, lastY - 5);

        // Warning Disruption Marker if Breach
        if (chartBands && chartBands.upper.length) {
            const lastUpper = chartBands.upper[chartBands.upper.length - 1];
            if (last.p > lastUpper) {
                // Breach
                ctx.beginPath();
                ctx.arc(w - 10, lastY, 5, 0, Math.PI * 2);
                ctx.fillStyle = '#ff0000';
                ctx.fill();
                ctx.fillText("! DISRUPTION RISK", w - 120, lastY + 20);
            }
        }
    }

    function drawMap() {
        const w = mainChart.width;
        const h = mainChart.height;
        ctx.clearRect(0, 0, w, h);

        // Draw World Outline Style (Abstract)
        ctx.strokeStyle = '#222';
        ctx.lineWidth = 1;
        ctx.beginPath();
        for (let i = 1; i < 8; i++) { const x = (i / 8) * w; ctx.moveTo(x, 0); ctx.lineTo(x, h); }
        for (let i = 1; i < 6; i++) { const y = (i / 6) * h; ctx.moveTo(0, y); ctx.lineTo(w, y); }
        ctx.stroke();

        // Draw each tanker with RICH LABELS
        mapAssets.forEach(tanker => {
            const x = ((tanker.lon + 180) / 360) * w;
            const y = ((90 - tanker.lat) / 180) * h;

            // Vessel Dot (larger for visibility)
            ctx.fillStyle = tanker.status === 'MOVING' ? '#00ff00' : '#ffaa00';
            ctx.beginPath();
            ctx.arc(x, y, 4, 0, Math.PI * 2);
            ctx.fill();

            // Outer ring
            ctx.strokeStyle = tanker.status === 'MOVING' ? '#00ff00' : '#ffaa00';
            ctx.lineWidth = 1;
            ctx.stroke();

            // Heading Vector
            if (tanker.heading && tanker.status === 'MOVING') {
                const rad = (tanker.heading - 90) * (Math.PI / 180);
                ctx.strokeStyle = '#00ff00';
                ctx.lineWidth = 2;
                ctx.beginPath();
                ctx.moveTo(x, y);
                ctx.lineTo(x + Math.cos(rad) * 15, y + Math.sin(rad) * 15);
                ctx.stroke();
            }

            // RICH LABEL - Multi-line info box
            ctx.font = '9px Inconsolata';
            ctx.textAlign = 'left';

            const labelX = x + 10;
            let labelY = y - 40;

            // Build label lines
            const lines = [
                `${tanker.origin_flag || ''} ${tanker.name}`,
                `${tanker.cargo_grade || 'OIL'} (${tanker.cargo_level || 0}%)`,
                `${tanker.origin_port || 'ORIGIN'} → ${tanker.dest || 'DEST'}`,
                `${tanker.vessel_type || 'VLCC'} | ${tanker.speed_knots || 0}kn`
            ];

            // Measure max width
            let maxWidth = 0;
            lines.forEach(line => {
                const metrics = ctx.measureText(line);
                if (metrics.width > maxWidth) maxWidth = metrics.width;
            });

            // Draw semi-transparent background
            ctx.fillStyle = 'rgba(0, 0, 0, 0.85)';
            ctx.fillRect(labelX - 2, labelY - 10, maxWidth + 4, lines.length * 11 + 4);

            // Draw border
            ctx.strokeStyle = tanker.status === 'MOVING' ? '#00ff00' : '#ffaa00';
            ctx.lineWidth = 1;
            ctx.strokeRect(labelX - 2, labelY - 10, maxWidth + 4, lines.length * 11 + 4);

            // Draw text lines
            ctx.fillStyle = '#ffffff';
            lines.forEach((line, i) => {
                ctx.fillText(line, labelX, labelY + (i * 11));
            });
        });

        // Title Overlay
        ctx.fillStyle = '#fff';
        ctx.font = '14px Inconsolata';
        ctx.textAlign = 'left';
        ctx.fillText(mapTitle, 10, 20);

        // Legend
        ctx.font = '10px Inconsolata';
        ctx.fillStyle = '#00ff00';
        ctx.fillText('● MOVING', 10, h - 30);
        ctx.fillStyle = '#ffaa00';
        ctx.fillText('● ANCHORED', 10, h - 15);
    }

    window.executeCommand = executeCommand;
});
    
