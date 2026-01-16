// Ordinary Mode Terminal Logic

const commandInput = document.getElementById('commandInput');
const terminalOutput = document.getElementById('terminalOutput');

// Allowed commands in Ordinary mode
const ALLOWED_COMMANDS = ['NIFTY', 'CHART', 'QUOTE', 'HELP', 'OVERVIEW', 'TODAY', 'NEWS'];

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

    // Check if command is allowed in Ordinary mode
    const baseCommand = command.split(' ')[0];
    if (!ALLOWED_COMMANDS.includes(baseCommand)) {
        addOutput(`❌ Command "${baseCommand}" is not available in Ordinary Mode.`, 'output-error');
        addOutput(`💼 Upgrade to Enterprise Mode for advanced features.`, 'output-error');
        commandInput.value = '';
        return;
    }

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

    data.slice(0, 10).forEach((stock, idx) => {
        const changeColor = stock.change_pct >= 0 ? '\x1b[32m' : '\x1b[31m';
        const changeSymbol = stock.change_pct >= 0 ? '▲' : '▼';

        addOutput(
            `${idx + 1}. ${stock.symbol.padEnd(15)} ₹${stock.price.toFixed(2).padStart(10)} ${changeSymbol} ${stock.change_pct.toFixed(2)}%`,
            stock.change_pct >= 0 ? 'output-success' : 'output-error'
        );
    });

    addOutput('═'.repeat(80), 'output-line');
    addOutput(`Showing 10 of ${data.length} stocks. Use CHART [SYMBOL] for details.`, 'output-line');
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
    addOutput('📚 AVAILABLE COMMANDS (ORDINARY MODE)', 'output-success');
    addOutput('═'.repeat(80), 'output-line');

    response.sections.forEach(section => {
        if (['DASHBOARDS', 'ANALYSIS', 'SYSTEM'].includes(section.category)) {
            addOutput(`\n${section.category}:`, 'output-success');
            section.cmds.forEach(cmd => {
                addOutput(`  • ${cmd}`, 'output-line');
            });
        }
    });

    addOutput('\n═'.repeat(80), 'output-line');
    addOutput('💼 Upgrade to Enterprise Mode for advanced features:', 'output-line');
    addOutput('  • Volatility Analysis (VOL)', 'output-line');
    addOutput('  • Heatmap Visualizations (HEATMAP)', 'output-line');
    addOutput('  • Correlation Matrix (CORR)', 'output-line');
    addOutput('  • Bloomberg Features (FX, SECTORS, CALENDAR)', 'output-line');
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

console.log('%c📊 Ordinary Mode Active', 'color: #10b981; font-size: 16px; font-weight: bold;');
