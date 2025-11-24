# 🐳 Docker Deployment Guide

## Overview

This Docker setup provides containerized deployment for both the Dagster pipeline and FastAPI services, with shared data and model volumes.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                Docker Compose Network                │
│                                                       │
│  ┌─────────────────────┐    ┌───────────────────┐  │
│  │   Dagster Service   │    │   API Service     │  │
│  │   Port: 3000        │    │   Port: 8000      │  │
│  │   - Train models    │───▶│   - Serve API     │  │
│  │   - Process data    │    │   - Read models   │  │
│  └─────────────────────┘    └───────────────────┘  │
│           │                           │              │
│           ▼                           ▼              │
│  ┌──────────────────────────────────────────────┐  │
│  │          Shared Volumes                      │  │
│  │   - /data    (read/write for Dagster)       │  │
│  │   - /models  (read/write for Dagster)       │  │
│  │              (read-only for API)             │  │
│  └──────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

## Files

- **`Dockerfile.dagster`** - Dagster pipeline container
- **`Dockerfile.api`** - FastAPI service container
- **`docker-compose.yml`** - Orchestrates both services
- **`.dockerignore`** - Excludes unnecessary files from build
- **`docker-start.sh`** - Start all services
- **`docker-stop.sh`** - Stop all services
- **`docker-logs.sh`** - View container logs

## Prerequisites

### Install Docker

**macOS:**
```bash
brew install --cask docker
# Or download from https://www.docker.com/products/docker-desktop
```

**Linux:**
```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER
```

**Verify installation:**
```bash
docker --version
docker-compose --version
```

## Quick Start

### 1. Build and Start Services

```bash
cd /Users/zerfaouiabdallah/Spotify/spotify_pipeline
./docker-start.sh
```

This will:
- Build Docker images for Dagster and API
- Start both services in the background
- Mount data and models directories as volumes

### 2. Access Services

- **Dagster UI:** http://localhost:3000
- **FastAPI:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

### 3. Run the Pipeline

1. Open http://localhost:3000
2. Click "Materialize all" to train the model
3. Wait for all 6 assets to complete
4. Model will be saved to mounted `/models` volume

### 4. Test the API

Once the model is trained:

```bash
# Health check
curl http://localhost:8000/health

# Make a prediction
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "acousticness": 0.1,
    "danceability": 0.7,
    "duration_ms": 200000,
    "energy": 0.8,
    "explicit": 0,
    "instrumentalness": 0.0,
    "key": 5,
    "liveness": 0.1,
    "loudness": -5.0,
    "mode": 1,
    "speechiness": 0.05,
    "tempo": 120.0,
    "time_signature": 4,
    "valence": 0.6,
    "artist_song_count": 10,
    "genre": "pop"
  }'
```

## Manual Docker Commands

### Build Services
```bash
# Build all services
docker-compose build

# Build specific service
docker-compose build dagster
docker-compose build api
```

### Start Services
```bash
# Start in background
docker-compose up -d

# Start in foreground (see logs)
docker-compose up

# Start specific service
docker-compose up -d dagster
docker-compose up -d api
```

### Stop Services
```bash
# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Stop specific service
docker-compose stop dagster
docker-compose stop api
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f dagster
docker-compose logs -f api

# Last 100 lines
docker-compose logs --tail=100
```

### Container Management
```bash
# List running containers
docker-compose ps

# Restart services
docker-compose restart

# Restart specific service
docker-compose restart dagster
docker-compose restart api

# Execute command in container
docker-compose exec dagster bash
docker-compose exec api bash
```

## Volume Management

### Data Volumes

The following directories are mounted as volumes:

1. **`../data`** → `/app/data` (both containers)
   - Contains: CSV data, dagster outputs
   - Permissions: Read/write for Dagster, read-only for API

2. **`../models`** → `/app/models` (both containers)
   - Contains: Trained models, metadata, predictions
   - Permissions: Read/write for Dagster, read-only for API

3. **`dagster_home`** (Docker volume)
   - Contains: Dagster configuration and metadata
   - Persistent across container restarts

4. **`dagster_storage`** (Docker volume)
   - Contains: Dagster asset storage (pickles)
   - Persistent across container restarts

### Backup Volumes

```bash
# List volumes
docker volume ls

# Inspect volume
docker volume inspect spotify_pipeline_dagster_home

# Backup volume
docker run --rm -v spotify_pipeline_dagster_home:/data -v $(pwd):/backup \
  alpine tar czf /backup/dagster_home_backup.tar.gz /data

# Restore volume
docker run --rm -v spotify_pipeline_dagster_home:/data -v $(pwd):/backup \
  alpine tar xzf /backup/dagster_home_backup.tar.gz -C /
```

