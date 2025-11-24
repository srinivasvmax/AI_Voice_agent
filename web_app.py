from fastapi import FastAPI, File, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, FileResponse
import uvicorn
import soundfile as sf
import asyncio
from pathlib import Path
from services.llm_service_api import LLMService
from services.whisper_service import WhisperService
from services.tts_service import TTSService

app = FastAPI(title="Voice Agent Web")

# Initialize services
llm_service = LLMService()
whisper_service = WhisperService()
tts_service = TTSService()

@app.get("/", response_class=HTMLResponse)
async def home():
    """Serve the web UI"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Voice Agent</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
            }
            
            .container {
                background: white;
                padding: 40px;
                border-radius: 20px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                max-width: 600px;
                width: 100%;
            }
            
            h1 {
                color: #333;
                text-align: center;
                margin-bottom: 10px;
                font-size: 2em;
            }
            
            .subtitle {
                text-align: center;
                color: #666;
                margin-bottom: 30px;
                font-size: 0.9em;
            }
            
            .controls {
                text-align: center;
                margin: 30px 0;
            }
            
            button {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                padding: 18px 40px;
                font-size: 18px;
                border-radius: 50px;
                cursor: pointer;
                transition: all 0.3s ease;
                box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
                font-weight: 600;
            }
            
            button:hover:not(:disabled) {
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
            }
            
            button:active:not(:disabled) {
                transform: translateY(0);
            }
            
            button:disabled {
                background: #ccc;
                cursor: not-allowed;
                box-shadow: none;
            }
            
            .recording {
                background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%) !important;
                animation: pulse 1.5s ease-in-out infinite;
            }
            
            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.7; }
            }
            
            .status, .response {
                padding: 20px;
                margin: 20px 0;
                border-radius: 12px;
                display: none;
                animation: slideIn 0.3s ease;
            }
            
            @keyframes slideIn {
                from {
                    opacity: 0;
                    transform: translateY(-10px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
            
            .status {
                background: linear-gradient(135deg, #e0f7fa 0%, #b2ebf2 100%);
                color: #006064;
                border-left: 4px solid #00acc1;
            }
            
            .response {
                background: linear-gradient(135deg, #f1f8e9 0%, #dcedc8 100%);
                color: #33691e;
                border-left: 4px solid #689f38;
            }
            
            .transcript {
                background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
                color: #e65100;
                border-left: 4px solid #ff9800;
                padding: 20px;
                margin: 20px 0;
                border-radius: 12px;
                display: none;
                animation: slideIn 0.3s ease;
            }
            
            audio {
                width: 100%;
                margin-top: 20px;
                border-radius: 50px;
                display: none;
            }
            
            .icon {
                font-size: 1.2em;
                margin-right: 8px;
            }
            
            .loading {
                display: inline-block;
                width: 20px;
                height: 20px;
                border: 3px solid rgba(255,255,255,.3);
                border-radius: 50%;
                border-top-color: white;
                animation: spin 1s ease-in-out infinite;
                margin-left: 10px;
                vertical-align: middle;
            }
            
            @keyframes spin {
                to { transform: rotate(360deg); }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎙️ Voice Agent</h1>
            <p class="subtitle">Powered by Pipecat Framework</p>
            
            <div class="controls">
                <button id="recordBtn" onclick="toggleRecording()">
                    <span class="icon">🎤</span> Start Recording
                </button>
            </div>
            
            <div id="status" class="status"></div>
            <div id="transcript" class="transcript"></div>
            <div id="response" class="response"></div>
            <audio id="audioPlayer" controls></audio>
        </div>

        <script>
            let mediaRecorder;
            let audioChunks = [];
            let isRecording = false;

            async function toggleRecording() {
                const btn = document.getElementById('recordBtn');
                const status = document.getElementById('status');
                
                if (!isRecording) {
                    try {
                        const stream = await navigator.mediaDevices.getUserMedia({ 
                            audio: {
                                channelCount: 1,
                                sampleRate: 16000
                            } 
                        });
                        
                        mediaRecorder = new MediaRecorder(stream, {
                            mimeType: 'audio/webm'
                        });
                        
                        mediaRecorder.ondataavailable = (event) => {
                            if (event.data.size > 0) {
                                audioChunks.push(event.data);
                            }
                        };
                        
                        mediaRecorder.onstop = async () => {
                            const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                            audioChunks = [];
                            await processAudio(audioBlob);
                        };
                        
                        mediaRecorder.start();
                        isRecording = true;
                        btn.innerHTML = '<span class="icon">⏹️</span> Stop Recording';
                        btn.classList.add('recording');
                        status.style.display = 'block';
                        status.innerHTML = '<span class="icon">🎤</span> Recording... Click Stop when done';
                        
                        // Hide previous results
                        document.getElementById('transcript').style.display = 'none';
                        document.getElementById('response').style.display = 'none';
                        document.getElementById('audioPlayer').style.display = 'none';
                        
                    } catch (err) {
                        alert('❌ Microphone access denied: ' + err.message);
                        console.error(err);
                    }
                } else {
                    mediaRecorder.stop();
                    mediaRecorder.stream.getTracks().forEach(track => track.stop());
                    isRecording = false;
                    btn.innerHTML = '<span class="icon">🎤</span> Start Recording';
                    btn.classList.remove('recording');
                    btn.disabled = true;
                    status.innerHTML = '<span class="icon">⏳</span> Processing<span class="loading"></span>';
                }
            }

            async function processAudio(audioBlob) {
                const status = document.getElementById('status');
                const transcript = document.getElementById('transcript');
                const response = document.getElementById('response');
                const audioPlayer = document.getElementById('audioPlayer');
                const btn = document.getElementById('recordBtn');
                
                try {
                    const formData = new FormData();
                    formData.append('file', audioBlob, 'recording.webm');
                    
                    status.innerHTML = '<span class="icon">🔄</span> Transcribing via Pipecat pipeline<span class="loading"></span>';
                    
                    const res = await fetch('/process-audio', {
                        method: 'POST',
                        body: formData
                    });
                    
                    if (!res.ok) {
                        throw new Error('Server error: ' + res.statusText);
                    }
                    
                    const data = await res.json();
                    
                    if (data.error) {
                        throw new Error(data.error);
                    }
                    
                    // Show results
                    status.innerHTML = '<span class="icon">✅</span> Processing complete!';
                    
                    transcript.style.display = 'block';
                    transcript.innerHTML = `
                        <div><span class="icon">🌐</span> <strong>Language:</strong> ${data.language}</div>
                        <div style="margin-top: 10px;"><span class="icon">📝</span> <strong>You said:</strong> "${data.transcript}"</div>
                    `;
                    
                    response.style.display = 'block';
                    response.innerHTML = `<span class="icon">💬</span> <strong>Assistant:</strong> ${data.response}`;
                    
                    // Play audio response
                    if (data.audio_file) {
                        audioPlayer.src = '/audio/' + data.audio_file;
                        audioPlayer.style.display = 'block';
                        audioPlayer.play();
                    }
                    
                    btn.disabled = false;
                    
                } catch (err) {
                    status.style.display = 'block';
                    status.style.background = 'linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%)';
                    status.style.borderLeft = '4px solid #f44336';
                    status.style.color = '#c62828';
                    status.innerHTML = '<span class="icon">❌</span> Error: ' + err.message;
                    btn.disabled = false;
                    console.error(err);
                }
            }
        </script>
    </body>
    </html>
    """

