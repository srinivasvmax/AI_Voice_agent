# Voice Agent with Pipecat - Setup Guide

A multilingual voice agent using Pipecat framework with automatic speech detection, transcription, LLM responses, and text-to-speech.

## Features

- 🎤 Voice Activity Detection (VAD) - Auto-stops after silence
- 🌐 Multilingual support (English, Hindi, Telugu)
- 🤖 Local LLM via llama.cpp server
- 🔊 Voice cloning with Coqui TTS
- 🔄 Pipecat pipeline architecture

---

## Quick Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Download LLM Model

Place your GGUF model in the `models/` folder:
```
models/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf
```

### 3. Start llama.cpp Server

Download llama.cpp from: https://github.com/ggerganov/llama.cpp/releases

Run the server:
```bash
llama-server.exe -m models\Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf -c 2048 --port 8080
```

Or use the provided batch file:
```bash
start_llama_server.bat
```

### 4. Run Voice Agent

**Desktop Version (Terminal):**
```bash
python voice_agent.py
```

**Web Interface (Browser):**
```bash
python web_app.py
# Then open: http://localhost:8000
```

---

## How It Works

1. **Recording**: Starts automatically, stops after 5 seconds of silence
2. **Transcription**: Whisper detects language and transcribes speech
3. **LLM Response**: Generates contextual response via local LLM
4. **Speech Output**: Speaks response using voice cloning

---

## Configuration

Edit `voice_agent.py` to adjust:

```python
# Silence detection timeout
agent = VoiceAgentPipecat(silence_duration=5.0)

# VAD sensitivity (in services/vad_service.py)
VADService(threshold=0.3)  # Lower = more sensitive
```

---

## Troubleshooting

**No audio detected?**
- Check microphone permissions
- Adjust VAD threshold in `services/vad_service.py`

**LLM not responding?**
- Ensure llama-server is running on port 8080
- Check `services/llm_service_api.py` for correct endpoint

**TTS issues?**
- First run downloads Coqui TTS models (~1GB)
- Check internet connection for initial setup

---

## Project Structure

```
├── voice_agent.py                # Desktop voice agent with Pipecat
├── web_app.py                    # Web interface with Pipecat
├── services/
│   ├── llm_service_api.py        # LLM via llama.cpp API
│   ├── whisper_service.py        # Speech-to-text
│   ├── tts_service.py            # Text-to-speech
│   └── vad_service.py            # Voice activity detection
├── models/                        # LLM models folder
└── requirements.txt              # Python dependencies
```
