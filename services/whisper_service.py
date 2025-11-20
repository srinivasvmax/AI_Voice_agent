import whisper
import numpy as np
import soundfile as sf

class WhisperService:
    def __init__(self, model_size="large-v3"):
        print("Loading Whisper model...")
        self.model = whisper.load_model(model_size)
        print("✅ Whisper model loaded")
    
    def transcribe(self, audio_file):
        """Convert speech to text with language detection"""
        # Load audio directly without ffmpeg
        audio, sr = sf.read(audio_file, dtype='float32')
        
        # Convert to mono if stereo
        if len(audio.shape) > 1:
            audio = audio.mean(axis=1)
        
        # Resample to 16kHz if needed
        if sr != 16000:
            import scipy.signal
            audio = scipy.signal.resample(audio, int(len(audio) * 16000 / sr))
        
        # Ensure float32 type for Whisper
        audio = np.array(audio, dtype=np.float32)
        
        # Transcribe
        result = self.model.transcribe(audio, language=None, fp16=False)
        detected_lang = result.get("language", "en")
        text = result["text"].strip()
        return text, detected_lang
