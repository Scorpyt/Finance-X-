# Finance-X Integration Guide

## Quick Start

### 1. Install Dependencies
All required dependencies are already in `requirements.txt`:
- pandas
- numpy
- yfinance
- fastapi
- uvicorn

### 2. Start the Server
```bash
cd /Users/aayush/Finance-X-
python server.py
```

### 3. Access Terminal
Open browser: `http://localhost:8000`

### 4. Try New Commands
```bash
VOL RELIANCE          # Volatility analysis
VOLSCAN               # High volatility scanner
HEATMAP SECTOR        # Sector heatmap
HEATMAP MARKET        # Market heatmap
CORR                  # Correlation matrix
HELP                  # See all commands
```

---

## Frontend Integration (Optional)

To enable the new view renderers, add to `static/index.html`:

```html
<!-- Before closing </body> tag -->
<script src="/terminal_extensions.js"></script>
```

Then add to `static/terminal.js` in the response handler switch statement:

```javascript
case 'VOLATILITY_VIEW':
    renderVolatilityView(response);
    break;
case 'VOLSCAN_VIEW':
    renderVolScanView(response);
    break;
case 'HEATMAP_VIEW':
    renderHeatmapView(response);
    break;
case 'CORRELATION_VIEW':
    renderCorrelationView(response);
    break;
```

---

## Command Reference

| Command | Description | Example |
|---------|-------------|---------|
| `VOL [SYMBOL]` | Volatility analysis for a stock | `VOL TCS` |
| `VOLSCAN` | Scan for high volatility stocks | `VOLSCAN` |
| `HEATMAP SECTOR` | Sector performance heatmap | `HEATMAP SECTOR` |
| `HEATMAP MARKET` | Market overview heatmap | `HEATMAP MARKET` |
| `HEATMAP VOLUME` | Volume-based heatmap | `HEATMAP VOLUME` |
| `CORR` | Correlation matrix | `CORR` |

---

## Files Created/Modified

**New Files**:
- `/Users/aayush/Finance-X-/volatility.py`
- `/Users/aayush/Finance-X-/heatmap.py`
- `/Users/aayush/Finance-X-/static/terminal_extensions.js`

**Modified Files**:
- `/Users/aayush/Finance-X-/server.py` (added imports and command handlers)

---

## Architecture

```
User Command
    ↓
server.py (routes command)
    ↓
volatility.py / heatmap.py (processes data)
    ↓
yfinance (fetches market data)
    ↓
JSON Response
    ↓
terminal_extensions.js (renders view)
    ↓
User Display
```

---

## Performance Notes

- **Caching**: Market data cached for 60 seconds
- **Limits**: VOLSCAN processes first 20 stocks
- **Speed**: Most commands respond in 2-5 seconds
- **Optimization**: Vectorized calculations using pandas/numpy

---

## Support

For issues or questions, refer to:
- [COMPLETE_ARCHITECTURE.md](file:///Users/aayush/Finance-X-/COMPLETE_ARCHITECTURE.md) - Full system documentation
- [walkthrough.md](file:///Users/aayush/.gemini/antigravity/brain/c4929537-4ceb-42b4-9cb3-5b7508daf827/walkthrough.md) - Detailed integration walkthrough
