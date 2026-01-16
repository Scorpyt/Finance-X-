// Enterprise Mode Terminal Logic

const commandInput = document.getElementById('commandInput');
const terminalOutput = document.getElementById('terminalOutput');

// Command history
let commandHistory = [];
let historyIndex = -1;

// Focus input on load
commandInput.focus();

// Enter key to execute
commandInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        executeCommand();
    }
});

// Arrow keys for history
commandInput.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowUp') {
        e.preventDefault();
        if (historyIndex < commandHistory.length - 1) {
            historyIndex++;
            commandInput.value = commandHistory[commandHistory.length - 1 - historyIndex];
        }
    } else if (e.key === 'ArrowDown') {
        e.preventDefault();
        if (historyIndex > 0) {
            historyIndex--;
            commandInput.value = commandHistory[commandHistory.length - 1 - historyIndex];
        } else if (historyIndex === 0) {
            historyIndex = -1;
            commandInput.value = '';
        }
    }
});

async function executeCommand() {
    const command = commandInput.value.trim().toUpperCase();

    if (!command) return;

    // Add to history
    commandHistory.push(command);
    historyIndex = -1;

    // Display command
    addOutput(`> ${command}`, 'output-success');

    // Show loading
    addOutput('⏳ Processing...', 'output-line');

    try {
        const response = await fetch('/api/command', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ command: command })
        });

        const data = await response.json();

        // Remove loading message
        removeLastOutput();

        // Display result
        displayResponse(data);

    } catch (error) {
        removeLastOutput();
        addOutput(`❌ Error: ${error.message}`, 'output-error');
        addOutput('⚠️  Make sure the Python backend is running on port 8000', 'output-error');
    }

    commandInput.value = '';
    scrollToBottom();
}

function displayResponse(response) {
    switch (response.type) {
        case 'OVERVIEW_GRID':
            displayMarketGrid(response.data);
            break;
        case 'CHART_FULL':
            displayChart(response);
            break;
        case 'VOLATILITY_VIEW':
            displayVolatility(response);
            break;
        case 'VOLSCAN_VIEW':
            displayVolScan(response);
            break;
        case 'HEATMAP_VIEW':
            displayHeatmap(response);
            break;
        case 'CORRELATION_VIEW':
            displayCorrelation(response);
            break;
        case 'FX_VIEW':
            displayFX(response);
            break;
        case 'SECTORS_VIEW':
            displaySectors(response);
            break;
        case 'TEXT':
            addOutput(`📊 ${response.title}`, 'output-success');
            addOutput(response.content, 'output-line');
            break;
        case 'HELP_MENU':
            displayHelp(response);
            break;
        case 'ERROR':
            addOutput(`❌ ${response.content}`, 'output-error');
            break;
        default:
            addOutput(JSON.stringify(response, null, 2), 'output-line');
    }
}

function displayMarketGrid(data) {
    addOutput('📈 NIFTY 50 MARKET SNAPSHOT', 'output-success');
    addOutput('═'.repeat(80), 'output-line');

    data.slice(0, 15).forEach((stock, idx) => {
        const changeSymbol = stock.change_pct >= 0 ? '▲' : '▼';
        addOutput(
            `${(idx + 1).toString().padStart(2)}. ${stock.symbol.padEnd(15)} ₹${stock.price.toFixed(2).padStart(10)} ${changeSymbol} ${stock.change_pct.toFixed(2)}%`,
            stock.change_pct >= 0 ? 'output-success' : 'output-error'
        );
    });

    addOutput('═'.repeat(80), 'output-line');
    addOutput(`💡 Use VOL [SYMBOL] for volatility analysis`, 'output-line');
}

function displayVolatility(response) {
    addOutput(`📊 VOLATILITY ANALYSIS: ${response.symbol}`, 'output-success');
    addOutput('═'.repeat(80), 'output-line');
    addOutput(`Current Price: ₹${response.current_price.toFixed(2)}`, 'output-line');
    addOutput(`Volatility Regime: ${response.regime}`, response.regime === 'HIGH_VOL' ? 'output-error' : 'output-success');
    addOutput('', 'output-line');

    addOutput('Metrics:', 'output-success');
    Object.entries(response.metrics).forEach(([key, value]) => {
        addOutput(`  ${key}: ${value}`, 'output-line');
    });

    addOutput('', 'output-line');
    addOutput('Comparison:', 'output-success');
    Object.entries(response.comparison).forEach(([key, value]) => {
        addOutput(`  ${key}: ${value}`, 'output-line');
    });
    addOutput('═'.repeat(80), 'output-line');
}

function displayVolScan(response) {
    addOutput(`🔥 HIGH VOLATILITY SCANNER`, 'output-success');
    addOutput('═'.repeat(80), 'output-line');
    addOutput(`Found ${response.count} high volatility stocks`, 'output-line');
    addOutput('', 'output-line');

    response.data.forEach((stock, idx) => {
        addOutput(
            `${idx + 1}. ${stock.symbol.padEnd(15)} ₹${stock.price.toFixed(2).padStart(10)} | Vol: ${(stock.volatility * 100).toFixed(2)}% | ${stock.regime}`,
            stock.regime === 'HIGH_VOL' ? 'output-error' : 'output-line'
        );
    });
    addOutput('═'.repeat(80), 'output-line');
}

