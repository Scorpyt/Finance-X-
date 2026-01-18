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
    let gridData = [];
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

    // AUTO-STARTUP SEQUENCE
    console.log("ðŸš€ BOOT SEQUENCE INITIATED...");
    setTimeout(() => {
        executeCommand('CHART SPX'); // Show Chart immediately
        executeCommand('risks');     // Update risk display
        executeCommand('news');      // Populate log
    }, 500);

    // Polling Loop - AGGRESSIVE REAL-TIME UPDATES
    setInterval(updateMarketData, 2000); // 2s polling for price updates
    setInterval(updateSystemState, 5000); // 5s for risk updates
    setInterval(() => {
        if (activeMode === 'CHART') {
            executeCommand(`CHART ${activeSymbol}`); // Auto-refresh active chart
        }
    }, 5000);

    updateMarketData();
    updateSystemState();
    updateLandingPage(); // Load landing page data on init

    // Navigation buttons
    const btnOverview = document.getElementById('btnOverview');
    const btnStudyInsights = document.getElementById('btnStudyInsights');
    const btnMarketMap = document.getElementById('btnMarketMap');
    const btnActions = document.getElementById('btnActions');

    const btnSysMarket = document.getElementById('btnSysMarket');
    const btnSysStudy = document.getElementById('btnSysStudy');
    const btnSysSecure = document.getElementById('btnSysSecure');

    function updateNavState(activeBtn) {
        [btnSysMarket, btnSysStudy, btnSysSecure].forEach(btn => {
            if (btn) btn.classList.remove('active-nav');
        });
        if (activeBtn) activeBtn.classList.add('active-nav');
    }

    if (btnSysMarket) {
        btnSysMarket.addEventListener('click', () => {
            updateNavState(btnSysMarket);
            executeCommand('NIFTY');
        });
    }

    if (btnSysStudy) {
        btnSysStudy.addEventListener('click', () => {
            updateNavState(btnSysStudy);
            executeCommand('STUDY');
        });
    }

    if (btnSysSecure) {
        btnSysSecure.addEventListener('click', () => {
            updateNavState(btnSysSecure);
            executeCommand('DISRUPTION');
        });
    }

    if (btnActions) {
        btnActions.addEventListener('click', () => {
            executeCommand('HELP');
        });
    }

    if (btnOverview) {
        btnOverview.addEventListener('click', () => {
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
    // Map System
    let mapMode = 'MARKET';
    let marketData = [];

    // Study Insights Button
    if (btnStudyInsights) {
        btnStudyInsights.addEventListener('click', async () => {
            console.log('[Study Insights] Loading study topics...');
            switchView('STUDY');
            await loadStudyTopics();
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
        const studyView = document.getElementById('studyInsightsView');

        // Hide all views
        landingView.style.display = 'none';
        chartCanvas.style.display = 'none';
        leafletMapEl.style.display = 'none';
        if (studyView) studyView.style.display = 'none';

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
            document.getElementById('chartSymbol').innerText = 'MARKET MAP';
            // Destroy Locomotive Scroll when not on landing page
            destroyLocomotiveScroll();
        } else if (mode === 'STUDY') {
            if (studyView) studyView.style.display = 'block';
            document.getElementById('chartSymbol').innerText = 'STUDY INSIGHTS';
            // Initialize Locomotive Scroll for study view
            setTimeout(() => initStudyLocomotiveScroll(), 100);
        }
    }

    function updateButtonStates(mode) {
        const buttons = {
            'LANDING': btnOverview,
            'STUDY': btnStudyInsights,
            'MAP_HD': btnMarketMap
        };

        // Reset all buttons
        [btnOverview, btnStudyInsights, btnMarketMap].forEach(btn => {
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

    function initStudyLocomotiveScroll() {
        // Destroy existing instance if any
        if (locomotiveScroll) {
            locomotiveScroll.destroy();
            locomotiveScroll = null;
        }

        // Initialize Locomotive Scroll on study view
        const studyView = document.getElementById('studyInsightsView');
        if (studyView && typeof LocomotiveScroll !== 'undefined') {
            locomotiveScroll = new LocomotiveScroll({
                el: studyView,
                smooth: true,
                multiplier: 1.2,
                lerp: 0.08,
                smartphone: {
                    smooth: true
                },
                tablet: {
                    smooth: true
                }
            });

            console.log('[Locomotive Scroll] Initialized for Study View');
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
                        <span style="color: #9ca3af; font-size: 9px;">${route.origin} â†’ ${route.dest}</span>
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
        const priceImpact = (anchored - moving) / total * 5; // Scale to Â±5%

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
                <div style="color: #9ca3af; font-size: 10px; margin-bottom: 6px; font-weight: 500;">ðŸ’° INVESTMENT IMPACT</div>
                <div style="color: ${analysis.impact >= 0 ? '#ef4444' : '#10b981'}; font-size: 28px; font-weight: 700; font-family: 'Roboto Mono', monospace; margin-bottom: 6px;">
                    ${analysis.impact >= 0 ? '+' : ''}${analysis.impact.toFixed(2)}%
                </div>
                <div style="color: #e5e7eb; font-size: 11px; line-height: 1.5;">
                    ${analysis.impactDescription}
                </div>
            </div>
            
            <!-- Route & Status -->
            <div style="background: rgba(31,41,55,0.5); border: 1px solid #374151; border-radius: 6px; padding: 12px; margin-bottom: 14px;">
                <div style="color: #3b82f6; font-size: 11px; font-weight: 600; margin-bottom: 8px;">ðŸ“ ROUTE DETAILS</div>
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
                <div style="color: #fbbf24; font-size: 11px; font-weight: 600; margin-bottom: 8px;">ðŸ“Š PROOF & EVIDENCE</div>
                ${analysis.proof.map(item => `
                    <div style="padding: 6px 0; border-bottom: 1px solid #1f2937;">
                        <div style="color: #e5e7eb; font-size: 10px; font-weight: 600; margin-bottom: 2px;">âœ“ ${item.title}</div>
                        <div style="color: #9ca3af; font-size: 9px;">${item.detail}</div>
                    </div>
                `).join('')}
            </div>
            
            <!-- Risk Assessment -->
            <div style="background: rgba(31,41,55,0.5); border: 1px solid #374151; border-radius: 6px; padding: 12px; margin-bottom: 14px;">
                <div style="color: #ef4444; font-size: 11px; font-weight: 600; margin-bottom: 8px;">âš ï¸ RISK ASSESSMENT</div>
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
                        <div style="color: #ef4444; font-size: 9px;">âš¡ ${risk}</div>
                    </div>
                `).join('')}
            </div>
            
            <!-- Actionable Recommendations -->
            <div style="background: linear-gradient(135deg, rgba(16,185,129,0.1), rgba(34,197,94,0.1)); border: 1px solid #10b981; border-radius: 6px; padding: 12px;">
                <div style="color: #10b981; font-size: 11px; font-weight: 600; margin-bottom: 8px;">ðŸ’¡ RECOMMENDATIONS</div>
                ${analysis.recommendations.map((rec, idx) => `
                    <div style="padding: 6px 0; ${idx < analysis.recommendations.length - 1 ? 'border-bottom: 1px solid #1f2937;' : ''}">
                        <div style="color: #e5e7eb; font-size: 10px; font-weight: 600; margin-bottom: 2px;">${idx + 1}. ${rec.action}</div>
                        <div style="color: #9ca3af; font-size: 9px;">${rec.reason}</div>
                        <div style="color: #10b981; font-size: 9px; margin-top: 2px;">ðŸ’° ${rec.benefit}</div>
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
        // Legacy: API removed.
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

    // ===== STUDY INSIGHTS FUNCTIONS =====

    async function loadStudyTopics() {
        try {
            const res = await fetch('/command', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ command: 'STUDY' })
            });
            const data = await res.json();
            if (data.type === 'STUDY_VIEW') {
                // Render resources as topics
                renderStudyTopics(data.resources);
                // Optionally render news if a function exists, otherwise ignore
                if (typeof renderStudyNews === 'function' && data.news) {
                    renderStudyNews(data.news);
                }
            }
        } catch (err) {
            console.error('Error loading study topics:', err);
        }
    }

    function renderStudyTopics(topics) {
        console.log('[Study] Rendering topics:', topics);
        const content = document.getElementById('studyContent');
        if (!content) {
            console.error('[Study] studyContent element not found!');
            return;
        }
        console.log('[Study] studyContent element found, rendering...');

        // Group topics by category
        const categories = {
            'ANALYSIS': { name: 'Technical Analysis', icon: 'ðŸ“ˆ', color: '#10b981', desc: 'Charts, Patterns, Indicators' },
            'FUNDAMENTALS': { name: 'Fundamentals', icon: 'ðŸ“Š', color: '#3b82f6', desc: 'Financial Statements, Ratios' },
            'DERIVATIVES': { name: 'Derivatives', icon: 'ðŸ“‰', color: '#f59e0b', desc: 'Options, Futures, Swaps' },
            'STRATEGY': { name: 'Trading Strategy', icon: 'â™Ÿï¸', color: '#8b5cf6', desc: 'Risk Mgmt, Portfolio Construction' }
        };

        content.innerHTML = `
            <div style="font-family: 'Inter', sans-serif; max-width: 1200px; margin: 0 auto;">
                <!-- Header -->
                <div style="margin-bottom: 32px; text-align: center;">
                    <h1 style="color: #10b981; font-size: 28px; font-weight: 700; margin-bottom: 8px; letter-spacing: -0.5px;">
                        ðŸ“š Finance Interview Prep
                    </h1>
                    <p style="color: #9ca3af; font-size: 14px; line-height: 1.6;">
                        Master finance interviews with real-time market data and expert-level questions
                    </p>
                </div>
                
                <!-- Category Grid -->
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; margin-bottom: 24px;">
                    ${Object.entries(categories).map(([key, cat]) => {
            const topicCount = topics.filter(t => t.category === key).length;
            return `
                        <div onclick="loadStudyCategory('${key}')" 
                             style="background: linear-gradient(135deg, rgba(17,24,39,0.95), rgba(31,41,55,0.9)); 
                                    border: 1px solid ${cat.color}30; 
                                    border-radius: 12px; 
                                    padding: 20px; 
                                    cursor: pointer; 
                                    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                                    position: relative;
                                    overflow: hidden;"
                             onmouseover="this.style.borderColor='${cat.color}'; this.style.transform='translateY(-4px)'; this.style.boxShadow='0 8px 24px rgba(0,0,0,0.4)';"
                             onmouseout="this.style.borderColor='${cat.color}30'; this.style.transform='translateY(0)'; this.style.boxShadow='none';">
                            
                            <!-- Gradient overlay -->
                            <div style="position: absolute; top: 0; right: 0; width: 100px; height: 100px; 
                                        background: radial-gradient(circle at top right, ${cat.color}15, transparent); 
                                        pointer-events: none;"></div>
                            
                            <div style="position: relative; z-index: 1;">
                                <div style="font-size: 36px; margin-bottom: 12px; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.3));">
                                    ${cat.icon}
                                </div>
                                <h3 style="color: ${cat.color}; font-size: 16px; font-weight: 600; margin-bottom: 6px; letter-spacing: -0.3px;">
                                    ${cat.name}
                                </h3>
                                <p style="color: #9ca3af; font-size: 12px; line-height: 1.5; margin-bottom: 12px;">
                                    ${cat.desc}
                                </p>
                                <div style="display: flex; align-items: center; justify-content: space-between;">
                                    <span style="color: #6b7280; font-size: 11px; font-weight: 500;">
                                        ${topicCount} topics
                                    </span>
                                    <span style="color: ${cat.color}; font-size: 18px;">â†’</span>
                                </div>
                            </div>
                        </div>
                    `}).join('')}
                </div>
                
                <!-- Quick Actions -->
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-top: 24px;">
                    <div onclick="loadMarketScenario()" 
                         style="background: linear-gradient(135deg, rgba(16,185,129,0.15), rgba(34,197,94,0.1)); 
                                border: 1px solid #10b98150; 
                                border-radius: 12px; 
                                padding: 20px; 
                                cursor: pointer;
                                transition: all 0.3s;"
                         onmouseover="this.style.borderColor='#10b981'; this.style.transform='translateY(-2px)';"
                         onmouseout="this.style.borderColor='#10b98150'; this.style.transform='translateY(0)';">
                        <div style="display: flex; align-items: center; gap: 12px;">
                            <div style="font-size: 32px;">ðŸŽ¯</div>
                            <div>
                                <div style="color: #10b981; font-size: 15px; font-weight: 600; margin-bottom: 4px;">
                                    Live Market Scenario
                                </div>
                                <div style="color: #9ca3af; font-size: 12px;">
                                    Practice with real-time VIX, SPX & BTC data
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div onclick="loadStudyResources()" 
                         style="background: linear-gradient(135deg, rgba(59,130,246,0.15), rgba(37,99,235,0.1)); 
                                border: 1px solid #3b82f650; 
                                border-radius: 12px; 
                                padding: 20px; 
                                cursor: pointer;
                                transition: all 0.3s;"
                         onmouseover="this.style.borderColor='#3b82f6'; this.style.transform='translateY(-2px)';"
                         onmouseout="this.style.borderColor='#3b82f650'; this.style.transform='translateY(0)';">
                        <div style="display: flex; align-items: center; gap: 12px;">
                            <div style="font-size: 32px;">ðŸ“–</div>
                            <div>
                                <div style="color: #3b82f6; font-size: 15px; font-weight: 600; margin-bottom: 4px;">
                                    Study Resources
                                </div>
                                <div style="color: #9ca3af; font-size: 12px;">
                                    Books, courses & certifications
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    async function loadStudyCategory(category) {
        try {
            const res = await fetch('/command', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ command: `STUDY ${category}` })
            });
            const data = await res.json();
            if (data.type === 'STUDY_QUESTIONS') {
                renderStudyQuestions(data);
            }
        } catch (err) {
            console.error('Error loading questions:', err);
        }
    }

    function renderStudyQuestions(data) {
        const content = document.getElementById('studyContent');
        if (!content) return;

        const difficultyColors = {
            'beginner': '#10b981',
            'intermediate': '#f59e0b',
            'advanced': '#ef4444'
        };

        content.innerHTML = `
            <div style="font-family: 'Inter', sans-serif;">
                <div style="display: flex; align-items: center; margin-bottom: 16px;">
                    <button onclick="loadStudyTopics()" 
                            style="background: #1f2937; color: #9ca3af; border: 1px solid #374151; 
                                   padding: 4px 12px; border-radius: 4px; cursor: pointer; margin-right: 12px;">
                        â† Back
                    </button>
                    <h2 style="color: #10b981; font-size: 16px; margin: 0;">${data.title}</h2>
                </div>
                
                <div style="display: flex; flex-direction: column; gap: 12px;">
                    ${data.questions.map((q, idx) => `
                        <div onclick="loadQuestionAnswer('${q.id}')"
                             style="background: rgba(31,41,55,0.5); border: 1px solid #374151; 
                                    border-radius: 8px; padding: 14px; cursor: pointer;
                                    transition: border-color 0.2s;"
                             onmouseover="this.style.borderColor='#10b981'"
                             onmouseout="this.style.borderColor='#374151'">
                            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px;">
                                <span style="color: #6b7280; font-size: 10px;">Question ${idx + 1}</span>
                                <span style="background: ${difficultyColors[q.difficulty]}20; color: ${difficultyColors[q.difficulty]}; 
                                             font-size: 9px; padding: 2px 8px; border-radius: 10px; font-weight: 600;">
                                    ${q.difficulty.toUpperCase()}
                                </span>
                            </div>
                            <div style="color: #e5e7eb; font-size: 12px; line-height: 1.5;">${q.question}</div>
                            ${q.uses_market_data ? `
                                <div style="color: #3b82f6; font-size: 10px; margin-top: 8px;">
                                    ðŸ“Š Uses real-time market data
                                </div>
                            ` : ''}
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    async function loadQuestionAnswer(questionId) {
        console.log('[Study] Loading answer for question:', questionId);
        try {
            const res = await fetch('/command', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ command: `ANSWER ${questionId}` })
            });
            const data = await res.json();
            console.log('[Study] Answer response:', data);
            if (data.type === 'STUDY_ANSWER') {
                renderQuestionAnswer(data.data);
            } else {
                console.error('[Study] Unexpected response type:', data.type);
            }
        } catch (err) {
            console.error('Error loading answer:', err);
        }
    }

    function renderQuestionAnswer(data) {
        const content = document.getElementById('studyContent');
        if (!content) return;

        content.innerHTML = `
            <div style="font-family: 'Inter', sans-serif;">
                <button onclick="loadStudyCategory('${data.category}')" 
                        style="background: #1f2937; color: #9ca3af; border: 1px solid #374151; 
                               padding: 4px 12px; border-radius: 4px; cursor: pointer; margin-bottom: 16px;">
                    â† Back to Questions
                </button>
                
                <div style="background: rgba(31,41,55,0.5); border: 1px solid #374151; border-radius: 8px; padding: 16px; margin-bottom: 16px;">
                    <div style="color: #9ca3af; font-size: 10px; margin-bottom: 8px;">QUESTION</div>
                    <div style="color: #e5e7eb; font-size: 14px; line-height: 1.6;">${data.question}</div>
                </div>
                
                <div style="background: linear-gradient(135deg, rgba(16,185,129,0.1), rgba(34,197,94,0.1)); 
                            border: 1px solid #10b981; border-radius: 8px; padding: 16px; margin-bottom: 16px;">
                    <div style="color: #10b981; font-size: 10px; font-weight: 600; margin-bottom: 8px;">âœ“ MODEL ANSWER</div>
                    <div style="color: #e5e7eb; font-size: 13px; line-height: 1.6;">${data.answer}</div>
                </div>
                
                <div style="background: rgba(59,130,246,0.1); border: 1px solid #3b82f6; border-radius: 8px; padding: 16px;">
                    <div style="color: #3b82f6; font-size: 10px; font-weight: 600; margin-bottom: 8px;">ðŸ’¡ DETAILED EXPLANATION</div>
                    <div style="color: #d1d5db; font-size: 12px; line-height: 1.7;">${data.explanation}</div>
                </div>
            </div>
        `;
    }

    async function loadMarketScenario() {
        try {
            const res = await fetch('/command', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ command: 'SCENARIO' })
            });
            const data = await res.json();
            if (data.type === 'MARKET_SCENARIO') {
                renderMarketScenario(data.scenario);
            }
        } catch (err) {
            console.error('Error loading scenario:', err);
        }
    }

    function renderMarketScenario(scenario) {
        const content = document.getElementById('studyContent');
        if (!content) return;

        const typeColors = {
            'high_volatility': '#ef4444',
            'low_volatility': '#f59e0b',
            'normal_market': '#10b981'
        };
        const color = typeColors[scenario.type] || '#10b981';

        content.innerHTML = `
            <div style="font-family: 'Inter', sans-serif;">
                <button onclick="loadStudyTopics()" 
                        style="background: #1f2937; color: #9ca3af; border: 1px solid #374151; 
                               padding: 4px 12px; border-radius: 4px; cursor: pointer; margin-bottom: 16px;">
                    â† Back
                </button>
                
                <div style="background: linear-gradient(135deg, ${color}10, ${color}05); 
                            border: 2px solid ${color}; border-radius: 12px; padding: 20px; margin-bottom: 16px;">
                    <div style="color: ${color}; font-size: 18px; font-weight: 700; margin-bottom: 8px;">
                        ðŸŽ¯ ${scenario.title}
                    </div>
                    <div style="color: #d1d5db; font-size: 13px; line-height: 1.6; margin-bottom: 16px;">
                        ${scenario.description}
                    </div>
                    
                    <div style="background: rgba(0,0,0,0.3); border-radius: 8px; padding: 12px; margin-bottom: 16px;">
                        <div style="color: #9ca3af; font-size: 10px; margin-bottom: 8px;">CURRENT MARKET DATA</div>
                        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px;">
                            <div style="text-align: center;">
                                <div style="color: #6b7280; font-size: 10px;">S&P 500</div>
                                <div style="color: #10b981; font-size: 16px; font-weight: 700;">${scenario.market_context.SPX.toLocaleString()}</div>
                            </div>
                            <div style="text-align: center;">
                                <div style="color: #6b7280; font-size: 10px;">VIX</div>
                                <div style="color: ${color}; font-size: 16px; font-weight: 700;">${scenario.market_context.VIX.toFixed(2)}</div>
                            </div>
                            <div style="text-align: center;">
                                <div style="color: #6b7280; font-size: 10px;">Bitcoin</div>
                                <div style="color: #f59e0b; font-size: 16px; font-weight: 700;">$${scenario.market_context.BTC.toLocaleString()}</div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div style="background: rgba(31,41,55,0.5); border: 1px solid #374151; border-radius: 8px; padding: 16px; margin-bottom: 16px;">
                    <div style="color: #f59e0b; font-size: 12px; font-weight: 600; margin-bottom: 12px;">ðŸ“ CHALLENGE</div>
                    <div style="color: #e5e7eb; font-size: 13px; line-height: 1.7;">${scenario.challenge}</div>
                </div>
                
                <div style="background: rgba(31,41,55,0.5); border: 1px solid #374151; border-radius: 8px; padding: 16px; margin-bottom: 16px;">
                    <div style="color: #3b82f6; font-size: 12px; font-weight: 600; margin-bottom: 12px;">ðŸ’¡ HINTS</div>
                    ${scenario.hints.map(hint => `
                        <div style="color: #9ca3af; font-size: 12px; padding: 6px 0; border-bottom: 1px solid #1f2937;">
                            â€¢ ${hint}
                        </div>
                    `).join('')}
                </div>
                
                <div id="solutionToggle" onclick="document.getElementById('solutionContent').style.display='block'; this.style.display='none';"
                     style="background: #10b981; color: #111; border-radius: 8px; padding: 12px; text-align: center; 
                            cursor: pointer; font-weight: 600; font-size: 13px;">
                    Reveal Solution Approach
                </div>
                <div id="solutionContent" style="display: none; background: linear-gradient(135deg, rgba(16,185,129,0.1), rgba(34,197,94,0.1)); 
                            border: 1px solid #10b981; border-radius: 8px; padding: 16px; margin-top: 12px;">
                    <div style="color: #10b981; font-size: 12px; font-weight: 600; margin-bottom: 8px;">âœ“ SOLUTION APPROACH</div>
                    <div style="color: #d1d5db; font-size: 12px; line-height: 1.7;">${scenario.solution_approach}</div>
                </div>
            </div>
        `;
    }

    async function loadStudyResources() {
        try {
            const res = await fetch('/command', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ command: 'RESOURCES' })
            });
            const data = await res.json();
            if (data.type === 'STUDY_RESOURCES') {
                renderStudyResources(data.resources);
            }
        } catch (err) {
            console.error('Error loading resources:', err);
        }
    }

    function renderStudyResources(resources) {
        const content = document.getElementById('studyContent');
        if (!content) return;

        const typeIcons = {
            'book': 'ðŸ“š',
            'course': 'ðŸŽ“',
            'certification': 'ðŸ†',
            'website': 'ðŸŒ'
        };

        content.innerHTML = `
            <div style="font-family: 'Inter', sans-serif;">
                <button onclick="loadStudyTopics()" 
                        style="background: #1f2937; color: #9ca3af; border: 1px solid #374151; 
                               padding: 4px 12px; border-radius: 4px; cursor: pointer; margin-bottom: 16px;">
                    â† Back
                </button>
                
                <h2 style="color: #10b981; font-size: 16px; margin-bottom: 16px;">ðŸ“– Study Resources</h2>
                
                <div style="display: flex; flex-direction: column; gap: 12px;">
                    ${resources.map(r => `
                        <div style="background: rgba(31,41,55,0.5); border: 1px solid #374151; 
                                    border-radius: 8px; padding: 14px;">
                            <div style="display: flex; align-items: flex-start; gap: 12px;">
                                <div style="font-size: 24px;">${typeIcons[r.type] || 'ðŸ“„'}</div>
                                <div style="flex: 1;">
                                    <div style="color: #e5e7eb; font-size: 13px; font-weight: 600; margin-bottom: 4px;">
                                        ${r.title}
                                    </div>
                                    <div style="color: #6b7280; font-size: 11px; margin-bottom: 6px;">
                                        by ${r.author} â€¢ ${r.type.charAt(0).toUpperCase() + r.type.slice(1)}
                                    </div>
                                    <div style="color: #9ca3af; font-size: 11px;">
                                        ${r.description}
                                    </div>
                                </div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    // Make study functions globally accessible
    window.loadStudyCategory = loadStudyCategory;
    window.loadStudyTopics = loadStudyTopics;
    window.loadQuestionAnswer = loadQuestionAnswer;
    window.loadMarketScenario = loadMarketScenario;
    window.loadStudyResources = loadStudyResources;

    function initLeafletMap() {
        leafletMap = L.map('leafletMap', { center: [20, 0], zoom: 2 });
        L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
            attribution: 'Â© OpenStreetMap Â© CartoDB'
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
        if (heading >= 337.5 || heading < 22.5) return 'â†‘';
        if (heading >= 22.5 && heading < 67.5) return 'â†—';
        if (heading >= 67.5 && heading < 112.5) return 'â†’';
        if (heading >= 112.5 && heading < 157.5) return 'â†˜';
        if (heading >= 157.5 && heading < 202.5) return 'â†“';
        if (heading >= 202.5 && heading < 247.5) return 'â†™';
        if (heading >= 247.5 && heading < 292.5) return 'â†';
        if (heading >= 292.5 && heading < 337.5) return 'â†–';
        return 'â—';
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
                        <div style="color:${market.is_open ? '#0f0' : '#f00'};font-size:9px;">${market.is_open ? 'â— OPEN' : 'â—‹ CLOSED'}</div>
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
    // Command Input History
    let cmdHistory = [];
    let historyIndex = -1;

    cmdInput.addEventListener('keydown', async (e) => {
        if (e.key === 'Enter') {
            const command = cmdInput.value;
            cmdInput.value = '';
            historyIndex = -1; // Reset

            if (command.trim() === '') return;

            // Add to history if unique/new
            if (cmdHistory[0] !== command) {
                cmdHistory.unshift(command);
            }
            if (cmdHistory.length > 50) cmdHistory.pop();

            await executeCommand(command);
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            if (historyIndex < cmdHistory.length - 1) {
                historyIndex++;
                cmdInput.value = cmdHistory[historyIndex];
            }
        } else if (e.key === 'ArrowDown') {
            e.preventDefault();
            if (historyIndex > 0) {
                historyIndex--;
                cmdInput.value = cmdHistory[historyIndex];
            } else {
                historyIndex = -1;
                cmdInput.value = '';
            }
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
        if (activeMode === 'OVERVIEW_GRID') renderOverviewGrid();
    }

    let gridPage = 0;
    const ITEMS_PER_PAGE = 9;

    function renderOverviewGrid() {
        if (!gridData || gridData.length === 0) return;
        const w = mainChart.width;
        const h = mainChart.height;
        ctx.clearRect(0, 0, w, h);

        // Pagination Controls
        const totalPages = Math.ceil(gridData.length / ITEMS_PER_PAGE);
        const controls = document.getElementById('gridControls');
        const pageNum = document.getElementById('gridPageNum');

        if (controls) {
            controls.style.display = 'flex';
            pageNum.innerText = `PAGE ${gridPage + 1}/${totalPages}`;
        }

        const start = gridPage * ITEMS_PER_PAGE;
        const viewData = gridData.slice(start, start + ITEMS_PER_PAGE);

        const rows = 3;
        const cols = 3;
        const cellW = w / cols;
        const cellH = h / rows;

        ctx.font = 'bold 12px Inconsolata';
        ctx.lineWidth = 1.5;

        viewData.forEach((item, index) => {
            const r = Math.floor(index / cols);
            const c = index % cols;

            const x = c * cellW;
            const y = r * cellH;
            const pad = 15;
            const chartW = cellW - 2 * pad;
            const chartH = cellH * 0.5; // Chart takes 50% height
            const chartX = x + pad;
            const chartY = y + cellH * 0.4; // Start chart 40% down

            // Draw Box Border
            ctx.strokeStyle = '#222';
            ctx.strokeRect(x, y, cellW, cellH);

            // Header Background
            ctx.fillStyle = 'rgba(255, 255, 255, 0.03)';
            ctx.fillRect(x, y, cellW, 30);

            // Title
            ctx.fillStyle = '#fff';
            ctx.textAlign = 'left';
            ctx.fillText(item.symbol, x + pad, y + 20);

            // Price
            const color = item.change >= 0 ? '#10b981' : '#ef4444';
            ctx.fillStyle = color;
            ctx.textAlign = 'right';
            ctx.fillText(`${item.price.toFixed(2)}`, x + cellW - pad, y + 20);

            // Change
            ctx.font = '10px Inconsolata';
            ctx.fillText(`${item.change > 0 ? '+' : ''}${item.change}%`, x + cellW - pad, y + cellH - 10);
            ctx.font = 'bold 12px Inconsolata';

            // Chart
            const prices = (item.history && item.history.map(p => p.p)) || [];
            if (prices.length > 1) {
                const min = Math.min(...prices);
                const max = Math.max(...prices);
                const range = max - min || 1;

                ctx.beginPath();
                ctx.strokeStyle = color;
                prices.forEach((p, i) => {
                    const cx = chartX + (i / (prices.length - 1)) * chartW;
                    const cy = (chartY + chartH) - ((p - min) / range * chartH);
                    if (i === 0) ctx.moveTo(cx, cy); else ctx.lineTo(cx, cy);
                });
                ctx.stroke();

                // Gradient fill
                const grad = ctx.createLinearGradient(0, chartY, 0, chartY + chartH);
                grad.addColorStop(0, color === '#10b981' ? 'rgba(16, 185, 129, 0.2)' : 'rgba(239, 68, 68, 0.2)');
                grad.addColorStop(1, 'rgba(0, 0, 0, 0)');
                ctx.lineTo(chartX + chartW, chartY + chartH);
                ctx.lineTo(chartX, chartY + chartH);
                ctx.closePath();
                ctx.fillStyle = grad;
                ctx.fill();
            }
        });
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

            // Hardware Diagnostics
            try {
                const diagRes = await fetch('/system/diagnostics');
                const diag = await diagRes.json();
                const cpuEl = document.getElementById('cpu-stat');
                cpuEl.innerText = `CPU: ${diag.cpu_percent}% [${diag.acceleration_mode}]`;

                // Color code load
                if (diag.cpu_percent > 80) cpuEl.style.color = '#ef4444';
                else if (diag.cpu_percent > 50) cpuEl.style.color = '#f59e0b';
                else cpuEl.style.color = '#10b981';
            } catch (dErr) { console.warn(dErr); }

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

    // Auth State
    let sessionToken = null;

    // Navigation History
    let navHistory = [];
    let currentNavCmd = "OVERVIEW";
    const btnBack = document.getElementById('btnBack');

    if (btnBack) {
        btnBack.addEventListener('click', goBack);
    }

    if (document.getElementById('btnGridNext')) {
        document.getElementById('btnGridNext').addEventListener('click', () => {
            const totalPages = Math.ceil((gridData?.length || 0) / ITEMS_PER_PAGE);
            if (gridPage < totalPages - 1) {
                gridPage++;
                renderOverviewGrid();
            }
        });
    }

    if (document.getElementById('btnGridPrev')) {
        document.getElementById('btnGridPrev').addEventListener('click', () => {
            if (gridPage > 0) {
                gridPage--;
                renderOverviewGrid();
            }
        });
    }

    function isNavCommand(cmd) {
        if (!cmd) return false;
        const c = cmd.toUpperCase();
        // Commands that represent a "Page"
        const prefixes = ['OVERVIEW', 'TANKER', 'MAP', 'CHART', 'QUOTE', 'SCAN', 'RISK', 'ADVISE', 'NEWS', 'TODAY', 'MEMORY', 'DISRUPTION', 'AUTH', 'SQL', 'NIFTY'];
        return prefixes.some(p => c.startsWith(p));
    }

    function goBack() {
        if (navHistory.length === 0) return;
        const prev = navHistory.pop();
        currentNavCmd = prev;
        executeCommand(prev, true);

        if (navHistory.length === 0 && btnBack) btnBack.style.display = 'none';

        // Sync Nav Bar
        if (window.updateNavState) {
            if (prev.startsWith('OVERVIEW') || prev === 'NIFTY') window.updateNavState(document.getElementById('btnSysMarket'));
            else if (prev.includes('TANKER')) window.updateNavState(document.getElementById('btnSysLogistics'));
            else if (prev.includes('SCAN') || prev.includes('AUTH') || prev.includes('SQL') || prev === 'DISRUPTION') window.updateNavState(document.getElementById('btnSysSecure'));
            else window.updateNavState(null);
        }
    }

    async function executeCommand(cmd, isBack = false) {
        if (!cmd) return;

        if (cmd === 'DEBUG') {
            alert(`Grid Data Items: ${gridData ? gridData.length : 'NULL'}`);
            if (gridData && gridData.length > 0) {
                alert(`Sample: ${JSON.stringify(gridData[0])}`);
                // Draw Red Box
                const w = mainChart.width;
                const h = mainChart.height;
                ctx.fillStyle = 'red';
                ctx.fillRect(w / 2 - 50, h / 2 - 50, 100, 100);
                ctx.fillStyle = 'white';
                ctx.fillText("CANVAS ALIVE", w / 2 - 40, h / 2);
            } else {
                alert("NO DATA to render.");
            }
            return;
        }

        // Handle History
        if (!isBack && isNavCommand(cmd)) {
            // Only push if different from current
            if (cmd.toUpperCase() !== currentNavCmd.toUpperCase()) {
                navHistory.push(currentNavCmd);
                currentNavCmd = cmd;
                if (btnBack) btnBack.style.display = 'block';

                // Reset Grid Page on new view
                if (!isBack && cmd === 'NIFTY') gridPage = 0;

                // Sync Nav Bar (Forward) is handled by button clicks usually, but direct commands need sync
                if (window.updateNavState) {
                    if (cmd.startsWith('OVERVIEW') || cmd === 'NIFTY') window.updateNavState(document.getElementById('btnSysMarket'));
                    else if (cmd.includes('TANKER')) window.updateNavState(document.getElementById('btnSysLogistics'));
                    else if (cmd.includes('SCAN') || cmd.includes('AUTH') || cmd === 'DISRUPTION') window.updateNavState(document.getElementById('btnSysSecure'));
                    else window.updateNavState(null);
                }
            }
        }

        detailView.innerHTML = "PROCESSING...";
        try {
            const res = await fetch('/command', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'x-auth-token': sessionToken || ''
                },
                body: JSON.stringify({ command: cmd })
            });
            const data = await res.json();
            handleResponse(data);
        } catch (err) {
            console.error(err);
        }
    }

    function handleResponse(data) {
        if (data.type === 'AUTH_SUCCESS') {
            sessionToken = data.token;
            detailView.innerHTML = `
            <div style="border: 2px solid #10b981; padding: 10px; color: #10b981; font-family:'Roboto Mono'">
                <div style="font-weight:bold">${data.title}</div>
                <div>${data.content}</div>
                <div style="font-size:10px; margin-top:5px; opacity:0.8">TOKEN: ${data.token.substring(0, 8)}...</div>
            </div>`;
            return;
        }

        if (data.type === 'ERROR') {
            const color = '#ef4444';
            detailView.innerHTML = `
            <div style="border-left: 2px solid ${color}; padding-left: 10px; color: #e0e0e0;">
                <div style="color:${color}; font-weight:bold">ERROR</div>
                <div>${data.content}</div>
            </div>`;
            return;
        }

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
                // ... (existing market map logic)
                marketData = data.markets || [];
                // ...
            } else {
                // ... (existing tanker map logic)
                activeMode = 'MAP_CANVAS';
                mapAssets = data.assets || [];
                mapTitle = data.title;
                if (data.metrics) mapTitle += ` [${data.metrics}]`;
                document.getElementById('chartSymbol').innerText = "ASSET MAP";
                renderMainView();
                // ...
            }
        }
        else if (data.type === 'OVERVIEW_GRID') {
            console.log("OVERVIEW_GRID Recv:", data.grids);
            gridData = data.grids || [];
            switchView('OVERVIEW_GRID');  // Show canvas before rendering
            activeMode = 'OVERVIEW_GRID';
            document.getElementById('chartSymbol').innerText = "MARKET DASHBOARD";
            renderMainView();
            detailView.innerHTML = `
                <div style="font-size: 14px; font-weight:bold; margin-bottom:10px">${data.title}</div>
                VIEW: MULTI-ASSET OVERVIEW<br>
                TRACKING: ${gridData.length} KEY INDICATORS<br>
                CPU OPTIMIZATION: ACTIVE`;
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
        else if (data.type === 'HELP_MENU') {
            let html = `<div style="font-size: 14px; font-weight:bold; margin-bottom:10px">${data.title}</div>`;
            data.sections.forEach(sec => {
                html += `<div style="margin-bottom:8px; color: #fff; border-bottom: 1px solid #333; padding-bottom: 4px;">${sec.category}</div>`;
                sec.cmds.forEach(cmd => {
                    const parts = cmd.split(' ');
                    const main = parts[0];
                    const desc = parts.slice(1).join(' ');
                    html += `
                    <div class="cmd-item" onclick="cmdInput.value='${main} '; cmdInput.focus();" style="cursor:pointer; margin-bottom:4px; font-family:'Roboto Mono'; font-size:11px;">
                        <span style="color:#00e5ff; font-weight:bold;">${main}</span> <span style="color:#888;">${desc}</span>
                    </div>`;
                });
                html += `<div style="height:8px"></div>`;
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
        }
        // Study Insights response handlers
        else if (data.type === 'STUDY_TOPICS') {
            switchView('STUDY');
            renderStudyTopics(data.topics);
        }
        else if (data.type === 'STUDY_QUESTIONS') {
            switchView('STUDY');
            renderStudyQuestions(data);
        }
        else if (data.type === 'STUDY_ANSWER') {
            switchView('STUDY');
            renderQuestionAnswer(data.data);
        }
        else if (data.type === 'MARKET_SCENARIO') {
            switchView('STUDY');
            renderMarketScenario(data.scenario);
        }
        else if (data.type === 'STUDY_RESOURCES') {
            switchView('STUDY');
            renderStudyResources(data.resources);
        }
        else {
            detailView.innerText = JSON.stringify(data, null, 2);
        }

        // === STUDY VIEWS ===
        if (data.type === 'STUDY_VIEW') {
            let html = `
                <div style="font-size: 16px; font-weight: 700; margin-bottom: 15px; color: #10b981;">${data.title}</div>
                <div style="font-size: 10px; color: #6b7280; margin-bottom: 15px;">Last updated: ${data.last_updated}</div>
                
                <div style="margin-bottom: 20px;">
                    <div style="color: #3b82f6; font-weight: 600; margin-bottom: 10px; border-bottom: 1px solid #374151; padding-bottom: 5px;">ðŸ“° LIVE NEWS</div>
            `;

            if (data.news && data.news.length > 0) {
                data.news.forEach(item => {
                    const sentimentColor = item.sentiment === 'BULLISH' ? '#10b981' :
                        item.sentiment === 'BEARISH' ? '#ef4444' : '#6b7280';
                    const impactColor = item.impact === 'HIGH' ? '#ef4444' :
                        item.impact === 'MEDIUM' ? '#f59e0b' : '#6b7280';
                    html += `
                        <div style="background: #111827; border: 1px solid #1f2937; border-radius: 6px; padding: 10px; margin-bottom: 8px;">
                            <div style="display: flex; justify-content: space-between; align-items: start;">
                                <span style="color: ${sentimentColor}; font-size: 10px; font-weight: 600;">
                                    ${item.sentiment === 'BULLISH' ? 'ðŸŸ¢' : item.sentiment === 'BEARISH' ? 'ðŸ”´' : 'âšª'} ${item.sentiment}
                                </span>
                                <span style="color: #6b7280; font-size: 9px;">${item.source}</span>
                            </div>
                            <div style="color: #e5e7eb; font-size: 11px; margin: 6px 0; line-height: 1.4;">${item.title}</div>
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 8px;">
                                <span style="color: ${impactColor}; font-size: 9px;">Impact: ${item.impact}</span>
                                ${item.tickers.length > 0 ? `
                                    <div style="display: flex; gap: 4px;">
                                        ${item.tickers.map(t => `<span onclick="executeCommand('ADVISE ${t}')" style="background: #1f2937; color: #3b82f6; padding: 2px 6px; border-radius: 3px; font-size: 9px; cursor: pointer;">${t}</span>`).join('')}
                                    </div>
                                ` : ''}
                            </div>
                        </div>
                    `;
                });
            } else {
                html += '<div style="color: #6b7280; font-size: 11px;">Loading news feeds...</div>';
            }

            html += `
                </div>
                <div style="margin-bottom: 20px;">
                    <div style="color: #8b5cf6; font-weight: 600; margin-bottom: 10px; border-bottom: 1px solid #374151; padding-bottom: 5px;">ðŸ“– LEARNING RESOURCES</div>
            `;

            if (data.resources) {
                data.resources.slice(0, 4).forEach(r => {
                    const diffColor = r.difficulty === 'BEGINNER' ? '#10b981' :
                        r.difficulty === 'INTERMEDIATE' ? '#f59e0b' : '#ef4444';
                    html += `
                        <div style="padding: 8px 0; border-bottom: 1px solid #1f2937;">
                            <div style="color: #e5e7eb; font-size: 11px; font-weight: 500;">${r.title}</div>
                            <div style="display: flex; justify-content: space-between; margin-top: 4px;">
                                <span style="color: #6b7280; font-size: 9px;">${r.category}</span>
                                <span style="color: ${diffColor}; font-size: 9px;">${r.difficulty}</span>
                            </div>
                        </div>
                    `;
                });
            }

            html += `
                </div>
                <div style="background: #111827; border: 1px solid #374151; border-radius: 6px; padding: 10px; text-align: center;">
                    <span style="color: #6b7280; font-size: 10px;">ðŸ“‹ ${data.glossary_count} terms in glossary</span>
                    <span onclick="executeCommand('GLOSSARY')" style="color: #3b82f6; font-size: 10px; margin-left: 10px; cursor: pointer;">View All â†’</span>
                </div>
            `;

            detailView.innerHTML = html;
        }

        if (data.type === 'LEARN_VIEW') {
            let html = `<div style="font-size: 14px; font-weight: 700; margin-bottom: 15px; color: #8b5cf6;">${data.title}</div>`;

            if (data.resources && data.resources.length > 0) {
                data.resources.forEach(r => {
                    const diffColor = r.difficulty === 'BEGINNER' ? '#10b981' :
                        r.difficulty === 'INTERMEDIATE' ? '#f59e0b' : '#ef4444';
                    html += `
                        <div style="background: #111827; border: 1px solid #1f2937; border-radius: 6px; padding: 12px; margin-bottom: 10px;">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <span style="color: #e5e7eb; font-size: 12px; font-weight: 600;">${r.title}</span>
                                <span style="background: ${diffColor}20; color: ${diffColor}; padding: 2px 8px; border-radius: 10px; font-size: 9px;">${r.difficulty}</span>
                            </div>
                            <div style="color: #9ca3af; font-size: 10px; margin-top: 6px;">${r.description}</div>
                            <div style="color: #6b7280; font-size: 9px; margin-top: 6px;">Category: ${r.category}</div>
                        </div>
                    `;
                });
            } else {
                html += '<div style="color: #6b7280;">No resources found for this topic.</div>';
            }

            detailView.innerHTML = html;
        }

        if (data.type === 'GLOSSARY_VIEW') {
            let html = `<div style="font-size: 14px; font-weight: 700; margin-bottom: 15px; color: #f59e0b;">${data.title}</div>`;

            if (data.terms && !data.terms.error) {
                Object.entries(data.terms).forEach(([term, definition]) => {
                    html += `
                        <div style="padding: 10px 0; border-bottom: 1px solid #1f2937;">
                            <div style="color: #10b981; font-size: 12px; font-weight: 600;">${term}</div>
                            <div style="color: #9ca3af; font-size: 11px; margin-top: 4px; line-height: 1.4;">${definition}</div>
                        </div>
                    `;
                });
            } else if (data.terms && data.terms.error) {
                html += `<div style="color: #ef4444;">${data.terms.error}</div>`;
            }

            detailView.innerHTML = html;
        }

        // === BLOOMBERG-STYLE VIEWS ===
        if (data.type === 'FX_VIEW') {
            let html = `
                <div style="font-size: 16px; font-weight: 700; margin-bottom: 10px; color: #f59e0b;">${data.title}</div>
                <div style="font-size: 10px; color: #6b7280; margin-bottom: 15px;">Updated: ${data.updated}</div>
            `;

            if (data.rates && data.rates.length > 0) {
                data.rates.forEach(r => {
                    const color = r.direction === 'up' ? '#10b981' : '#ef4444';
                    const arrow = r.direction === 'up' ? 'â–²' : 'â–¼';
                    html += `
                        <div style="display: flex; justify-content: space-between; align-items: center; padding: 10px; background: #111827; border: 1px solid #1f2937; border-radius: 6px; margin-bottom: 6px;">
                            <span style="color: #e5e7eb; font-weight: 600; font-size: 12px;">${r.pair}</span>
                            <div style="text-align: right;">
                                <span style="color: #fff; font-size: 14px; font-weight: 700; font-family: 'Roboto Mono', monospace;">${r.rate}</span>
                                <span style="color: ${color}; font-size: 10px; margin-left: 8px;">${arrow} ${r.change_pct}%</span>
                            </div>
                        </div>
                    `;
                });
            } else {
                html += '<div style="color: #6b7280;">Loading FX rates...</div>';
            }
            detailView.innerHTML = html;
        }

        if (data.type === 'SCREENER_VIEW') {
            let html = `
                <div style="font-size: 16px; font-weight: 700; margin-bottom: 15px; color: #3b82f6;">${data.title}</div>
            `;

            if (data.results && data.results.length > 0) {
                html += `<div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 4px; font-size: 9px; color: #6b7280; padding: 4px 8px; border-bottom: 1px solid #1f2937;"><span>SYMBOL</span><span style="text-align:right">PRICE</span><span style="text-align:right">CHG%</span></div>`;
                data.results.forEach(s => {
                    const color = s.change_pct >= 0 ? '#10b981' : '#ef4444';
                    html += `
                        <div onclick="executeCommand('ADVISE ${s.symbol}')" style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 4px; padding: 8px; background: #111827; border: 1px solid #1f2937; border-radius: 4px; margin-bottom: 4px; cursor: pointer;">
                            <span style="color: #e5e7eb; font-weight: 600; font-size: 11px;">${s.symbol}</span>
                            <span style="color: #fff; text-align: right; font-family: 'Roboto Mono'; font-size: 11px;">â‚¹${s.price}</span>
                            <span style="color: ${color}; text-align: right; font-size: 11px; font-weight: 600;">${s.change_pct >= 0 ? '+' : ''}${s.change_pct}%</span>
                        </div>
                    `;
                });
            }
            detailView.innerHTML = html;
        }

        if (data.type === 'MOVERS_VIEW') {
            let html = `
                <div style="font-size: 16px; font-weight: 700; margin-bottom: 10px; color: #10b981;">${data.title}</div>
            `;

            // Market summary
            if (data.summary) {
                const s = data.summary;
                html += `
                    <div style="background: #111827; border: 1px solid #1f2937; border-radius: 6px; padding: 10px; margin-bottom: 15px; display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; text-align: center;">
                        <div><div style="color: #10b981; font-size: 16px; font-weight: 700;">${s.gainers}</div><div style="color: #6b7280; font-size: 9px;">GAINERS</div></div>
                        <div><div style="color: #ef4444; font-size: 16px; font-weight: 700;">${s.losers}</div><div style="color: #6b7280; font-size: 9px;">LOSERS</div></div>
                        <div><div style="color: ${s.market_sentiment === 'BULLISH' ? '#10b981' : '#ef4444'}; font-size: 12px; font-weight: 700;">${s.market_sentiment}</div><div style="color: #6b7280; font-size: 9px;">SENTIMENT</div></div>
                    </div>
                `;
            }

            // Gainers
            html += '<div style="color: #10b981; font-weight: 600; margin-bottom: 8px; font-size: 11px;">ðŸŸ¢ TOP GAINERS</div>';
            if (data.gainers) {
                data.gainers.forEach(s => {
                    html += `
                        <div onclick="executeCommand('CHART ${s.symbol}')" style="display: flex; justify-content: space-between; padding: 6px 8px; background: rgba(16,185,129,0.1); border-left: 2px solid #10b981; margin-bottom: 4px; cursor: pointer;">
                            <span style="color: #e5e7eb; font-weight: 600; font-size: 11px;">${s.symbol}</span>
                            <span style="color: #10b981; font-size: 11px; font-weight: 600;">+${s.change_pct}%</span>
                        </div>
                    `;
                });
            }

            // Losers
            html += '<div style="color: #ef4444; font-weight: 600; margin: 12px 0 8px; font-size: 11px;">ðŸ”´ TOP LOSERS</div>';
            if (data.losers) {
                data.losers.forEach(s => {
                    html += `
                        <div onclick="executeCommand('CHART ${s.symbol}')" style="display: flex; justify-content: space-between; padding: 6px 8px; background: rgba(239,68,68,0.1); border-left: 2px solid #ef4444; margin-bottom: 4px; cursor: pointer;">
                            <span style="color: #e5e7eb; font-weight: 600; font-size: 11px;">${s.symbol}</span>
                            <span style="color: #ef4444; font-size: 11px; font-weight: 600;">${s.change_pct}%</span>
                        </div>
                    `;
                });
            }
            detailView.innerHTML = html;
        }

        if (data.type === 'SECTORS_VIEW') {
            let html = `
                <div style="font-size: 16px; font-weight: 700; margin-bottom: 10px; color: #8b5cf6;">${data.title}</div>
                <div style="font-size: 10px; color: #6b7280; margin-bottom: 15px;">US Sector ETFs | ${data.updated}</div>
            `;

            if (data.sectors && data.sectors.length > 0) {
                html += '<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">';
                data.sectors.forEach(s => {
                    const color = s.direction === 'up' ? '#10b981' : '#ef4444';
                    const bgColor = s.direction === 'up' ? 'rgba(16,185,129,0.15)' : 'rgba(239,68,68,0.15)';
                    html += `
                        <div style="background: ${bgColor}; border: 1px solid ${color}40; border-radius: 6px; padding: 10px;">
                            <div style="color: #e5e7eb; font-weight: 600; font-size: 11px;">${s.sector}</div>
                            <div style="color: ${color}; font-size: 16px; font-weight: 700; margin-top: 4px;">${s.change_pct >= 0 ? '+' : ''}${s.change_pct}%</div>
                            <div style="color: #6b7280; font-size: 9px; margin-top: 2px;">${s.symbol} â€¢ $${s.price}</div>
                        </div>
                    `;
                });
                html += '</div>';
            }
            detailView.innerHTML = html;
        }

        if (data.type === 'CALENDAR_VIEW') {
            let html = `
                <div style="font-size: 16px; font-weight: 700; margin-bottom: 15px; color: #f59e0b;">${data.title}</div>
            `;

            if (data.events && data.events.length > 0) {
                data.events.forEach(e => {
                    const impactColor = e.impact === 'HIGH' ? '#ef4444' : e.impact === 'MEDIUM' ? '#f59e0b' : '#6b7280';
                    const isToday = e.days_until === 0;
                    html += `
                        <div style="background: ${isToday ? 'rgba(245,158,11,0.15)' : '#111827'}; border: 1px solid ${isToday ? '#f59e0b' : '#1f2937'}; border-radius: 6px; padding: 12px; margin-bottom: 8px;">
                            <div style="display: flex; justify-content: space-between; align-items: start;">
                                <span style="color: #e5e7eb; font-weight: 600; font-size: 11px;">${e.event}</span>
                                <span style="background: ${impactColor}20; color: ${impactColor}; padding: 2px 6px; border-radius: 3px; font-size: 9px; font-weight: 600;">${e.impact}</span>
                            </div>
                            <div style="display: flex; justify-content: space-between; margin-top: 8px;">
                                <span style="color: #6b7280; font-size: 10px;">ðŸ“… ${e.formatted_date} (${e.day_name}) â€¢ ${e.time}</span>
                                <span style="color: #3b82f6; font-size: 10px;">${e.currency}</span>
                            </div>
                            ${isToday ? '<div style="color: #f59e0b; font-size: 9px; margin-top: 6px; font-weight: 600;">âš¡ TODAY</div>' : ''}
                        </div>
                    `;
                });
            } else {
                html += '<div style="color: #6b7280;">No upcoming events.</div>';
            }
            detailView.innerHTML = html;
        }
    }

    function drawChart() {
        if (!chartData || chartData.length === 0) return;

        const w = mainChart.width;
        const h = mainChart.height;
        ctx.clearRect(0, 0, w, h);

        const prices = chartData.map(d => d.p);
        let min = Math.min(...prices);
        let max = Math.max(...prices);

        // Handle single point or flat line case
        if (min === max) {
            min -= 1;
            max += 1;
        }

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
            const xStep = chartData.length > 1 ? (w / (chartData.length - 1)) : 0;
            ctx.beginPath();

            chartBands.upper.forEach((v, i) => {
                const x = i * xStep;
                const y = h - ((v - min) / range) * h;
                if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
            });
            // Reverse down lower band
            for (let i = chartBands.lower.length - 1; i >= 0; i--) {
                const v = chartBands.lower[i];
                const x = i * xStep;
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
        const xStep = chartData.length > 1 ? (w / (chartData.length - 1)) : 0;

        chartData.forEach((d, i) => {
            const x = i * xStep;
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
                `${tanker.origin_port || 'ORIGIN'} â†’ ${tanker.dest || 'DEST'}`,
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
        ctx.fillText('â— MOVING', 10, h - 30);
        ctx.fillStyle = '#ffaa00';
        ctx.fillText('â— ANCHORED', 10, h - 15);
    }

    function drawSparkline(ctx, data, color) {
        const w = ctx.canvas.width;
        const h = ctx.canvas.height;
        ctx.clearRect(0, 0, w, h);

        if (!data || data.length < 2) return;

        const min = Math.min(...data);
        const max = Math.max(...data);
        const range = max - min || 1;

        ctx.beginPath();
        ctx.strokeStyle = color;
        ctx.lineWidth = 1.5;

        data.forEach((p, i) => {
            const x = (i / (data.length - 1)) * w;
            // Invert Y (canvas origin is top-left)
            const y = h - ((p - min) / range) * (h * 0.8) - (h * 0.1);

            if (i === 0) ctx.moveTo(x, y);
            else ctx.lineTo(x, y);
        });

        ctx.stroke();
    }

    window.executeCommand = executeCommand;

 
 f u n c t i o n   r e n d e r S t u d y N e w s ( n e w s I t e m s )   { 
 
         i f   ( ! n e w s I t e m s   | |   n e w s I t e m s . l e n g t h   = = =   0 )   r e t u r n ; 
 
 
 
         c o n s t   c o n t a i n e r   =   d o c u m e n t . g e t E l e m e n t B y I d ( ' s t u d y N e w s C o n t a i n e r ' ) ; 
 
         i f   ( ! c o n t a i n e r )   { 
 
                 c o n s t   s t u d y C o n t e n t   =   d o c u m e n t . g e t E l e m e n t B y I d ( ' s t u d y C o n t e n t ' ) ; 
 
                 i f   ( s t u d y C o n t e n t )   { 
 
                         c o n s t   n e w s D i v   =   d o c u m e n t . c r e a t e E l e m e n t ( ' d i v ' ) ; 
 
                         n e w s D i v . i d   =   ' s t u d y N e w s C o n t a i n e r ' ; 
 
                         n e w s D i v . s t y l e . m a r g i n T o p   =   ' 3 0 p x ' ; 
 
                         n e w s D i v . s t y l e . p a d d i n g   =   ' 2 0 p x ' ; 
 
                         n e w s D i v . s t y l e . b o r d e r T o p   =   ' 1 p x   s o l i d   # 3 3 3 ' ; 
 
                         s t u d y C o n t e n t . a p p e n d C h i l d ( n e w s D i v ) ; 
 
                         r e n d e r S t u d y N e w s ( n e w s I t e m s ) ; 
 
                 } 
 
                 r e t u r n ; 
 
         } 
 
 
 
         c o n s t   n e w s H T M L   =   n e w s I t e m s . m a p ( i t e m   = >   ` 
 
                         < d i v   s t y l e = " p a d d i n g :   1 0 p x ;   b o r d e r - b o t t o m :   1 p x   s o l i d   # 2 2 2 ;   m a r g i n - b o t t o m :   5 p x ; " > 
 
                                 < d i v   s t y l e = " c o l o r :   # 1 0 b 9 8 1 ;   f o n t - s i z e :   1 0 p x ;   f o n t - w e i g h t : 7 0 0 ; " > $ { i t e m . s o u r c e }   â ¬ ¢   $ { i t e m . p u b l i s h e d } < / d i v > 
 
                                 < d i v   s t y l e = " c o l o r :   # e e e ;   f o n t - s i z e :   1 4 p x ;   m a r g i n :   4 p x   0 ; " > 
 
                                         < a   h r e f = " $ { i t e m . l i n k } "   t a r g e t = " _ b l a n k "   s t y l e = " c o l o r :   # e e e ;   t e x t - d e c o r a t i o n :   n o n e ; " > $ { i t e m . t i t l e } < / a > 
 
                                 < / d i v > 
 
                                 < d i v   s t y l e = " d i s p l a y :   f l e x ;   g a p :   5 p x ;   m a r g i n - t o p :   5 p x ; " > 
 
                                         < s p a n   s t y l e = " b a c k g r o u n d :   # 1 f 2 9 3 7 ;   c o l o r :   # 9 c a 3 a f ;   p a d d i n g :   2 p x   6 p x ;   b o r d e r - r a d i u s :   4 p x ;   f o n t - s i z e :   9 p x ; " > $ { i t e m . s e n t i m e n t } < / s p a n > 
 
                                         < s p a n   s t y l e = " b a c k g r o u n d :   # 1 f 2 9 3 7 ;   c o l o r :   # 9 c a 3 a f ;   p a d d i n g :   2 p x   6 p x ;   b o r d e r - r a d i u s :   4 p x ;   f o n t - s i z e :   9 p x ; " > I M P A C T :   $ { i t e m . i m p a c t } < / s p a n > 
 
                                 < / d i v > 
 
                         < / d i v > 
 
                 ` ) . j o i n ( ' ' ) ; 
 
 
 
         c o n t a i n e r . i n n e r H T M L   =   ` 
 
                         < d i v   s t y l e = " c o l o r :   # f f f ;   f o n t - s i z e :   1 6 p x ;   f o n t - w e i g h t :   7 0 0 ;   m a r g i n - b o t t o m :   1 5 p x ; " > L i v e   M a r k e t   I n t e l l i g e n c e < / d i v > 
 
                         $ { n e w s H T M L } 
 
                 ` ; 
 
 } 
 
 } ) ; 
 
 
