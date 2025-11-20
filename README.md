# Voice Agent with Pipecat

A multilingual AI voice agent built with Pipecat framework, featuring automatic speech detection, local LLM processing, and voice cloning.

## Quick Start

### Option 1: Desktop Voice Agent

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start LLM server
start_llama_server.bat

# 3. Run voice agent
python voice_agent.py
```

### Option 2: Web Interface

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start LLM server
start_llama_server.bat

# 3. Run web server
python web_app.py

# 4. Open browser
# Visit: http://localhost:8000
```

## Features

- 🎙️ **Voice Activity Detection** - Automatically stops recording after silence
- 🌍 **Multilingual** - Supports English, Hindi, Telugu
- 🤖 **Local LLM** - Runs Meta-Llama-3.1-8B locally via llama.cpp
- 🔊 **Voice Cloning** - Mimics your voice using Coqui TTS
- ⚡ **Pipecat Pipeline** - Modular processing architecture
- 🌐 **Web Interface** - Beautiful browser-based UI with real-time audio processing

## Documentation

- [Setup Guide](docs/README_SETUP.md) - Detailed installation and configuration
- [Docker Guide](docs/README_DOCKER.md) - Containerized deployment (if available)

## Requirements

- Python 3.11+
- Microphone access
- ~8GB RAM for LLM
- Internet connection (first run only, for model downloads)

## License

MIT
