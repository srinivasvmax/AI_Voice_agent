from TTS.api import TTS
import os

# Optional pyaudio import for desktop playback
try:
    import pyaudio
    import wave
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False
    print("⚠️ PyAudio not available - audio playback disabled (file output still works)")

class TTSService:
    def __init__(self):
        print("Loading TTS models...")
        # Initialize models for different languages
        self.models = {}
        
        # Load XTTS v2 - supports multiple languages including Hindi
        try:
            print("📥 Loading XTTS v2 (multilingual: en, hi, and more)...")
            self.models['xtts'] = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
            print("✅ XTTS v2 loaded")
            print("   Supports: English, Spanish, French, German, Italian, Portuguese, Polish, Turkish, Russian, Dutch, Czech, Arabic, Chinese, Japanese, Hungarian, Korean, Hindi")
        except Exception as e:
            print(f"⚠️ XTTS v2 failed: {e}")
            print("   Falling back to English-only model...")
            try:
                self.models['en'] = TTS("tts_models/en/ljspeech/tacotron2-DDC")
                print("✅ English TTS loaded as fallback")
            except Exception as e2:
                print(f"❌ All TTS models failed: {e2}")
        
        # Initialize audio only if pyaudio is available
        if PYAUDIO_AVAILABLE:
            self.audio = pyaudio.PyAudio()
            self.CHUNK = 1024
        else:
            self.audio = None
            
        print(f"✅ TTS service ready with {len(self.models)} model(s) loaded")
    
    def _detect_code_mixing(self, text, primary_language):
        """Detect if text contains mixed languages (code-mixing)"""
        # Simple heuristic: check for Latin characters in non-English text
        import re
        has_latin = bool(re.search(r'[a-zA-Z]+', text))
        has_native = bool(re.search(r'[^\x00-\x7F]+', text))  # Non-ASCII characters
        
        if primary_language != 'en' and has_latin and has_native:
            # Extract English words
            english_words = re.findall(r'\b[a-zA-Z]+\b', text)
            if english_words:
                print(f"   ℹ️ Code-mixing detected! English words: {', '.join(english_words[:5])}")
                return True, english_words
        return False, []
    
    def speak(self, text, output_file="response.wav", speaker_wav=None, language="en", play_audio=True):
        """Convert text to speech and optionally play it"""
        print(f"\n🔊 TTS Request:")
        print(f"   Text: {text[:50]}...")
        print(f"   Language: {language}")
        print(f"   Speaker WAV: {speaker_wav}")
        print(f"   Output: {output_file}")
        
        # Detect code-mixing
        is_mixed, english_words = self._detect_code_mixing(text, language)
        if is_mixed:
            print(f"   🌐 Code-mixing detected (mixing {language} with English)")
        
        try:
            # Use XTTS v2 for all languages
            if 'xtts' in self.models:
                model = self.models['xtts']
                print(f"🌐 Using XTTS v2 for {language}")
                
                # XTTS requires speaker_wav for voice cloning
                if not speaker_wav or not os.path.exists(speaker_wav):
                    print(f"⚠️ WARNING: XTTS requires speaker_wav for voice cloning")
                    print(f"   Using default voice")
                    # Try without speaker_wav (will use default voice)
                    model.tts_to_file(
                        text=text,
                        file_path=output_file,
                        language=language
                    )
                else:
                    print(f"   Using voice cloning with: {speaker_wav}")
                    model.tts_to_file(
                        text=text,
                        file_path=output_file,
                        speaker_wav=speaker_wav,
                        language=language
                    )
            elif 'en' in self.models:
                # Fallback to English-only model
                print(f"⚠️ XTTS not available, using English model")
                model = self.models['en']
                model.tts_to_file(text=text, file_path=output_file)
            else:
                print(f"❌ No TTS model available")
                return False
            
            # Verify file was created
            if os.path.exists(output_file):
                file_size = os.path.getsize(output_file)
                print(f"✅ Audio file created: {output_file} ({file_size} bytes)")
                if file_size == 0:
                    print(f"❌ ERROR: File is empty!")
                    return False
            else:
                print(f"❌ Audio file NOT created: {output_file}")
                return False
                
        except Exception as e:
            print(f"❌ TTS error: {e}")
            import traceback
            print(traceback.format_exc())
            return False
        
        # Play the audio only if requested and pyaudio is available
        if play_audio and PYAUDIO_AVAILABLE and self.audio:
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
        elif play_audio and not PYAUDIO_AVAILABLE:
            print("⚠️ Audio playback skipped (PyAudio not available)")
        
        return True
    
    def cleanup(self):
        """Clean up audio resources"""
        if PYAUDIO_AVAILABLE and self.audio:
            self.audio.terminate()
