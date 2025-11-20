from TTS.api import TTS
import pyaudio
import wave
import os

class TTSService:
    def __init__(self):
        print("Loading TTS models...")
        # Initialize models for different languages
        self.models = {}
        
        # Try to load multilingual model (supports multiple languages)
        try:
            self.models['multilingual'] = TTS("tts_models/multilingual/multi-dataset/your_tts")
            print("✅ Multilingual TTS model loaded (supports Telugu, Hindi, English)")
        except:
            print("⚠️ Multilingual model failed, trying XTTS...")
            try:
                self.models['multilingual'] = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
                print("✅ XTTS v2 loaded")
            except:
                print("⚠️ Using basic English model")
                self.models['en'] = TTS("tts_models/en/ljspeech/tacotron2-DDC")
        
        self.audio = pyaudio.PyAudio()
        self.CHUNK = 1024
        print("✅ TTS service ready")
    
    def speak(self, text, output_file="response.wav", speaker_wav=None, language="en", play_audio=True):
        """Convert text to speech and optionally play it"""
        # Language mapping
        lang_map = {
            "en": "en",
            "hi": "hi", 
            "te": "te"
        }
        tts_lang = lang_map.get(language, "en")
        
        try:
            model = self.models.get('multilingual', self.models.get('en'))
            
            # Check if model supports language parameter
            if hasattr(model, 'languages') and tts_lang in model.languages:
                print(f"🌐 Generating speech in {tts_lang}")
                if speaker_wav and os.path.exists(speaker_wav):
                    model.tts_to_file(
                        text=text,
                        file_path=output_file,
                        speaker_wav=speaker_wav,
                        language=tts_lang
                    )
                else:
                    model.tts_to_file(
                        text=text,
                        file_path=output_file,
                        language=tts_lang
                    )
            else:
                print(f"⚠️ Language {tts_lang} not supported, using default")
                model.tts_to_file(text=text, file_path=output_file)
                
        except Exception as e:
            print(f"⚠️ TTS error: {e}")
            # Simple fallback
            try:
                model = self.models.get('multilingual', self.models.get('en'))
                model.tts_to_file(text=text, file_path=output_file)
            except Exception as e2:
                print(f"❌ TTS failed: {e2}")
                return
        
        # Play the audio only if requested
        if play_audio:
            with wave.open(output_file, 'rb') as wf:
                stream = self.audio.open(
                    format=self.audio.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True
                )
                
                data = wf.readframes(self.CHUNK)
                while data:
                    stream.write(data)
                    data = wf.readframes(self.CHUNK)
                
                stream.stop_stream()
                stream.close()
    
    def cleanup(self):
        """Clean up audio resources"""
        self.audio.terminate()
