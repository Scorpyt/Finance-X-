# Finance-X

**Professional Trading Terminal with AI-Powered Analysis**

A sophisticated financial trading terminal featuring real-time market data, intelligent analysis engines, and enterprise-grade security. Built for Indian and global markets with Bloomberg-style features.

---

## ✨ Features

### 📊 Market Analysis
- **Real-time NIFTY 50** - Live Indian stock market data with yfinance
- **Bloomberg-Style Features** - FX rates, sector analysis, stock screener, top movers
- **AI-Powered Insights** - 3-point stock evaluation (trend, factors, outlook)
- **Disruption Mode** - Portfolio loss alerts and risk monitoring

### 🧠 Intelligence Engines
- `engine.py` - Core AI analysis engine
- `india_engine.py` - NSE/Indian market specialist
- `bloomberg_engine.py` - Professional trading features
- `study_engine.py` - News analysis and learning

### 🛡️ Enterprise Security
- **Cloudflare-style Zero Trust** authentication
- **Hourly rotating security codes**
- **Real-time access logging**
- **Strict allowlist enforcement**

### 🏗️ JARVIS Architecture Visualizer
Interactive React-based system architecture viewer with:
- Draggable node diagram
- **Virtual IDE Simulation** - Click wires to simulate connection changes
- Real-time security dashboard
- Module explorer with VS Code integration
- **Workflow Laboratory** - Simulate and analyze system workflows with impact reports

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- PostgreSQL (or Neon for cloud)

### Installation

```bash
# Clone the repository
git clone https://github.com/Scorpyt/Finance-X-.git
cd Finance-X-

# Install Python dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your database connection string
```

### Running the Application

```bash
# Start the main server
python server.py

# In a separate terminal, start JARVIS Visualizer
cd jarvis
npm install
npm run dev
```

---

## 📁 Project Structure

```
Finance-X-/
├── server.py              # FastAPI main server
├── engine.py              # Core intelligence engine
├── india_engine.py        # Indian market analysis
├── bloomberg_engine.py    # Bloomberg-style features
├── study_engine.py        # News & learning engine
├── database.py            # PostgreSQL/SQLite manager
├── user_data.py           # Portfolio management
├── db_config.py           # Database configuration
│
├── jarvis/                # JARVIS Architecture Visualizer
│   ├── src/
│   │   ├── components/    # React components
│   │   └── data/          # Architecture data
│   └── auth-server.cjs    # Enterprise auth server
│
├── static/                # Terminal frontend
│   ├── index.html
│   └── terminal.js
│
└── config/                # Configuration files
```

---

## ⚙️ Configuration

Create a `.env` file in the root directory:

```env
# Database (PostgreSQL recommended for production)
DATABASE_URL=postgresql://user:pass@host:port/database

# Use SQLite for local development
USE_SQLITE=false
```

---

## 🔐 Security

This application implements multiple security layers:

- **Authentication**: Enterprise-grade email verification
- **Authorization**: Strict allowlist for authorized users
- **Session Management**: Time-limited sessions with automatic expiry
- **Logging**: All access attempts are logged and monitored

> ⚠️ **Important**: Never commit `.env` files or expose credentials in code.

---

## 📊 Supported Commands

| Command | Description |
|---------|-------------|
| `NIFTY` | View NIFTY 50 stocks |
| `FX` | Live forex rates |
| `SECTORS` | Sector performance |
| `MOVERS` | Top gainers/losers |
| `SCREEN` | Stock screener |
| `ADD <symbol> <price>` | Add to portfolio |
| `PORTFOLIO` | View holdings |
| `DISRUPTION` | Enable loss alerts |

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | Python, FastAPI |
| Database | PostgreSQL (Neon), SQLite |
| Frontend | HTML/JS, React (JARVIS) |
| Data | yfinance, RSS feeds |
| Auth | Custom Zero Trust |
| Deployment | Vercel, Docker |

---

## 📋 Release Notes

### v2.0.0 (January 2026)
**Major Release: JARVIS & Enterprise Security**

#### 🆕 New Features
- **JARVIS Architecture Visualizer**
  - Interactive system diagram with React Flow
  - Virtual IDE simulation for connection changes
  - Real-time security logs dashboard
  - Module explorer with VS Code integration
  - **Interactive Node Flows**: Visualization of data pipelines and dependencies for each module
  - **Workflow Laboratory**: Import, export, and simulate system workflows with AI impact analysis

- **Enterprise Security**
  - Cloudflare-style Zero Trust authentication
  - Hourly rotating security codes
  - Email notifications for authorized users
  - Access attempt logging

- **Database Upgrade**
  - Migrated from SQLite to PostgreSQL (Neon)
  - Connection pooling for 20K+ concurrent users
  - Automatic schema migration
  - Performance indexes

#### 🔧 Improvements
- Enhanced Bloomberg-style features
- Improved Disruption Mode alerts
- Better error handling
- Cleaner project structure

### v1.0.0 (December 2025)
**Initial Release**
- Core trading terminal
- Basic market analysis
- Portfolio tracking
- Indian market support

---

## 📄 License

This project is proprietary software. Unauthorized copying, modification, or distribution is prohibited.

---

## 👥 Contributing

This is a private project. For access requests, please contact the maintainers.

---

<p align="center">
  <b>Finance-X</b> - Professional Trading Terminal
</p>
