# Finance-X Docker Setup

This directory contains Docker configuration for the Finance-X application.

## Quick Start

### Using Docker Compose (Recommended)
```bash
# Build and start the container
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the container
docker-compose down
```

### Using Docker directly
```bash
# Build the image
docker build -t finance-x .

# Run the container
docker run -d -p 8000:8000 --name finance-x-app finance-x

# View logs
docker logs -f finance-x-app

# Stop the container
docker stop finance-x-app
docker rm finance-x-app
```

## Access the Application

Once running, access the application at:
- **Web Interface**: http://localhost:8000
- **API Status**: http://localhost:8000/status
- **API Docs**: http://localhost:8000/docs

## Admin Access

When the container starts, check the logs for the admin access key:
```bash
docker-compose logs | grep "ADMIN ACCESS KEY"
```

## Database Persistence

The databases (`finance.db` and `users.db`) are mounted as volumes, so your data persists across container restarts.

## Environment Variables

You can customize the application by setting environment variables in `docker-compose.yml`:
- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)

## Troubleshooting

### Container won't start
```bash
# Check logs
docker-compose logs

# Rebuild the image
docker-compose build --no-cache
docker-compose up -d
```

### Port already in use
Change the port mapping in `docker-compose.yml`:
```yaml
ports:
  - "8080:8000"  # Use port 8080 instead
```
