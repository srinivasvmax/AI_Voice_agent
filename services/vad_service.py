import numpy as np
import torch
from collections import deque

class VADService:
    """Voice Activity Detection using Silero VAD"""
    def __init__(self, threshold=0.5, sample_rate=16000):
        print("Loading Silero VAD model...")
        self.threshold = threshold
        self.sample_rate = sample_rate
        
        # Load Silero VAD model
        self.model, utils = torch.hub.load(
            repo_or_dir='snakers4/silero-vad',
            model='silero_vad',
            force_reload=False,
            onnx=False
        )
        
        self.get_speech_timestamps = utils[0]
        print("✅ VAD model loaded")
    
    def is_speech(self, audio_chunk):
        """Check if audio chunk contains speech"""
        # Convert to tensor
        if isinstance(audio_chunk, np.ndarray):
            audio_tensor = torch.from_numpy(audio_chunk).float()
        else:
            audio_tensor = audio_chunk
        
        # Ensure correct shape
        if len(audio_tensor.shape) > 1:
            audio_tensor = audio_tensor.squeeze()
        
        # Get speech probability
        speech_prob = self.model(audio_tensor, self.sample_rate).item()
        
        return speech_prob > self.threshold, speech_prob
    
    def detect_silence(self, audio_data, silence_duration=1.5):
        """Detect if there's been silence for specified duration"""
        # Split audio into chunks
        chunk_size = int(self.sample_rate * 0.5)  # 0.5 second chunks
        silence_chunks_needed = int(silence_duration / 0.5)
        
        recent_chunks = deque(maxlen=silence_chunks_needed)
        
        for i in range(0, len(audio_data), chunk_size):
            chunk = audio_data[i:i + chunk_size]
            if len(chunk) < chunk_size:
                break
            
            is_speech, prob = self.is_speech(chunk)
            recent_chunks.append(is_speech)
        
        # Check if all recent chunks are silence
        if len(recent_chunks) == silence_chunks_needed:
            return not any(recent_chunks)
        
        return False
