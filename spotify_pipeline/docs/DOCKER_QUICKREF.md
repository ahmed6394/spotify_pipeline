# 🐳 Docker Quick Reference

## 🚀 Quick Start

```bash
cd /Users/zerfaouiabdallah/Spotify/spotify_pipeline

# Start everything
./docker-start.sh

# Test services
./docker-test.sh

# View logs
./docker-logs.sh

# Stop everything
./docker-stop.sh
```

## 📡 Service URLs

| Service | URL | Description |
|---------|-----|-------------|
| Dagster UI | http://localhost:3000 | Train models, view pipeline |
| API | http://localhost:8000 | Prediction endpoint |
| API Docs | http://localhost:8000/docs | Interactive API documentation |

## 🛠️ Common Commands

### Container Management
```bash
# Status
docker-compose ps

# Start
docker-compose up -d

# Stop
docker-compose down

# Restart
docker-compose restart

# Rebuild
docker-compose build --no-cache
```

### Logs
```bash
# All logs
docker-compose logs -f

# Specific service
docker-compose logs -f dagster
docker-compose logs -f api

# Last 50 lines
docker-compose logs --tail=50
```

### Execute Commands
```bash
# Shell access
docker-compose exec dagster bash
docker-compose exec api bash

# Check model
docker-compose exec api ls -lh /app/models/

# Run Python command
docker-compose exec api python -c "from api import model; print(model)"
```

### Volume Management
```bash
# List volumes
docker volume ls

# Remove volumes
docker-compose down -v

# Backup volume
docker run --rm -v spotify_pipeline_dagster_home:/data -v $(pwd):/backup \
  alpine tar czf /backup/dagster_backup.tar.gz /data
```

## 🔧 Troubleshooting

### Service won't start
```bash
# Check logs
docker-compose logs dagster
docker-compose logs api

# Rebuild from scratch
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

### Port conflict
```bash
# Find process using port
lsof -i :3000
lsof -i :8000

# Kill process
kill -9 <PID>
```

### Model not found
1. Open http://localhost:3000
2. Click "Materialize all"
3. Wait for all 6 assets to complete
4. Check: `docker-compose exec api ls -lh /app/models/`

### Container out of memory
- Docker Desktop → Preferences → Resources
- Increase memory to at least 4GB

## 📊 Monitoring

```bash
# Container stats
docker stats

# Health check
docker-compose ps

# Detailed health
docker inspect spotify_dagster | jq '.[0].State.Health'
docker inspect spotify_api | jq '.[0].State.Health'
```

## 🧹 Cleanup

```bash
# Stop containers
docker-compose down

# Remove everything (including volumes)
docker-compose down -v

# Remove images
docker rmi spotify_pipeline_dagster spotify_pipeline_api

# Clean all unused Docker resources
docker system prune -a
```

## 🎯 Workflow

### 1. Start Services
```bash
./docker-start.sh
```

### 2. Train Model
- Open http://localhost:3000
- Click "Materialize all"
- Wait for completion (green checkmarks)

### 3. Test API
```bash
# Health check
curl http://localhost:8000/health

# Make prediction
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"acousticness": 0.1, "danceability": 0.7, ...}'

# Or use Swagger UI
open http://localhost:8000/docs
```

### 4. Stop Services
```bash
./docker-stop.sh
```

## 📂 File Structure

```
spotify_pipeline/
├── Dockerfile.dagster       # Dagster container
├── Dockerfile.api           # API container
├── docker-compose.yml       # Orchestration
├── .dockerignore           # Build exclusions
├── docker-start.sh         # Start script
├── docker-stop.sh          # Stop script
├── docker-logs.sh          # Logs script
├── docker-test.sh          # Test script
└── DOCKER_GUIDE.md         # Full documentation
```

## 🔗 Volumes

| Volume | Path in Container | Purpose |
|--------|------------------|---------|
| `../data` | `/app/data` | CSV data, pipeline outputs |
| `../models` | `/app/models` | Trained models |
| `dagster_home` | `/app/dagster_home` | Dagster config |
| `dagster_storage` | `/app/data/dagster_storage` | Asset storage |

## 💡 Tips

- **First time setup:** Models need to be trained via Dagster before API can serve predictions
- **Data persistence:** Data and models persist across container restarts via volumes
- **Logs:** Use `./docker-logs.sh` to debug issues
- **Health checks:** Services have automatic health monitoring
- **Resource limits:** Adjust in `docker-compose.yml` if needed

## 🆘 Getting Help

```bash
# Container status
docker-compose ps

# Full logs
./docker-logs.sh

# Test services
./docker-test.sh

# Read full docs
cat DOCKER_GUIDE.md
```