## Port Configuration

Default ports:
- **Dagster:** 3000
- **API:** 8000

To change ports, edit `docker-compose.yml`:

```yaml
services:
  dagster:
    ports:
      - "3001:3000"  # Host:Container
  
  api:
    ports:
      - "8001:8000"  # Host:Container
```

## Environment Variables

### Dagster Container
- `DAGSTER_HOME=/app/dagster_home` - Dagster home directory
- `PYTHONUNBUFFERED=1` - Enable Python logging
- `PYTHONPATH=/app/src:$PYTHONPATH` - Python module path

### API Container
- `PYTHONUNBUFFERED=1` - Enable Python logging
- `PYTHONPATH=/app/src:$PYTHONPATH` - Python module path

Add custom environment variables in `docker-compose.yml`:

```yaml
services:
  api:
    environment:
      - CUSTOM_VAR=value
```

## Health Checks

Both services have health checks configured:

**Dagster:**
- Endpoint: http://localhost:3000
- Interval: 30s
- Timeout: 10s
- Start period: 40s

**API:**
- Endpoint: http://localhost:8000/health
- Interval: 30s
- Timeout: 10s
- Start period: 20s

View health status:
```bash
docker-compose ps
```

## Troubleshooting

### Container won't start

**Check logs:**
```bash
docker-compose logs dagster
docker-compose logs api
```

**Rebuild images:**
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Port already in use

**Find process using port:**
```bash
# macOS/Linux
lsof -i :3000
lsof -i :8000

# Kill process
kill -9 <PID>
```

**Or change port in `docker-compose.yml`**

### Volume permission issues

**Fix permissions:**
```bash
sudo chown -R $USER:$USER ../data
sudo chown -R $USER:$USER ../models
```

### Container out of memory

**Increase Docker memory:**
- Docker Desktop → Settings → Resources → Memory
- Increase to at least 4GB

### Model not found in API

**Check if model exists:**
```bash
docker-compose exec api ls -lh /app/models/
```

**If missing, train model:**
1. Open http://localhost:3000
2. Click "Materialize all"
3. Wait for completion

### Cannot connect to services

**Check if containers are running:**
```bash
docker-compose ps
```

**Check network:**
```bash
docker network ls
docker network inspect spotify_pipeline_spotify-network
```

## Production Deployment

### Security Considerations

1. **Don't expose Dagster UI publicly** (port 3000)
   - Use reverse proxy with authentication
   - Or remove port mapping entirely

2. **API Security:**
   - Add API key authentication
   - Use HTTPS with reverse proxy (nginx/traefik)
   - Enable CORS only for trusted domains

3. **Environment Variables:**
   - Use `.env` file for secrets
   - Never commit sensitive data to git

### Example with nginx reverse proxy

```yaml
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - api
```

### Resource Limits

Add resource limits in `docker-compose.yml`:

```yaml
services:
  dagster:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
  
  api:
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
```

## Monitoring

### Container Stats
```bash
# Real-time stats
docker stats

# Specific containers
docker stats spotify_dagster spotify_api
```

### Health Status
```bash
# Check health
docker-compose ps

# Detailed inspect
docker inspect spotify_dagster | jq '.[0].State.Health'
docker inspect spotify_api | jq '.[0].State.Health'
```

## Cleanup

### Remove Everything
```bash
# Stop and remove containers, networks
docker-compose down

# Also remove volumes
docker-compose down -v

# Remove images
docker rmi spotify_pipeline_dagster
docker rmi spotify_pipeline_api
```

### Remove Unused Docker Resources
```bash
# Remove stopped containers
docker container prune

# Remove unused images
docker image prune

# Remove unused volumes
docker volume prune

# Remove everything unused
docker system prune -a
```

## Development Workflow

### Local Development
```bash
# Use local scripts
./start.sh        # Dagster
./start_api.sh    # API
```

### Container Development
```bash
# Mount source code for live reload
docker-compose -f docker-compose.dev.yml up
```

### Testing in Container
```bash
# Run tests in Dagster container
docker-compose exec dagster uv run pytest

# Test API endpoint
docker-compose exec api curl http://localhost:8000/health
```

## Summary

✅ **Two services:** Dagster (3000) and API (8000)  
✅ **Shared volumes:** Data and models persist between containers  
✅ **Health checks:** Automatic service monitoring  
✅ **Easy scripts:** One-command start/stop  
✅ **Production-ready:** Resource limits, logging, restarts  

**Quick Commands:**
```bash
./docker-start.sh    # Start everything
./docker-stop.sh     # Stop everything
./docker-logs.sh     # View logs
```

Access at:
- http://localhost:3000 (Dagster)
- http://localhost:8000 (API)