@app.post("/process-audio")
async def process_audio(file: UploadFile = File(...)):
    """Process uploaded audio through Pipecat pipeline"""
    try:
        print(f"\n📥 Received: {file.filename} ({file.content_type})")
        
        # Save uploaded file
        temp_file = "temp_upload_raw.webm"
        content = await file.read()
        with open(temp_file, "wb") as f:
            f.write(content)
        print(f"✅ Saved {len(content)} bytes")
        
        # Convert to WAV
        print("🔄 Converting to WAV...")
        from pydub import AudioSegment
        audio = AudioSegment.from_file(temp_file)
        audio_file = "temp_upload.wav"
        audio.export(audio_file, format="wav", parameters=["-ar", "16000", "-ac", "1"])
        print(f"✅ Converted to {audio_file}")
        
        # Transcribe with Whisper
        print("🔄 Transcribing via Pipecat...")
        user_text, detected_lang = whisper_service.transcribe(audio_file)
        print(f"✅ Transcribed: '{user_text}' (lang: {detected_lang})")
        
        lang_names = {"en": "English", "hi": "Hindi", "te": "Telugu"}
        
        # Generate LLM response
        print("🤔 Generating response via Pipecat pipeline...")
        response = llm_service.generate_response(user_text, language=detected_lang)
        print(f"✅ Response: '{response}'")
        
        # Generate TTS
        print("🔊 Generating speech...")
        import time
        output_file = f"response_{int(time.time())}.wav"
        tts_success = tts_service.speak(
            response, 
            output_file=output_file, 
            speaker_wav=audio_file, 
            language=detected_lang, 
            play_audio=False
        )
        
        if tts_success:
            print(f"✅ Speech saved to {output_file}")
        else:
            print(f"❌ Speech generation failed!")
            output_file = None
        
        return {
            "transcript": user_text,
            "language": lang_names.get(detected_lang, detected_lang),
            "response": response,
            "audio_file": output_file
        }
        
    except Exception as e:
        import traceback
        error_msg = f"Error: {str(e)}\n{traceback.format_exc()}"
        print(f"❌ {error_msg}")
        return {
            "error": str(e),
            "transcript": "",
            "language": "",
            "response": ""
        }

@app.get("/audio/{filename}")
async def get_audio(filename: str):
    """Serve generated audio files"""
    file_path = Path(filename)
    if file_path.exists():
        print(f"✅ Serving audio file: {filename}")
        return FileResponse(str(file_path), media_type="audio/wav")
    else:
        print(f"❌ Audio file not found: {filename}")
        print(f"   Current directory: {Path.cwd()}")
        print(f"   Looking for: {file_path.absolute()}")
        return {"error": "File not found"}

@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown"""
    tts_service.cleanup()
    print("✅ Cleaned up resources")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🌐 Voice Agent Web Server")
    print("="*60)
    print("📍 Open: http://localhost:8000")
    print("🎙️  Click 'Start Recording' to begin")
    print("="*60 + "\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)
