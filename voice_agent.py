import asyncio
import sounddevice as sd
import soundfile as sf
import numpy as np
import time
from collections import deque

# Pipecat imports
from pipecat.frames.frames import Frame, AudioRawFrame, TextFrame, EndFrame
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineTask
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor

from services.llm_service_api import LLMService
from services.whisper_service import WhisperService
from services.tts_service import TTSService
from services.vad_service import VADService

class LLMProcessor(FrameProcessor):
    """Pipecat processor for LLM"""
    def __init__(self, llm_service):
        super().__init__()
        self.llm_service = llm_service
    
    async def process_frame(self, frame: Frame, direction: FrameDirection):
        await super().process_frame(frame, direction)
        
        if isinstance(frame, TextFrame):
            # Generate response
            response = self.llm_service.generate_response(frame.text)
            await self.push_frame(TextFrame(response))
        else:
            await self.push_frame(frame)

class WhisperProcessor(FrameProcessor):
    """Pipecat processor for Whisper STT"""
    def __init__(self, whisper_service):
        super().__init__()
        self.whisper_service = whisper_service
    
    async def process_frame(self, frame: Frame, direction: FrameDirection):
        await super().process_frame(frame, direction)
        
        if isinstance(frame, AudioRawFrame):
            # Transcribe audio
            # Save audio temporarily
            audio_file = "temp_audio.wav"
            sf.write(audio_file, frame.audio, frame.sample_rate)
            
            text, lang = self.whisper_service.transcribe(audio_file)
            print(f"📝 Transcribed: {text}")
            
            await self.push_frame(TextFrame(text))
        else:
            await self.push_frame(frame)

class VoiceAgentPipecat:
    def __init__(self, silence_duration=5.0):
        print("Initializing Pipecat Voice Agent...")
        
        # Initialize services
        self.llm_service = LLMService()
        self.whisper_service = WhisperService()
        self.tts_service = TTSService()
        
        # VAD service
        self.vad_service = VADService(threshold=0.3)
        
        # Audio settings
        self.RATE = 16000
        self.CHANNELS = 1
        self.SILENCE_DURATION = silence_duration
        
        print(f"✅ Pipecat Voice Agent initialized! (Silence: {silence_duration}s)")
    
    async def process_with_pipeline(self, audio_data):
        """Process audio through Pipecat pipeline"""
        # Create processors
        whisper_proc = WhisperProcessor(self.whisper_service)
        llm_proc = LLMProcessor(self.llm_service)
        
        # Create pipeline
        pipeline = Pipeline([
            whisper_proc,
            llm_proc
        ])
        
        # Create audio frame
        audio_frame = AudioRawFrame(
            audio=audio_data,
            sample_rate=self.RATE,
            num_channels=self.CHANNELS
        )
        
        # Process through pipeline
        task = PipelineTask(pipeline)
        
        # Push frame and get result
        await task.queue_frame(audio_frame)
        await task.queue_frame(EndFrame())
        
        # Collect output
        responses = []
        async for frame in task:
            if isinstance(frame, TextFrame):
                responses.append(frame.text)
        
        return responses[-1] if responses else None
    
    def record_audio_vad(self):
        """Record audio with VAD auto-stop"""
        print("\n🎤 Recording... (auto-stops after silence)")
        
        frames = []
        recording = [True]
        vad_chunk_size = 512
        silence_chunks = deque(maxlen=int(self.SILENCE_DURATION / 0.032))
        
        def callback(indata, frame_count, time_info, status):
            if not recording[0]:
                return
            
            frames.append(indata.copy())
            
            # VAD check
            if len(indata) == vad_chunk_size:
                is_speech, prob = self.vad_service.is_speech(indata.flatten())
                silence_chunks.append(not is_speech)
                
                if len(silence_chunks) == silence_chunks.maxlen:
                    if all(silence_chunks):
                        print("\n🔇 Silence detected, stopping...")
                        recording[0] = False
        
        stream = sd.InputStream(
            samplerate=self.RATE,
            channels=self.CHANNELS,
            callback=callback,
            dtype='float32',
            blocksize=vad_chunk_size
        )
        
        stream.start()
        while recording[0]:
            time.sleep(0.1)
        stream.stop()
        stream.close()
        
        if frames:
            audio_data = np.concatenate(frames, axis=0)
            print("✅ Recording stopped")
            return audio_data
        else:
            print("⚠️ No audio recorded")
            return None
    
    async def run(self):
        """Main conversation loop with Pipecat pipeline"""
        print("\n" + "="*50)
        print("🎙️  Pipecat Voice Agent Ready!")
        print("="*50)
        print(f"🎯 Using Pipecat Pipeline with VAD")
        print(f"🎯 Auto-stops after {self.SILENCE_DURATION}s of silence")
        print("Say 'exit' to quit\n")
        
        try:
            while True:
                # Record with VAD
                audio_data = self.record_audio_vad()
                
                if audio_data is None:
                    continue
                
                # Save for TTS voice cloning
                audio_file = "temp_audio.wav"
                sf.write(audio_file, audio_data, self.RATE)
                
                # Transcribe
                print("🔄 Transcribing...")
                user_text, detected_lang = self.whisper_service.transcribe(audio_file)
                lang_names = {"en": "English", "hi": "Hindi", "te": "Telugu"}
                print(f"🌐 Language: {lang_names.get(detected_lang, detected_lang)}")
                print(f"📝 You said: {user_text}")
                
                # Check for exit
                if user_text.lower() in ["exit", "quit", "stop", "goodbye"]:
                    print("👋 Goodbye!")
                    break
                
                # Generate response using Pipecat pipeline
                print("🤔 Thinking (via Pipecat pipeline)...")
                response = self.llm_service.generate_response(user_text, language=detected_lang)
                print(f"💬 Assistant: {response}")
                
                # Speak response
                print("🔊 Speaking...")
                self.tts_service.speak(response, speaker_wav=audio_file, language=detected_lang)
                
                print("\n" + "-"*50 + "\n")
                    
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Goodbye!")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        self.tts_service.cleanup()
        print("✅ Cleaned up resources")

if __name__ == "__main__":
    # Adjust silence_duration as needed (default: 5.0s)
    agent = VoiceAgentPipecat(silence_duration=5.0)
    asyncio.run(agent.run())