function displayHeatmap(response) {
    addOutput(`🗺️  ${response.title}`, 'output-success');
    addOutput('═'.repeat(80), 'output-line');
    addOutput('Heatmap data received. Visual rendering available in browser UI.', 'output-line');
    addOutput('Top performers:', 'output-success');

    if (response.data && response.data.data) {
        response.data.data.slice(0, 10).forEach((item, idx) => {
            const label = item.sector || item.symbol || 'N/A';
            const value = item.display_value || item.value;
            addOutput(`  ${idx + 1}. ${label}: ${value}`, 'output-line');
        });
    }
    addOutput('═'.repeat(80), 'output-line');
}

function displayCorrelation(response) {
    addOutput(`🔗 CORRELATION MATRIX`, 'output-success');
    addOutput('═'.repeat(80), 'output-line');
    addOutput('Correlation analysis complete. Matrix available in browser UI.', 'output-line');
    addOutput('Strong correlations detected:', 'output-success');
    addOutput('  • Use for portfolio diversification', 'output-line');
    addOutput('  • Identify pair trading opportunities', 'output-line');
    addOutput('═'.repeat(80), 'output-line');
}

function displayFX(response) {
    addOutput(`💱 FOREIGN EXCHANGE RATES`, 'output-success');
    addOutput('═'.repeat(80), 'output-line');

    if (response.rates) {
        response.rates.forEach(rate => {
            const changeSymbol = rate.change_pct >= 0 ? '▲' : '▼';
            addOutput(
                `${rate.pair.padEnd(15)} ${rate.rate.toFixed(4).padStart(10)} ${changeSymbol} ${rate.change_pct.toFixed(2)}%`,
                rate.change_pct >= 0 ? 'output-success' : 'output-error'
            );
        });
    }
    addOutput('═'.repeat(80), 'output-line');
}

function displaySectors(response) {
    addOutput(`📊 SECTOR PERFORMANCE`, 'output-success');
    addOutput('═'.repeat(80), 'output-line');

    if (response.sectors) {
        response.sectors.forEach((sector, idx) => {
            const changeSymbol = sector.change_pct >= 0 ? '▲' : '▼';
            addOutput(
                `${(idx + 1).toString().padStart(2)}. ${sector.sector.padEnd(20)} ${changeSymbol} ${sector.change_pct.toFixed(2)}%`,
                sector.change_pct >= 0 ? 'output-success' : 'output-error'
            );
        });
    }
    addOutput('═'.repeat(80), 'output-line');
    addOutput('💡 Use HEATMAP SECTOR for visual representation', 'output-line');
}

function displayChart(response) {
    addOutput(`📊 CHART: ${response.symbol}`, 'output-success');
    addOutput('═'.repeat(80), 'output-line');

    const history = response.history.slice(-10);
    history.forEach(point => {
        addOutput(`${point.t}: ₹${point.p.toFixed(2)} | Vol: ${point.v}`, 'output-line');
    });

    addOutput('═'.repeat(80), 'output-line');
    addOutput(`Bollinger Bands: Upper=${response.bands.upper.toFixed(2)}, Mid=${response.bands.middle.toFixed(2)}, Lower=${response.bands.lower.toFixed(2)}`, 'output-line');
}

function displayHelp(response) {
    addOutput('📚 AVAILABLE COMMANDS (ENTERPRISE MODE)', 'output-success');
    addOutput('═'.repeat(80), 'output-line');

    response.sections.forEach(section => {
        addOutput(`\n${section.category}:`, 'output-success');
        section.cmds.forEach(cmd => {
            addOutput(`  • ${cmd}`, 'output-line');
        });
    });

    addOutput('\n═'.repeat(80), 'output-line');
}

function addOutput(text, className = 'output-line') {
    const line = document.createElement('div');
    line.className = className;
    line.textContent = text;

    // Animate entry
    gsap.from(line, {
        opacity: 0,
        x: -20,
        duration: 0.3,
        ease: 'power2.out'
    });

    terminalOutput.appendChild(line);
}

function removeLastOutput() {
    const lastLine = terminalOutput.lastElementChild;
    if (lastLine) {
        lastLine.remove();
    }
}

function scrollToBottom() {
    terminalOutput.scrollTop = terminalOutput.scrollHeight;
}

// Animate terminal on load
gsap.from('.terminal-container', {
    opacity: 0,
    y: 50,
    duration: 1,
    ease: 'power3.out'
});

// Particle effect for enterprise mode
const canvas = document.createElement('canvas');
canvas.style.position = 'fixed';
canvas.style.top = '0';
canvas.style.left = '0';
canvas.style.width = '100%';
canvas.style.height = '100%';
canvas.style.zIndex = '0';
canvas.style.opacity = '0.1';
canvas.style.pointerEvents = 'none';
document.body.insertBefore(canvas, document.body.firstChild);

console.log('%c💼 Enterprise Mode Active', 'color: #3b82f6; font-size: 16px; font-weight: bold;');
console.log('%c🚀 All Features Unlocked', 'color: #10b981; font-size: 14px;');
