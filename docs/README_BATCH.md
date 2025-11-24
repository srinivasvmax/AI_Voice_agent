# Batch Audio Processor

Process multiple audio files automatically with transcription, LLM responses, and TTS generation.

## Quick Start

### 1. Prepare your audio files

Create an `input` folder and add your audio files:
```
input/
  ├── recording1.wav
  ├── recording2.wav
  └── recording3.wav
```

Supported formats: `.wav`, `.mp3`, `.webm`, `.ogg`, `.m4a`, `.flac`

### 2. Start llama server

```bash
start_llama_server.bat
```

Keep this running in a separate terminal.

### 3. Run batch processor

```bash
start_batch_processor.bat
```

Or directly:
```bash
python batch_processor.py
```

### 4. Check results

Results are saved in the `output` folder:
```
output/
  ├── results.json          # Detailed JSON with all data
  ├── transcripts.txt       # All transcriptions
  ├── responses.txt         # All AI responses
  └── audio/
      ├── response_001.wav  # TTS audio for response 1
      ├── response_002.wav  # TTS audio for response 2
      └── response_003.wav  # TTS audio for response 3
```

---

## Example Output

### transcripts.txt
```
============================================================
TRANSCRIPTS
============================================================

[1] recording1.wav
Language: en
Transcript: What is artificial intelligence?
------------------------------------------------------------

[2] recording2.wav
Language: en
Transcript: How does machine learning work?
------------------------------------------------------------
```

### responses.txt
```
============================================================
AI RESPONSES
============================================================

[1] recording1.wav
Question: What is artificial intelligence?
Response: Artificial intelligence is the simulation of human intelligence...
------------------------------------------------------------

[2] recording2.wav
Question: How does machine learning work?
Response: Machine learning works by training algorithms on data...
------------------------------------------------------------
```

---

## Features

- ✅ **Automatic processing** - No manual intervention needed
- ✅ **Multilingual** - Supports English, Hindi, Telugu
- ✅ **Voice cloning** - TTS uses original speaker's voice
- ✅ **Detailed logs** - See progress for each file
- ✅ **Error handling** - Continues even if one file fails
- ✅ **Multiple formats** - Saves JSON, TXT, and audio outputs

---

## Use Cases

1. **Testing** - Test voice agent with multiple samples
2. **Bulk transcription** - Transcribe multiple recordings at once
3. **Interview processing** - Process recorded interviews
4. **Dataset creation** - Create training data with Q&A pairs
5. **Automated workflows** - Integrate into automation pipelines

---

## Configuration

Edit `batch_processor.py` to customize:

```python
# Change input/output folders
processor = BatchAudioProcessor(
    input_folder="my_recordings",
    output_folder="my_results"
)
```

---

## Troubleshooting

**No files found?**
- Check that audio files are in the `input` folder
- Verify file extensions are supported

**LLM timeout?**
- Ensure llama-server is running
- Check `services/llm_service_api.py` timeout settings

**Processing too slow?**
- Use a smaller LLM model
- Reduce number of files
- Process in smaller batches

---

## Performance

Processing time per file (approximate):
- Transcription: 2-5 seconds
- LLM response: 30-60 seconds (CPU) / 5-10 seconds (GPU)
- TTS generation: 3-5 seconds

**Total:** ~40-70 seconds per file on CPU

For 10 files: ~7-12 minutes
