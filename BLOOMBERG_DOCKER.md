# Bloomberg Engine Docker Container

Standalone Docker container for the Bloomberg Engine microservice.

## Overview

The Bloomberg Engine provides professional market data features including:
- **FX Rates**: Live foreign exchange rates for major currency pairs
- **Top Movers**: Top 5 gainers and losers
- **Stock Screener**: Filter stocks by various criteria
- **Sector Performance**: US sector ETF performance data
- **Economic Calendar**: Upcoming economic events
- **Market Summary**: Overall market statistics and sentiment

## Quick Start

### Using Docker Compose (Recommended)

```bash
# Build and start the container
docker-compose -f docker-compose.bloomberg.yml up -d

# View logs
docker-compose -f docker-compose.bloomberg.yml logs -f

# Stop the container
docker-compose -f docker-compose.bloomberg.yml down
```

### Using Docker Directly

```bash
# Build the image
docker build -f Dockerfile.bloomberg -t bloomberg-engine .

# Run the container
docker run -d -p 8001:8001 --name bloomberg-engine bloomberg-engine

# View logs
docker logs -f bloomberg-engine

# Stop the container
docker stop bloomberg-engine
docker rm bloomberg-engine
```

## API Endpoints

Once running, the Bloomberg Engine API is available at `http://localhost:8001`

### Root Endpoint
```bash
curl http://localhost:8001/
```

### Health Check
```bash
curl http://localhost:8001/health
```

### FX Rates
Get live foreign exchange rates:
```bash
curl http://localhost:8001/fx-rates
```

**Response Example:**
```json
{
  "success": true,
  "count": 8,
  "data": [
    {
      "pair": "USD/INR",
      "rate": 83.25,
      "change": 0.15,
      "change_pct": 0.18,
      "direction": "up"
    }
  ]
}
```

### Sector Performance
Get US sector ETF performance:
```bash
curl http://localhost:8001/sectors
```

**Response Example:**
```json
{
  "success": true,
  "count": 10,
  "data": [
    {
      "sector": "Technology",
      "symbol": "XLK",
      "price": 185.50,
      "change_pct": 1.25,
      "direction": "up"
    }
  ]
}
```

### Economic Calendar
Get upcoming economic events:
```bash
# Get events for next 10 days (default)
curl http://localhost:8001/economic-calendar

# Get events for next 7 days
curl "http://localhost:8001/economic-calendar?days_ahead=7"
```

**Response Example:**
```json
{
  "success": true,
  "days_ahead": 10,
  "count": 5,
  "data": [
    {
      "date": "2026-01-16",
      "time": "08:30",
      "event": "Initial Jobless Claims",
      "impact": "MEDIUM",
      "currency": "USD",
      "days_until": 0,
      "day_name": "Thursday",
      "formatted_date": "Jan 16"
    }
  ]
}
```

### Stock Screener
Screen stocks by criteria (requires market data):
```bash
# Available criteria: GAINERS, LOSERS, VOLUME, VOLATILE
curl "http://localhost:8001/screen?criteria=GAINERS"
```

### Top Movers
Get top gainers and losers (requires market data):
```bash
curl http://localhost:8001/top-movers
```

### Market Summary
Get market summary statistics (requires market data):
```bash
curl http://localhost:8001/market-summary
```

## API Documentation

Interactive API documentation is available at:
- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc

## Configuration

### Port Configuration
To change the port, modify `docker-compose.bloomberg.yml`:
```yaml
ports:
  - "8002:8001"  # Use port 8002 instead
```

### Environment Variables
- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8001)
- `PYTHONUNBUFFERED`: Python output buffering (default: 1)

## Integration with Main Application

The Bloomberg Engine can be used as a standalone microservice or integrated with the main Finance-X application:

```python
import requests

# Call Bloomberg Engine API
response = requests.get("http://localhost:8001/fx-rates")
fx_data = response.json()
```

## Troubleshooting

### Container won't start
```bash
# Check logs
docker-compose -f docker-compose.bloomberg.yml logs

# Rebuild the image
docker-compose -f docker-compose.bloomberg.yml build --no-cache
docker-compose -f docker-compose.bloomberg.yml up -d
```

### Port already in use
```bash
# Check what's using port 8001
lsof -i :8001

# Change port in docker-compose.bloomberg.yml
```

### Health check failing
```bash
# Check if service is responding
curl http://localhost:8001/health

# View container logs
docker logs bloomberg-engine
```

## Performance Notes

- FX rates are cached for 30 seconds
- Sector data is cached for 60 seconds
- Market data endpoints require external data to be provided
- All data is fetched from yfinance in real-time (with caching)

## Development

To run the service locally without Docker:
```bash
# Install dependencies
pip install fastapi uvicorn yfinance pandas numpy requests

# Run the service
python bloomberg_service.py
```

## License

Part of the Finance-X application.
