document.addEventListener('DOMContentLoaded', () => {
    const cmdInput = document.getElementById('cmdInput');
    const marketList = document.getElementById('marketList');
    const eventLog = document.getElementById('eventLog');
    const detailView = document.getElementById('detailView');
    const mainChart = document.getElementById('mainChart');
    const ctx = mainChart.getContext('2d');
    const leafletMapDiv = document.getElementById('leafletMap');
    const toggleMapBtn = document.getElementById('toggleMapMode');

    // State
    let activeMode = 'CHART'; // 'CHART', 'MAP_CANVAS', 'MAP_HD'
    let activeSymbol = 'SPX';
    let chartData = [];
    let chartBands = null;
    let mapAssets = [];
    let mapTitle = "GLOBAL ASSET MAP";

    // Leaflet Map Instance
    let leafletMap = null;
    let vesselMarkers = [];
    let regionMarkers = [];

    // Auto-focus
    cmdInput.focus();
    document.addEventListener('click', () => cmdInput.focus());

    // Init
    resizeChart();
    window.addEventListener('resize', resizeChart);

    // Polling (reduced frequency to prevent 500 errors)
    setInterval(updateMarketData, 10000);  // 10s instead of 2s
    setInterval(updateSystemState, 15000); // 15s instead of 5s
    updateMarketData();
    updateSystemState();

    // Command Input
    cmdInput.addEventListener('keydown', async (e) => {
        if (e.key === 'Enter') {
            const command = cmdInput.value;
            cmdInput.value = '';
            if (command.trim() === '') return;
            await executeCommand(command);
        }
    });

    // Toggle Map Mode
    toggleMapBtn.addEventListener('click', () => {
        if (activeMode === 'MAP_CANVAS' || activeMode === 'MAP_HD') {
            if (activeMode === 'MAP_CANVAS') {
                switchToHDMap();
            } else {
                switchToCanvasMap();
            }
        }
    });

    function switchToHDMap() {
        activeMode = 'MAP_HD';
        mainChart.style.display = 'none';
        leafletMapDiv.style.display = 'block';
        toggleMapBtn.innerText = 'SWITCH TO CANVAS';

        if (!leafletMap) {
            initLeafletMap();
        }
        renderHDMap();
    }

    function switchToCanvasMap() {
        activeMode = 'MAP_CANVAS';
        mainChart.style.display = 'block';
        leafletMapDiv.style.display = 'none';
        toggleMapBtn.innerText = 'SWITCH TO HD MAP';
        renderMainView();
    }

    function initLeafletMap() {
        // Initialize Leaflet with dark tiles
        leafletMap = L.map('leafletMap', {
            center: [20, 0],
            zoom: 2,
            minZoom: 2,
            maxZoom: 10,
            zoomControl: true
        });

        // Dark theme tiles (CartoDB Dark Matter)
        L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
            attribution: '© OpenStreetMap © CartoDB',
            subdomains: 'abcd',
            maxZoom: 19
        }).addTo(leafletMap);

        console.log('[HD Map] Leaflet initialized');
    }

    function renderHDMap() {
        if (!leafletMap) return;

        // Clear existing markers
        vesselMarkers.forEach(m => leafletMap.removeLayer(m));
        regionMarkers.forEach(m => leafletMap.removeLayer(m));
        vesselMarkers = [];
        regionMarkers = [];

        // Add Regional Market Sentiment Overlays
        addRegionalOverlays();

        // Add Vessel Markers
        mapAssets.forEach(tanker => {
            const icon = L.divIcon({
                className: 'vessel-marker',
                html: `<div style="
                    width: 12px; 
                    height: 12px; 
                    background: ${tanker.status === 'MOVING' ? '#00ff00' : '#ffaa00'}; 
                    border: 2px solid ${tanker.status === 'MOVING' ? '#00ff00' : '#ffaa00'};
                    border-radius: 50%;
                    box-shadow: 0 0 10px ${tanker.status === 'MOVING' ? '#00ff00' : '#ffaa00'};
                "></div>`,
                iconSize: [12, 12],
                iconAnchor: [6, 6]
            });

            const marker = L.marker([tanker.lat, tanker.lon], { icon: icon }).addTo(leafletMap);

            // Rich Popup
            const popupContent = `
                <div class="vessel-popup">
                    <b>${tanker.origin_flag || ''} ${tanker.name}</b><br>
                    <span style="color: #ffaa00;">CARGO:</span> ${tanker.cargo_grade || 'OIL'} (${tanker.cargo_level || 0}%)<br>
                    <span style="color: #00aaff;">ROUTE:</span> ${tanker.origin_port || 'ORIGIN'} → ${tanker.dest || 'DEST'}<br>
                    <span style="color: #ff00ff;">TYPE:</span> ${tanker.vessel_type || 'VLCC'}<br>
                    <span style="color: #00ff00;">SPEED:</span> ${tanker.speed_knots || 0} knots<br>
                    <span style="color: #888;">STATUS:</span> ${tanker.status}<br>
                    <span style="color: #888;">COORDS:</span> ${tanker.lat.toFixed(2)}, ${tanker.lon.toFixed(2)}
                </div>
            `;

            marker.bindPopup(popupContent, {
                className: 'vessel-popup',
                maxWidth: 250
            });

            // Heading line (if moving)
            if (tanker.heading && tanker.status === 'MOVING') {
                const headingRad = (tanker.heading - 90) * (Math.PI / 180);
                const distance = 1.5; // degrees
                const endLat = tanker.lat + Math.sin(headingRad) * distance;
                const endLon = tanker.lon + Math.cos(headingRad) * distance;

                const line = L.polyline(
                    [[tanker.lat, tanker.lon], [endLat, endLon]],
                    { color: '#00ff00', weight: 2, opacity: 0.7 }
                ).addTo(leafletMap);

                vesselMarkers.push(line);
            }

            vesselMarkers.push(marker);
        });

        console.log(`[HD Map] Rendered ${vesselMarkers.length} vessels`);
    }

    function addRegionalOverlays() {
        // Define major trading regions with market sentiment
        const regions = [
            { name: "NORTH AMERICA", lat: 40, lon: -100, sentiment: "BULLISH", risk: 2.5 },
            { name: "EUROPE", lat: 50, lon: 10, sentiment: "NEUTRAL", risk: 3.2 },
            { name: "MIDDLE EAST", lat: 25, lon: 50, sentiment: "VOLATILE", risk: 7.8 },
            { name: "ASIA PACIFIC", lat: 30, lon: 110, sentiment: "BEARISH", risk: 5.1 },
            { name: "SOUTH AMERICA", lat: -15, lon: -60, sentiment: "STABLE", risk: 2.0 }
        ];

        regions.forEach(region => {
            // Color based on sentiment
            let color = '#00aaff';
            if (region.sentiment === 'BULLISH') color = '#00ff00';
            if (region.sentiment === 'BEARISH') color = '#ff3300';
            if (region.sentiment === 'VOLATILE') color = '#ff9900';

            // Circle overlay (market influence radius)
            const circle = L.circle([region.lat, region.lon], {
                color: color,
                fillColor: color,
                fillOpacity: 0.1,
                radius: 2000000, // 2000km radius
                weight: 1
            }).addTo(leafletMap);

            // Label
            const label = L.marker([region.lat, region.lon], {
                icon: L.divIcon({
                    className: 'region-label',
                    html: `<div style="background: rgba(0,0,0,0.8); border: 1px solid ${color}; color: ${color}; padding: 5px; font-size: 10px; white-space: nowrap;">
                        <b>${region.name}</b><br>
                        ${region.sentiment} | RISK: ${region.risk}
                    </div>`,
                    iconSize: [120, 40],
                    iconAnchor: [60, 20]
                })
            }).addTo(leafletMap);

            regionMarkers.push(circle, label);
        });
    }

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

            const logRes = await fetch('/command', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ command: 'TODAY' })
            });
            const logData = await logRes.json();
            eventLog.innerHTML = logData.data.map(e =>
                `[${e.Time}] ${e.Description} <span style="color:#555">(R:${e.Relevance})</span>`
            ).join('\n');

        } catch (err) { }
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
            mainChart.style.display = 'block';
            leafletMapDiv.style.display = 'none';
            toggleMapBtn.innerText = 'SWITCH TO HD MAP';

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
            activeMode = 'MAP_CANVAS';
            mapAssets = data.assets;
            mapTitle = data.title;
            if (data.metrics) mapTitle += ` [${data.metrics}]`;

            mainChart.style.display = 'block';
            leafletMapDiv.style.display = 'none';
            toggleMapBtn.innerText = 'SWITCH TO HD MAP';

            document.getElementById('chartSymbol').innerText = "ASSET MAP";
            renderMainView();
            detailView.innerHTML = `
            <div style="font-size: 14px; font-weight:bold; margin-bottom:10px">${data.title}</div>
            STATUS: ACTIVE MONITORING<br>
            FLEET: ${data.assets.length} VESSELS<br>
            LOGIC: SUPPLY CHAIN MONITORING ENABLED<br><br>
            <button onclick="document.getElementById('toggleMapMode').click()" style="background: #111; color: #00ff00; border: 1px solid #00ff00; padding: 5px 10px; cursor: pointer; font-family: 'Inconsolata', monospace;">
                SWITCH TO HD INTERACTIVE MAP
            </button>`;
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

        if (chartBands) {
            const lower = chartBands.lower.filter(v => v);
            const upper = chartBands.upper.filter(v => v);
            if (lower.length) min = Math.min(min, ...lower);
            if (upper.length) max = Math.max(max, ...upper);
        }

        min *= 0.999;
        max *= 1.001;
        const range = max - min;

        // Bollinger Bands
        if (chartBands && chartBands.upper.length) {
            ctx.beginPath();
            chartBands.upper.forEach((v, i) => {
                const x = (i / (chartData.length - 1)) * w;
                const y = h - ((v - min) / range) * h;
                if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
            });
            for (let i = chartBands.lower.length - 1; i >= 0; i--) {
                const v = chartBands.lower[i];
                const x = (i / (chartData.length - 1)) * w;
                const y = h - ((v - min) / range) * h;
                ctx.lineTo(x, y);
            }
            ctx.closePath();
            ctx.fillStyle = 'rgba(0, 80, 200, 0.15)';
            ctx.fill();
            ctx.strokeStyle = 'rgba(0, 80, 200, 0.3)';
            ctx.stroke();
        }

        // Price Line
        ctx.beginPath();
        ctx.strokeStyle = '#00aaff';
        ctx.lineWidth = 2;
        chartData.forEach((d, i) => {
            const x = (i / (chartData.length - 1)) * w;
            const y = h - ((d.p - min) / range) * h;
            if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
        });
        ctx.stroke();

        // Grid
        ctx.strokeStyle = '#222'; ctx.lineWidth = 1; ctx.beginPath();
        for (let i = 1; i < 5; i++) { const y = (i / 5) * h; ctx.moveTo(0, y); ctx.lineTo(w, y); }
        ctx.stroke();

        // Last Price
        const last = chartData[chartData.length - 1];
        const lastY = h - ((last.p - min) / range) * h;
        ctx.fillStyle = '#ff9900';
        ctx.font = '11px Inconsolata';
        ctx.fillText(last.p.toFixed(2), w - 50, lastY - 5);

        // Disruption Warning
        if (chartBands && chartBands.upper.length) {
            const lastUpper = chartBands.upper[chartBands.upper.length - 1];
            if (last.p > lastUpper) {
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

        // Grid
        ctx.strokeStyle = '#222';
        ctx.lineWidth = 1;
        ctx.beginPath();
        for (let i = 1; i < 8; i++) { const x = (i / 8) * w; ctx.moveTo(x, 0); ctx.lineTo(x, h); }
        for (let i = 1; i < 6; i++) { const y = (i / 6) * h; ctx.moveTo(0, y); ctx.lineTo(w, y); }
        ctx.stroke();

        // Vessels with labels
        mapAssets.forEach(tanker => {
            const x = ((tanker.lon + 180) / 360) * w;
            const y = ((90 - tanker.lat) / 180) * h;

            ctx.fillStyle = tanker.status === 'MOVING' ? '#00ff00' : '#ffaa00';
            ctx.beginPath();
            ctx.arc(x, y, 4, 0, Math.PI * 2);
            ctx.fill();
            ctx.strokeStyle = tanker.status === 'MOVING' ? '#00ff00' : '#ffaa00';
            ctx.lineWidth = 1;
            ctx.stroke();

            if (tanker.heading && tanker.status === 'MOVING') {
                const rad = (tanker.heading - 90) * (Math.PI / 180);
                ctx.strokeStyle = '#00ff00';
                ctx.lineWidth = 2;
                ctx.beginPath();
                ctx.moveTo(x, y);
                ctx.lineTo(x + Math.cos(rad) * 15, y + Math.sin(rad) * 15);
                ctx.stroke();
            }

            // Labels
            ctx.font = '9px Inconsolata';
            ctx.textAlign = 'left';
            const labelX = x + 10;
            let labelY = y - 40;
            const lines = [
                `${tanker.origin_flag || ''} ${tanker.name}`,
                `${tanker.cargo_grade || 'OIL'} (${tanker.cargo_level || 0}%)`,
                `${tanker.origin_port || 'ORIGIN'} → ${tanker.dest || 'DEST'}`,
                `${tanker.vessel_type || 'VLCC'} | ${tanker.speed_knots || 0}kn`
            ];

            let maxWidth = 0;
            lines.forEach(line => {
                const metrics = ctx.measureText(line);
                if (metrics.width > maxWidth) maxWidth = metrics.width;
            });

            ctx.fillStyle = 'rgba(0, 0, 0, 0.85)';
            ctx.fillRect(labelX - 2, labelY - 10, maxWidth + 4, lines.length * 11 + 4);
            ctx.strokeStyle = tanker.status === 'MOVING' ? '#00ff00' : '#ffaa00';
            ctx.lineWidth = 1;
            ctx.strokeRect(labelX - 2, labelY - 10, maxWidth + 4, lines.length * 11 + 4);
            ctx.fillStyle = '#ffffff';
            lines.forEach((line, i) => {
                ctx.fillText(line, labelX, labelY + (i * 11));
            });
        });

        ctx.fillStyle = '#fff';
        ctx.font = '14px Inconsolata';
        ctx.textAlign = 'left';
        ctx.fillText(mapTitle, 10, 20);

        ctx.font = '10px Inconsolata';
        ctx.fillStyle = '#00ff00';
        ctx.fillText('● MOVING', 10, h - 30);
        ctx.fillStyle = '#ffaa00';
        ctx.fillText('● ANCHORED', 10, h - 15);
    }

    window.executeCommand = executeCommand;
});
