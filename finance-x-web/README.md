# Finance-X Interactive Website

Interactive Node.js website with GSAP animations featuring Ordinary and Enterprise terminal modes.

## 🚀 Features

### Landing Page
- **Stunning GSAP Animations**: Particle effects, parallax scrolling, smooth transitions
- **Dual Mode Selection**: Choose between Ordinary and Enterprise modes
- **Modern Design**: Dark theme with gradient accents and glassmorphism

### Ordinary Mode
- Basic trading commands (NIFTY, CHART, QUOTE)
- Simplified interface for beginners
- Free tier features

### Enterprise Mode
- Full command set (VOL, VOLSCAN, HEATMAP, CORR, FX, SECTORS)
- Advanced analytics and visualizations
- Professional Bloomberg-style terminal
- Premium features unlocked

## 📦 Installation

```bash
cd finance-x-web
npm install
```

## 🏃 Running the Application

### 1. Start Python Backend (Required)
```bash
cd /Users/aayush/Finance-X-
python server.py
```
Backend runs on `http://localhost:8000`

### 2. Start Node.js Frontend
```bash
cd finance-x-web
npm start
```
Frontend runs on `http://localhost:3000`

### 3. Open Browser
Navigate to `http://localhost:3000`

## 📁 Project Structure

```
finance-x-web/
├── server.js                 # Express server with proxy
├── package.json              # Dependencies
├── public/
│   ├── index.html           # Landing page
│   ├── ordinary.html        # Ordinary mode terminal
│   ├── enterprise.html      # Enterprise mode terminal
│   ├── css/
│   │   └── styles.css       # All styles
│   └── js/
│       ├── animations.js    # GSAP animations
│       ├── ordinary-terminal.js
│       └── enterprise-terminal.js
```

## 🎨 Technologies Used

- **Backend**: Node.js, Express.js
- **Frontend**: HTML5, CSS3, JavaScript
- **Animations**: GSAP (GreenSock Animation Platform)
- **API**: Axios for backend communication
- **Fonts**: Inter, Roboto Mono

## 🔧 Configuration

### Ports
- Frontend: `3000` (configurable via `PORT` env variable)
- Backend: `8000` (Python FastAPI)

### Environment Variables
```bash
PORT=3000  # Frontend port (optional)
```

## 📊 Available Commands

### Ordinary Mode
- `NIFTY` - View NIFTY 50 stocks
- `CHART [SYMBOL]` - View price chart
- `QUOTE [SYMBOL]` - Get stock quote
- `HELP` - Show all commands

### Enterprise Mode (All Ordinary + Advanced)
- `VOL [SYMBOL]` - Volatility analysis
- `VOLSCAN` - High volatility scanner
- `HEATMAP [SECTOR/MARKET/VOLUME]` - Heatmap visualizations
- `CORR` - Correlation matrix
- `FX` - Foreign exchange rates
- `SECTORS` - Sector performance
- `CALENDAR` - Economic calendar

## 🎯 Usage Examples

### Ordinary Mode
```
> NIFTY
📈 NIFTY 50 MARKET SNAPSHOT
1. RELIANCE      ₹2,450.50 ▲ +1.25%
2. TCS           ₹3,456.80 ▼ -0.45%
...
```

### Enterprise Mode
```
> VOL RELIANCE
📊 VOLATILITY ANALYSIS: RELIANCE
Current Price: ₹2,450.50
Volatility Regime: MEDIUM_VOL
Metrics:
  rolling_vol_20d: 0.0234
  historical_vol_annual: 28.45%
  ...
```

## 🔒 Security

- CORS enabled for development
- Proxy pattern to hide backend URL
- No sensitive data in frontend

## 🚀 Deployment

### Production Build
```bash
npm start
```

### Docker (Optional)
```bash
docker build -t finance-x-web .
docker run -p 3000:3000 finance-x-web
```

## 🐛 Troubleshooting

### Backend Connection Failed
- Ensure Python server is running on port 8000
- Check `BACKEND_URL` in `server.js`

### GSAP Animations Not Working
- Check browser console for errors
- Ensure GSAP CDN is accessible

### Commands Not Working
- Verify Python backend is running
- Check network tab for API errors

## 📝 Development

### Adding New Commands
1. Add command handler in `server.py` (Python backend)
2. Update terminal logic in `ordinary-terminal.js` or `enterprise-terminal.js`
3. Add display function for response type

### Customizing Animations
Edit `public/js/animations.js` to modify GSAP timelines and effects.

## 📄 License

MIT License - Finance-X 2026

## 🤝 Support

For issues or questions, refer to the main Finance-X documentation.

---

**Enjoy your professional trading terminal! 🚀📊**
