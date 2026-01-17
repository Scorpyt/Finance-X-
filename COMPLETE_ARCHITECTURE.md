# Finance-X Complete Architecture & Workflow

## 📋 Table of Contents
1. [System Overview](#system-overview)
2. [Architecture Diagram](#architecture-diagram)
3. [File Structure & Dependencies](#file-structure--dependencies)
4. [Data Flow](#data-flow)
5. [Component Details](#component-details)
6. [Docker Deployment](#docker-deployment)

---

## System Overview

Finance-X is a **real-time financial intelligence terminal** that combines:
- Live market data from Indian (NSE) and global markets
- AI-powered analysis and risk detection
- Bloomberg-style professional features
- Educational resources and news feeds
- Hardware-optimized performance engine

### Technology Stack
- **Backend**: FastAPI (Python 3.11)
- **Data Sources**: yfinance, RSS feeds
- **Database**: SQLite (finance.db, users.db)
- **Frontend**: Vanilla HTML/CSS/JavaScript
- **Deployment**: Docker, Uvicorn

---

## Architecture Diagram

```mermaid
graph TB
    subgraph "Client Layer"
        UI[Terminal UI<br/>index.html + terminal.js]
    end
    
    subgraph "API Layer"
        SERVER[server.py<br/>FastAPI Application]
        BLOOMBERG_API[bloomberg_service.py<br/>Microservice API]
    end
    
    subgraph "Core Engines"
        ENGINE[engine.py<br/>Intelligence Engine]
        INDIA[india_engine.py<br/>NSE Market Engine]
        BLOOMBERG[bloomberg_engine.py<br/>Bloomberg Features]
        STUDY[study_engine.py<br/>News & Learning]
        PERF[performance_engine.py<br/>Hardware Optimizer]
    end
    
    subgraph "Support Modules"
        ANALYST[analyst.py<br/>Event Analysis]
        MODELS[models.py<br/>Data Models]
        DB[database.py<br/>SQLite Manager]
        USER[user_data.py<br/>Portfolio Manager]
    end
    
    subgraph "Data Storage"
        FINDB[(finance.db)]
        USERDB[(users.db)]
    end
    
    subgraph "External Services"
        YFINANCE[yfinance API<br/>Market Data]
        RSS[RSS Feeds<br/>News Data]
    end
    
    UI -->|HTTP Requests| SERVER
    UI -->|HTTP Requests| BLOOMBERG_API
    
    SERVER --> ENGINE
    SERVER --> INDIA
    SERVER --> BLOOMBERG
    SERVER --> STUDY
    SERVER --> ANALYST
    SERVER --> USER
    
    BLOOMBERG_API --> BLOOMBERG
    
    ENGINE --> MODELS
    ENGINE --> DB
    ENGINE --> PERF
    
    INDIA --> YFINANCE
    BLOOMBERG --> YFINANCE
    STUDY --> RSS
    
    DB --> FINDB
    DB --> USERDB
    USER --> USERDB
    
    style SERVER fill:#4CAF50
    style ENGINE fill:#2196F3
    style BLOOMBERG_API fill:#FF9800
    style YFINANCE fill:#9C27B0
```

---

## File Structure & Dependencies

### 📁 Project Root Structure

```
Finance-X/
├── 🐳 Docker Configuration
│   ├── Dockerfile                    # Main app container
│   ├── Dockerfile.bloomberg          # Bloomberg microservice
│   ├── docker-compose.yml            # Main orchestration
│   ├── docker-compose.bloomberg.yml  # Bloomberg service
│   ├── .dockerignore                 # Docker ignore rules
│   ├── DOCKER.md                     # Docker documentation
│   └── BLOOMBERG_DOCKER.md           # Bloomberg Docker docs
│
├── 🎯 Core Application
│   ├── server.py                     # Main FastAPI server
│   ├── bloomberg_service.py          # Bloomberg API service
│   ├── main.py                       # Alternative entry point
│   └── terminal_ui.py                # Terminal UI server
│
├── 🧠 Intelligence Engines
│   ├── engine.py                     # Core intelligence engine
│   ├── india_engine.py               # NSE market engine
│   ├── bloomberg_engine.py           # Bloomberg features
│   ├── study_engine.py               # News & learning
│   └── performance_engine.py         # Performance optimizer
│
├── 🔧 Support Modules
│   ├── analyst.py                    # Event analysis
│   ├── models.py                     # Data models
│   ├── database.py                   # Database manager
│   └── user_data.py                  # User portfolio
│
├── 🗄️ Databases
│   ├── finance.db                    # Market data storage
│   └── users.db                      # User data storage
│
├── 🎨 Frontend
│   └── static/
│       ├── index.html                # Main UI
│       ├── terminal.js               # Terminal logic
│       ├── terminal.css              # Styling
│       └── commodity_risk.js         # Risk analysis
│
├── 🔌 Extensions
│   └── extensions/
│       ├── __init__.py
│       ├── audit.py                  # Audit logging
│       ├── command_handlers.py       # Command processing
│       ├── data_feeds.py             # Data feed handlers
│       ├── enhanced_models.py        # Extended models
│       ├── persistence.py            # Data persistence
│       ├── wri_aqueduct.py          # WRI integration
│       ├── wri_models.py            # WRI data models
│       └── yfinance_data.py         # yfinance wrapper
│
├── 📦 Configuration
│   ├── requirements.txt              # Python dependencies
│   ├── requirements_extended.txt     # Extended deps
│   ├── runtime.txt                   # Python version
│   ├── Procfile                      # Deployment config
│   └── render.yaml                   # Render.com config
│
└── 📚 Documentation
    ├── README.md
    ├── DOCKER.md
    ├── BLOOMBERG_DOCKER.md
    └── WORKFLOW_PIPELINE_AND_FRAMEWORK.md
```

---

## Data Flow

### 1. User Command Flow

```mermaid
sequenceDiagram
    participant User
    participant UI as Terminal UI
    participant Server as server.py
    participant Engine as Core Engines
    participant DB as Database
    participant External as External APIs
    
    User->>UI: Enter Command (e.g., "NIFTY")
    UI->>Server: POST /command
    Server->>Server: Parse Command
    
    alt Market Data Command
        Server->>Engine: india_engine.fetch_market_snapshot()
        Engine->>External: yfinance.download()
        External-->>Engine: Market Data
        Engine-->>Server: Processed Data
    else Analysis Command
        Server->>Engine: engine.detect_state()
        Engine->>DB: Query Events
        DB-->>Engine: Historical Data
        Engine-->>Server: Analysis Result
    else Bloomberg Command
        Server->>Engine: bloomberg_engine.get_fx_rates()
        Engine->>External: yfinance API
        External-->>Engine: FX Data
        Engine-->>Server: FX Rates
    end
    
    Server-->>UI: JSON Response
    UI-->>User: Render Result
```

### 2. Market Data Update Flow

```mermaid
graph LR
    A[yfinance API] -->|Raw Data| B[India Engine]
    A -->|Raw Data| C[Bloomberg Engine]
    
    B -->|Process| D[Market Snapshot]
    C -->|Process| E[FX/Sector Data]
    
    D --> F[Cache Layer]
    E --> F
    
    F -->|60s TTL| G[server.py]
    
    G -->|Response| H[Terminal UI]
    
    style A fill:#9C27B0
    style F fill:#FFC107
    style G fill:#4CAF50
```

### 3. Risk Detection Flow

```mermaid
graph TB
    A[Market Events] --> B[engine.py<br/>Intelligence Engine]
    C[Price Updates] --> B
    
    B --> D[Apply Decay]
    D --> E[Calculate Risk Score]
    E --> F{Risk Threshold}
    
    F -->|Score > 25| G[CRASH State]
    F -->|Score 15-25| H[HIGH_VOL State]
    F -->|Score < 15| I[STABLE State]
    
    G --> J[Update System State]
    H --> J
    I --> J
    
    J --> K[Store in Database]
    J --> L[Return to Client]
    
    style B fill:#2196F3
    style F fill:#FF5722
    style K fill:#607D8B
```

---

## Component Details

### 🎯 Core Application Layer

#### [server.py](file:///Users/aayush/Finance-X-/server.py)
**Role**: Main FastAPI application server

**Key Responsibilities**:
- Route HTTP requests to appropriate engines
- Command parsing and execution
- Session management and authentication
- Static file serving

**Dependencies**:
```python
from engine import IntelligenceEngine
from india_engine import IndiaMarketEngine
from bloomberg_engine import BloombergEngine
from study_engine import StudyEngine
from analyst import Analyst
from user_data import UserManager
```

**Key Endpoints**:
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/command` | POST | Process terminal commands |
| `/status` | GET | Get system state |
| `/market` | GET | Get all ticker data |
| `/system/diagnostics` | GET | Hardware metrics |

**Command Routing**:
```
TODAY → Event log display
NIFTY → India market snapshot
FX → Foreign exchange rates
SECTORS → Sector performance
MOVERS → Top gainers/losers
STUDY → News and learning
CHART [SYM] → Price chart
EVAL [SYM] → Stock analysis
```

---

#### [bloomberg_service.py](file:///Users/aayush/Finance-X-/bloomberg_service.py)
**Role**: Standalone Bloomberg microservice API

**Key Features**:
- Independent FastAPI service on port 8001
- REST API for Bloomberg features
- CORS enabled for cross-origin requests
- Health check endpoint

**API Endpoints**:
| Endpoint | Purpose |
|----------|---------|
| `GET /health` | Health check |
| `GET /fx-rates` | Live FX rates |
| `GET /sectors` | Sector performance |
| `GET /economic-calendar` | Economic events |
| `GET /screen` | Stock screener |
| `GET /top-movers` | Top gainers/losers |

**Effect**: Allows Bloomberg features to run as independent microservice, enabling:
- Separate scaling
- Independent deployment
- Service isolation
- Load distribution

---

### 🧠 Intelligence Engines

#### [engine.py](file:///Users/aayush/Finance-X-/engine.py)
**Role**: Core intelligence and risk detection engine

**Key Classes**:

##### `IntelligenceEngine`
**Purpose**: Central brain of the system

**Node Effects**:
```mermaid
graph LR
    A[Market Events] -->|ingest| B[IntelligenceEngine]
    C[Time Progression] -->|apply_decay| B
    B -->|detect_state| D[Risk Score]
    B -->|update_prices| E[Market Simulator]
    E --> F[Price Updates]
    D --> G[System State]
    
    style B fill:#2196F3
```

**Key Methods**:
- `ingest(event)` - Add new market event
- `apply_decay(time)` - Apply time-based decay to event weights
- `detect_state(time)` - Calculate risk score and determine system state
- `get_ticker(symbol)` - Retrieve ticker data
- `get_all_tickers()` - Get all market data

**State Detection Logic**:
```python
if risk_score > 25.0:
    state = CRASH
elif risk_score > 15.0:
    state = HIGH_VOL
else:
    state = STABLE
```

##### `TechnicalAnalysis`
**Purpose**: Technical indicator calculations

**Methods**:
- `calculate_bollinger_bands()` - Bollinger Bands calculation
- `analyze_risk_depth()` - Risk depth analysis based on price position

##### `MarketSimulator`
**Purpose**: Simulates price movements

**Tickers Tracked**:
- SPX (S&P 500)
- NDX (Nasdaq 100)
- BTC (Bitcoin)
- VIX (Volatility Index)
- AAPL, NVDA, JPM, XOM, WTI

**Price Update Logic**:
```python
volatility = base_volatility * risk_multiplier
shock = random.normal(0, volatility)
new_price = current_price * (1 + shock + bias)
```

---

#### [india_engine.py](file:///Users/aayush/Finance-X-/india_engine.py)
**Role**: Real-time bridge to Indian stock market (NSE)

**Key Class**: `IndiaMarketEngine`

**Node Effects**:
```mermaid
graph TB
    A[NIFTY 50 Symbols] --> B[IndiaMarketEngine]
    B -->|yfinance.download| C[Live Market Data]
    C --> D[Process & Cache]
    D --> E[Market Snapshot]
    D --> F[Stock Analysis]
    D --> G[Portfolio Health]
    
    E --> H[server.py NIFTY command]
    F --> I[server.py EVAL command]
    G --> J[server.py DISRUPTION command]
    
    style B fill:#FF9800
    style D fill:#FFC107
```

**Tracked Symbols**: 49 NIFTY 50 constituents
- RELIANCE.NS, TCS.NS, INFY.NS, HDFCBANK.NS, etc.

**Key Methods**:

##### `fetch_market_snapshot()`
**Effect**: Fetches live data for all NIFTY 50 stocks
- Uses threading for parallel downloads
- Caches for 60 seconds (TTL)
- Returns: symbol, price, change%, volume, trend, history

##### `get_stock_analysis(symbol)`
**Effect**: Deep dive analysis for single stock
- Calculates SMA-5 and SMA-20
- Determines trend (UPTREND/DOWNTREND/SIDEWAYS)
- Analyzes volume patterns
- Provides future outlook prediction
- Detects corrections from monthly high

##### `check_portfolio_health(portfolio)`
**Effect**: Monitors portfolio for stop-loss breaches
- Compares current price vs entry price
- Triggers alerts when loss exceeds threshold
- Used for "Disruption Mode" feature

---

#### [bloomberg_engine.py](file:///Users/aayush/Finance-X-/bloomberg_engine.py)
**Role**: Professional Bloomberg-style market features

**Key Class**: `BloombergEngine`

**Node Effects**:
```mermaid
graph TB
    A[Bloomberg Engine] --> B[FX Rates]
    A --> C[Sector Performance]
    A --> D[Economic Calendar]
    A --> E[Stock Screener]
    A --> F[Top Movers]
    
    B -->|8 pairs| G[USD/INR, EUR/USD, BTC/USD, etc.]
    C -->|10 sectors| H[XLK, XLF, XLE, etc.]
    D -->|Events| I[Fed Decisions, CPI, GDP]
    E -->|Criteria| J[GAINERS/LOSERS/VOLUME/VOLATILE]
    F -->|Top 5| K[Gainers + Losers]
    
    style A fill:#00BCD4
```

**Features**:

##### FX Rates (`get_fx_rates()`)
**Tracked Pairs**:
- USD/INR, EUR/USD, GBP/USD, USD/JPY
- EUR/INR, GBP/INR
- BTC/USD, ETH/USD

**Cache**: 30 seconds
**Effect**: Provides live currency exchange rates

##### Sector Performance (`get_sector_performance()`)
**Tracked Sectors** (US ETFs):
- Technology (XLK)
- Financials (XLF)
- Energy (XLE)
- Healthcare (XLV)
- Industrials (XLI)
- Consumer (XLY)
- Utilities (XLU)
- Real Estate (XLRE)
- Materials (XLB)
- Communications (XLC)

**Cache**: 60 seconds
**Effect**: Shows sector rotation and market leadership

##### Stock Screener (`screen_stocks()`)
**Criteria**:
- GAINERS - Top 10 by % gain
- LOSERS - Top 10 by % loss
- VOLUME - Top 10 by trading volume
- VOLATILE - Top 10 by intraday range

**Effect**: Filters market data based on user criteria

##### Economic Calendar (`get_economic_calendar()`)
**Events Tracked**:
- Fed Interest Rate Decisions (HIGH impact)
- CPI Inflation Data (HIGH impact)
- GDP Growth Rate (HIGH impact)
- RBI Policy Meetings (HIGH impact)
- Jobless Claims (MEDIUM impact)
- Consumer Sentiment (MEDIUM impact)

**Effect**: Provides upcoming economic events calendar

---

#### [study_engine.py](file:///Users/aayush/Finance-X-/study_engine.py)
**Role**: Financial news and educational resources

**Key Class**: `StudyEngine`

**Node Effects**:
```mermaid
graph LR
    A[RSS Feeds] -->|fetch| B[StudyEngine]
    C[Resource Library] --> B
    D[Glossary DB] --> B
    
    B -->|analyze| E[Sentiment Analysis]
    B -->|extract| F[Ticker Mentions]
    B -->|categorize| G[Impact Level]
    
    E --> H[News Feed]
    F --> H
    G --> H
    
    H --> I[server.py STUDY command]
    
    style B fill:#8BC34A
```

**News Sources**:
- Yahoo Finance RSS
- MarketWatch RSS
- Reuters Business RSS
- Bloomberg Markets RSS

**Key Methods**:

##### `fetch_live_news()`
**Effect**: Fetches and analyzes news from multiple RSS feeds
- Sentiment analysis (BULLISH/BEARISH/NEUTRAL)
- Impact estimation (HIGH/MEDIUM/LOW)
- Ticker extraction from headlines

##### `get_study_resources(category)`
**Categories**:
- Technical Analysis
- Fundamental Analysis
- Options Trading
- Risk Management
- Market Psychology

**Effect**: Provides curated learning resources

##### `get_glossary(term)`
**Terms Covered**:
- Bull Market, Bear Market
- Volatility, Liquidity
- Stop Loss, Margin Call
- Beta, Alpha, Sharpe Ratio
- And 50+ more terms

**Effect**: Educational reference for market terminology

---

#### [performance_engine.py](file:///Users/aayush/Finance-X-/performance_engine.py)
**Role**: Hardware optimization and vectorized calculations

**Key Classes**:

##### `HardwareNavigator`
**Purpose**: System resource monitoring

**Node Effects**:
```mermaid
graph TB
    A[System Metrics] --> B[HardwareNavigator]
    B --> C{CPU Load}
    
    C -->|< 30%| D[ULTRA Mode]
    C -->|30-70%| E[HIGH Mode]
    C -->|> 70%| F[EFFICIENT Mode]
    
    D --> G[Max Simulation Depth]
    E --> H[Balanced Performance]
    F --> I[Throttled Mode]
    
    style B fill:#FF5722
```

**Methods**:
- `get_system_metrics()` - CPU%, memory%, core count
- `determine_fidelity_level()` - Adaptive performance mode

##### `PerformanceEngine`
**Purpose**: Vectorized mathematical operations using NumPy

**Methods**:

###### `calculate_bollinger_bands_vectorized()`
**Effect**: ~50x faster than loop-based calculation
- Uses Pandas rolling window
- Vectorized operations via NumPy
- Fills NaN values automatically

###### `batch_update_prices()`
**Effect**: Updates all ticker prices simultaneously
- Vectorized random shock generation
- System risk-based volatility multiplier
- Correlation matrix support (advanced)

###### `calculate_decay_batch()`
**Effect**: Vectorized event weight decay
- Exponential decay formula
- Processes all events at once
- Time-based weight reduction

**Performance Impact**:
- Bollinger Bands: 50x faster
- Price Updates: 100x faster for 50+ tickers
- Decay Calculation: 80x faster for 100+ events

---

### 🔧 Support Modules

#### [analyst.py](file:///Users/aayush/Finance-X-/analyst.py)
**Role**: Event analysis and explanation

**Key Class**: `Analyst`

**Method**: `explain_event(event)`
**Effect**: Generates human-readable analysis of market events
- Categorizes event type
- Explains impact level
- Provides context and implications

---

#### [models.py](file:///Users/aayush/Finance-X-/models.py)
**Role**: Data structure definitions

**Key Models**:

##### `MarketEvent`
```python
timestamp: datetime
event_type: str
description: str
base_impact: float
sector: str
```

##### `ProcessedEvent`
```python
original_event: MarketEvent
current_weight: float
```

##### `SystemState` (Enum)
```python
STABLE
VOLATILE
HIGH_VOL
CRASH
```

##### `MarketRegime` (Enum)
```python
LOW_VOL
MEDIUM_VOL
HIGH_VOL
CRISIS
```

##### `Ticker`
```python
symbol: str
name: str
current_price: float
change_pct: float
history: List[PricePoint]
```

**Effect**: Provides type safety and data structure consistency across all modules

---

#### [database.py](file:///Users/aayush/Finance-X-/database.py)
**Role**: SQLite database management

**Key Class**: `DatabaseManager`

**Tables**:
- `events` - Market events history
- `system_states` - System state snapshots
- `price_history` - Ticker price history

**Methods**:
- `initialize_db()` - Create tables
- `log_event()` - Store market event
- `log_state()` - Store system state
- `get_recent_events()` - Query events

**Effect**: Persistent storage for historical analysis and audit trails

---

#### [user_data.py](file:///Users/aayush/Finance-X-/user_data.py)
**Role**: User portfolio management

**Key Class**: `UserManager`

**Database**: `users.db`

**Tables**:
- `positions` - User stock positions

**Methods**:
- `add_position(symbol, price, qty)` - Add stock position
- `get_portfolio()` - Retrieve all positions
- `remove_position(id)` - Delete position

**Effect**: Enables portfolio tracking and disruption monitoring

---

### 🎨 Frontend Layer

#### [static/index.html](file:///Users/aayush/Finance-X-/static/index.html)
**Role**: Main terminal UI interface

**Structure**:
- Terminal header with system status
- Command input area
- Output display panel
- Responsive grid layouts

**Effect**: Provides Bloomberg-style terminal interface

---

#### [static/terminal.js](file:///Users/aayush/Finance-X-/static/terminal.js)
**Role**: Terminal logic and rendering

**Key Functions**:
- `sendCommand()` - Send command to server
- `renderResponse()` - Render different response types
- `updateStatus()` - Update system status display
- `renderChart()` - Chart visualization
- `renderGrid()` - Market grid display

**Response Types Handled**:
- TABLE - Tabular data
- CHART_FULL - Price charts
- OVERVIEW_GRID - Market overview
- FX_VIEW - FX rates display
- SECTORS_VIEW - Sector heatmap
- NEWS_FEED - News articles
- STUDY_VIEW - Learning resources

**Effect**: Dynamic UI rendering based on server responses

---

#### [static/terminal.css](file:///Users/aayush/Finance-X-/static/terminal.css)
**Role**: Terminal styling

**Design Features**:
- Dark theme (Bloomberg-style)
- Monospace fonts
- Color-coded data (green/red for gains/losses)
- Responsive layouts
- Glassmorphism effects

**Effect**: Professional, modern terminal aesthetic

---

## Docker Deployment

### Container Architecture

```mermaid
graph TB
    subgraph "Docker Network"
        A[finance-x-app<br/>Port 8000]
        B[bloomberg-engine<br/>Port 8001]
    end
    
    C[finance.db] -.->|Volume Mount| A
    D[users.db] -.->|Volume Mount| A
    
    E[Host Port 8000] --> A
    F[Host Port 8001] --> B
    
    A -.->|Can call| B
    
    style A fill:#4CAF50
    style B fill:#FF9800
```

### Main Application Container

#### [Dockerfile](file:///Users/aayush/Finance-X-/Dockerfile)
**Base Image**: `python:3.11-slim`

**Build Steps**:
1. Install system dependencies (gcc, g++)
2. Copy requirements.txt
3. Install Python dependencies
4. Copy application files
5. Create directories
6. Set environment variables
7. Configure health check

**Exposed Port**: 8000

**Entry Point**: `uvicorn server:app --host 0.0.0.0 --port 8000`

**Effect**: Containerizes main Finance-X application

---

#### [docker-compose.yml](file:///Users/aayush/Finance-X-/docker-compose.yml)
**Services**: `finance-x`

**Configuration**:
- Port mapping: 8000:8000
- Volume mounts: finance.db, users.db
- Health checks every 30s
- Auto-restart policy
- Bridge network

**Effect**: Orchestrates main application deployment

---

### Bloomberg Microservice Container

#### [Dockerfile.bloomberg](file:///Users/aayush/Finance-X-/Dockerfile.bloomberg)
**Base Image**: `python:3.11-slim`

**Dependencies** (minimal):
- fastapi
- uvicorn
- yfinance
- pandas
- numpy

**Exposed Port**: 8001

**Entry Point**: `uvicorn bloomberg_service:app --host 0.0.0.0 --port 8001`

**Effect**: Creates lightweight Bloomberg microservice container

---

#### [docker-compose.bloomberg.yml](file:///Users/aayush/Finance-X-/docker-compose.bloomberg.yml)
**Services**: `bloomberg-engine`

**Configuration**:
- Port mapping: 8001:8001
- Independent network
- Health checks
- Auto-restart

**Effect**: Enables independent Bloomberg service deployment

---

## System Integration Flow

### Complete Request-Response Cycle

```mermaid
sequenceDiagram
    participant User
    participant Browser
    participant Server
    participant Engine
    participant IndiaEngine
    participant BloombergEngine
    participant Database
    participant yfinance
    
    User->>Browser: Type "NIFTY"
    Browser->>Server: POST /command {"command": "NIFTY"}
    Server->>IndiaEngine: fetch_market_snapshot()
    
    IndiaEngine->>IndiaEngine: Check cache (60s TTL)
    
    alt Cache Miss
        IndiaEngine->>yfinance: download(NIFTY_50_symbols)
        yfinance-->>IndiaEngine: Raw market data
        IndiaEngine->>IndiaEngine: Process & calculate metrics
        IndiaEngine->>IndiaEngine: Update cache
    end
    
    IndiaEngine-->>Server: Market snapshot array
    Server-->>Browser: JSON response
    Browser->>Browser: Render grid view
    Browser-->>User: Display NIFTY 50 data
    
    User->>Browser: Type "EVAL RELIANCE"
    Browser->>Server: POST /command {"command": "EVAL RELIANCE"}
    Server->>IndiaEngine: get_stock_analysis("RELIANCE")
    IndiaEngine->>yfinance: Ticker("RELIANCE.NS").history()
    yfinance-->>IndiaEngine: 1-month historical data
    IndiaEngine->>IndiaEngine: Calculate SMA-5, SMA-20
    IndiaEngine->>IndiaEngine: Analyze trend & momentum
    IndiaEngine-->>Server: Analysis result
    Server-->>Browser: JSON response
    Browser->>Browser: Render analysis report
    Browser-->>User: Display stock evaluation
```

---

## Performance Optimizations

### 1. Caching Strategy

```mermaid
graph TB
    A[Request] --> B{Cache Check}
    B -->|Hit| C[Return Cached Data]
    B -->|Miss| D[Fetch from API]
    D --> E[Process Data]
    E --> F[Update Cache]
    F --> G[Return Fresh Data]
    
    C --> H[Response]
    G --> H
    
    style B fill:#FFC107
    style F fill:#4CAF50
```

**Cache TTLs**:
- India Market: 60 seconds
- FX Rates: 30 seconds
- Sector Data: 60 seconds
- News Feed: 300 seconds

**Effect**: Reduces API calls by ~90%, improves response time

---

### 2. Vectorized Operations

**Before** (Loop-based):
```python
for i, price in enumerate(prices):
    sma = sum(prices[i-20:i]) / 20
    std = calculate_std(prices[i-20:i])
    upper[i] = sma + 2 * std
```

**After** (Vectorized):
```python
sma = pd.Series(prices).rolling(20).mean()
std = pd.Series(prices).rolling(20).std()
upper = sma + 2 * std
```

**Performance Gain**: 50x faster for 1000+ data points

---

### 3. Parallel Data Fetching

```python
# Fetches all 49 NIFTY stocks in parallel
data = yf.download(
    NIFTY_SYMBOLS,
    period="5d",
    threads=True  # Parallel downloads
)
```

**Effect**: Reduces fetch time from ~50s to ~5s

---

## Key Workflows

### Workflow 1: Adding New Market Feature

```mermaid
graph TB
    A[Define Feature] --> B[Create Engine Method]
    B --> C[Add Server Route]
    C --> D[Update Frontend Renderer]
    D --> E[Add Command to Help Menu]
    E --> F[Test End-to-End]
    
    style A fill:#2196F3
    style F fill:#4CAF50
```

**Example**: Adding Crypto Tracker
1. **Engine**: Add `get_crypto_prices()` to `bloomberg_engine.py`
2. **Server**: Add `elif cmd == "CRYPTO":` route in `server.py`
3. **Frontend**: Add `CRYPTO_VIEW` renderer in `terminal.js`
4. **Help**: Update help menu with "CRYPTO" command

---

### Workflow 2: Database Schema Change

```mermaid
graph TB
    A[Modify models.py] --> B[Update database.py]
    B --> C[Create Migration Script]
    C --> D[Test Locally]
    D --> E[Update Docker Volume]
    E --> F[Deploy]
    
    style C fill:#FF9800
    style F fill:#4CAF50
```

---

### Workflow 3: Adding New Command

1. **Parse Command** in `server.py`:
```python
elif cmd == "NEWCMD":
    # Command logic
```

2. **Call Engine**:
```python
result = engine.new_feature()
```

3. **Return Response**:
```python
return {
    "type": "NEW_VIEW",
    "title": "Feature Title",
    "data": result
}
```

4. **Render in Frontend** (`terminal.js`):
```javascript
case 'NEW_VIEW':
    renderNewView(response.data);
    break;
```

---

## Deployment Scenarios

### Scenario 1: Local Development
```bash
# Run directly
python server.py

# Or with uvicorn
uvicorn server:app --reload --port 8000
```

### Scenario 2: Docker (Single Container)
```bash
docker-compose up -d
```

### Scenario 3: Microservices (Both Containers)
```bash
# Main app
docker-compose up -d

# Bloomberg service
docker-compose -f docker-compose.bloomberg.yml up -d
```

### Scenario 4: Production (Render.com)
Uses `render.yaml` configuration:
- Auto-deploy from Git
- Managed database
- SSL/HTTPS
- Health checks

---

## Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `HOST` | 0.0.0.0 | Server bind address |
| `PORT` | 8000 | Server port |
| `PYTHONUNBUFFERED` | 1 | Python output buffering |

---

## Security Features

### 1. Admin Authentication
```python
ADMIN_KEY = "FIN-X-" + secrets.token_hex(2).upper()
SESSION_TOKENS = set()
```

**Flow**:
1. User enters: `AUTH [KEY]`
2. Server validates key
3. Returns session token
4. Token required for SQL commands

### 2. SQL Injection Protection
- Uses parameterized queries
- Admin-only access
- Limited to 20 rows output

---

## Monitoring & Diagnostics

### System Metrics Endpoint
```
GET /system/diagnostics
```

**Returns**:
```json
{
  "cpu_percent": 45.2,
  "cores": 8,
  "memory_percent": 62.1,
  "acceleration_mode": "AVX2_VECTORIZED"
}
```

### Health Checks
- **Main App**: `GET /status`
- **Bloomberg Service**: `GET /health`

---

## Future Enhancements

### Planned Features
1. **WebSocket Support** - Real-time price streaming
2. **Redis Caching** - Distributed cache layer
3. **PostgreSQL Migration** - Scalable database
4. **Machine Learning** - Predictive models
5. **Mobile App** - React Native client

### Architecture Evolution
```mermaid
graph TB
    subgraph "Current"
        A[Monolith + 1 Microservice]
    end
    
    subgraph "Future"
        B[API Gateway]
        C[Market Data Service]
        D[Analysis Service]
        E[Bloomberg Service]
        F[ML Service]
        G[WebSocket Service]
    end
    
    A -.->|Refactor| B
    B --> C
    B --> D
    B --> E
    B --> F
    B --> G
    
    style A fill:#FFC107
    style B fill:#4CAF50
```

---

## Troubleshooting Guide

### Issue: Market Data Not Loading
**Symptoms**: Empty arrays, no prices
**Causes**:
- yfinance API rate limit
- Network connectivity
- Market closed

**Solutions**:
1. Check yfinance status
2. Increase cache TTL
3. Add retry logic

### Issue: High Memory Usage
**Symptoms**: Container OOM, slow performance
**Causes**:
- Large price history arrays
- No cache eviction
- Memory leaks

**Solutions**:
1. Limit history length
2. Implement LRU cache
3. Profile with memory_profiler

### Issue: Slow Response Times
**Symptoms**: Commands take >5s
**Causes**:
- Cache miss
- Synchronous API calls
- Large data processing

**Solutions**:
1. Warm up cache on startup
2. Use async/await
3. Implement pagination

---

## Conclusion

Finance-X is a **modular, scalable financial intelligence platform** with:
- ✅ Real-time market data integration
- ✅ Professional Bloomberg-style features
- ✅ AI-powered risk detection
- ✅ Microservices architecture
- ✅ Docker containerization
- ✅ Performance optimization
- ✅ Educational resources

The architecture supports both **monolithic deployment** (simple) and **microservices deployment** (scalable), making it suitable for development, testing, and production environments.
