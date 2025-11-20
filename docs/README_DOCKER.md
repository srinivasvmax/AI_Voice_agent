# Docker Setup for Voice Agent

## Prerequisites

1. **Install Docker Desktop**
   - Download from: https://www.docker.com/products/docker-desktop
   - Install and start Docker Desktop
   - Verify installation: `docker --version`

2. **Ensure model file exists**
   - File: `models/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf`
   - Should be ~4.5GB in size

---

## Quick Start (Recommended)

### Step 1: Navigate to docker folder
```bash
cd docker
```

### Step 2: Start all services
```bash
docker-compose up --build
```

This will:
- Download and start llama.cpp server (port 8080)
- Build and start voice agent web app (port 8000)
- Mount your models and code for live updates

### Step 3: Access the application
Open your browser: **http://localhost:8000**

### Step 4: Stop the services
Press `Ctrl+C` in the terminal, then:
```bash
docker-compose down
```

---

## Alternative: Run in Background

```bash
cd docker
docker-compose up -d --build
```

View logs:
```bash
docker-compose logs -f
```

Stop services:
```bash
docker-compose down
```

---

## Individual Services

### Run only Llama Server
```bash
docker run -p 8080:8080 -v "%CD%\models:/models" ghcr.io/ggerganov/llama.cpp:server --model /models/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf --ctx-size 2048 --port 8080 --host 0.0.0.0
```

### Run only Voice Agent (after llama server is running)
```bash
cd docker
docker build -t voice-agent -f Dockerfile ..
docker run -p 8000:8000 -v "%CD%\..\models:/app/models" voice-agent
```

---

## Troubleshooting

### Docker Desktop not running
```
Error: Cannot connect to the Docker daemon
```
**Solution:** Start Docker Desktop application

### Port already in use
```
Error: port is already allocated
```
**Solution:** Stop other services using ports 8000 or 8080, or change ports in `docker-compose.yml`

### Model not found
```
Error: failed to load model
```
**Solution:** Ensure `models/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf` exists in project root

### Out of memory
```
Error: failed to allocate memory
```
**Solution:** Increase Docker Desktop memory limit:
- Docker Desktop → Settings → Resources → Memory → Increase to 8GB+

---

## What's Running?

- **Llama Server**: http://localhost:8080 (LLM API)
- **Voice Agent Web**: http://localhost:8000 (Web interface)

Both services auto-restart if they crash.
