// Workflow and Pipeline Definitions

export const workflows = [
    {
        id: 'command-flow',
        name: 'Command Processing',
        description: 'How user commands are processed from terminal to response',
        steps: [
            {
                id: 1,
                title: 'User Input',
                description: 'User enters command in Terminal UI (e.g., "NIFTY")',
                file: '/Users/aayush/Finance-X-/static/terminal.js',
                function: 'sendCommand()',
            },
            {
                id: 2,
                title: 'HTTP Request',
                description: 'POST /command sent to FastAPI server',
                file: '/Users/aayush/Finance-X-/server.py',
                function: 'process_command()',
            },
            {
                id: 3,
                title: 'Command Routing',
                description: 'Server parses command and routes to appropriate engine',
                file: '/Users/aayush/Finance-X-/server.py',
                details: 'NIFTY → india_engine, FX → bloomberg_engine, STUDY → study_engine',
            },
            {
                id: 4,
                title: 'Engine Processing',
                description: 'Engine fetches data (yfinance) or computes analysis',
                file: '/Users/aayush/Finance-X-/india_engine.py',
                function: 'fetch_market_snapshot()',
            },
            {
                id: 5,
                title: 'Response Formatting',
                description: 'Data packaged as JSON with type (TABLE, CHART, etc.)',
                file: '/Users/aayush/Finance-X-/server.py',
            },
            {
                id: 6,
                title: 'UI Rendering',
                description: 'Terminal.js renders response based on type',
                file: '/Users/aayush/Finance-X-/static/terminal.js',
                function: 'renderResponse()',
            },
        ],
    },
    {
        id: 'market-data-flow',
        name: 'Market Data Pipeline',
        description: 'How live market data flows through the system',
        steps: [
            {
                id: 1,
                title: 'yfinance API',
                description: 'External API provides real-time stock data',
                external: true,
            },
            {
                id: 2,
                title: 'India Engine',
                description: 'Fetches NIFTY 50 data with parallel threading',
                file: '/Users/aayush/Finance-X-/india_engine.py',
                function: 'fetch_market_snapshot()',
            },
            {
                id: 3,
                title: 'Cache Layer',
                description: '60-second TTL cache prevents API overload',
                file: '/Users/aayush/Finance-X-/india_engine.py',
                details: 'Uses timestamp-based cache invalidation',
            },
            {
                id: 4,
                title: 'Data Processing',
                description: 'Calculate change%, SMA, trends',
                file: '/Users/aayush/Finance-X-/india_engine.py',
                function: 'get_stock_analysis()',
            },
            {
                id: 5,
                title: 'Server Response',
                description: 'Processed data returned to client',
                file: '/Users/aayush/Finance-X-/server.py',
            },
        ],
    },
    {
        id: 'risk-detection-flow',
        name: 'Risk Detection Pipeline',
        description: 'How system detects and responds to market risk',
        steps: [
            {
                id: 1,
                title: 'Event Ingestion',
                description: 'Market events added with base_impact score',
                file: '/Users/aayush/Finance-X-/engine.py',
                function: 'ingest(event)',
            },
            {
                id: 2,
                title: 'Decay Processing',
                description: 'Event weights decay over time: weight = score × e^(-rate × time)',
                file: '/Users/aayush/Finance-X-/engine.py',
                function: 'apply_decay()',
            },
            {
                id: 3,
                title: 'Risk Calculation',
                description: 'Sum all event weights to get total_risk',
                file: '/Users/aayush/Finance-X-/engine.py',
                function: 'detect_state()',
            },
            {
                id: 4,
                title: 'State Classification',
                description: 'risk > 25 → CRASH, risk > 15 → HIGH_VOL, else STABLE',
                file: '/Users/aayush/Finance-X-/engine.py',
            },
            {
                id: 5,
                title: 'Market Simulation',
                description: 'Prices updated with state-based volatility multipliers',
                file: '/Users/aayush/Finance-X-/engine.py',
                function: 'update_prices()',
            },
            {
                id: 6,
                title: 'Alert Generation',
                description: 'Portfolio health check for disruption mode',
                file: '/Users/aayush/Finance-X-/india_engine.py',
                function: 'check_portfolio_health()',
            },
        ],
    },
    {
        id: 'bloomberg-flow',
        name: 'Bloomberg Features',
        description: 'Professional market analysis features',
        steps: [
            {
                id: 1,
                title: 'FX Rates',
                description: '8 currency pairs: USD/INR, EUR/USD, BTC/USD, etc.',
                file: '/Users/aayush/Finance-X-/bloomberg_engine.py',
                function: 'get_fx_rates()',
            },
            {
                id: 2,
                title: 'Sector Performance',
                description: '10 US sector ETFs: XLK, XLF, XLE, etc.',
                file: '/Users/aayush/Finance-X-/bloomberg_engine.py',
                function: 'get_sector_performance()',
            },
            {
                id: 3,
                title: 'Stock Screener',
                description: 'Filter by GAINERS, LOSERS, VOLUME, VOLATILE',
                file: '/Users/aayush/Finance-X-/bloomberg_engine.py',
                function: 'screen_stocks()',
            },
            {
                id: 4,
                title: 'Economic Calendar',
                description: 'Fed decisions, CPI, GDP, RBI meetings',
                file: '/Users/aayush/Finance-X-/bloomberg_engine.py',
                function: 'get_economic_calendar()',
            },
        ],
    },
];

export const getWorkflowById = (id) => {
    return workflows.find(w => w.id === id);
};
