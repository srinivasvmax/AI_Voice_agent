"""
Batch Audio Processor
Process multiple audio files from a folder automatically
"""
import os
import json
from pathlib import Path
from datetime import datetime
from services.llm_service_api import LLMService
from services.whisper_service import WhisperService
from services.tts_service import TTSService

class BatchAudioProcessor:
    def __init__(self, input_folder="input", output_folder="output"):
        print("="*60)
        print("🎙️  Batch Audio Processor")
        print("="*60)
        
        self.input_folder = Path(input_folder)
        self.output_folder = Path(output_folder)
        
        # Create folders if they don't exist
        self.input_folder.mkdir(exist_ok=True)
        self.output_folder.mkdir(exist_ok=True)
        (self.output_folder / "audio").mkdir(exist_ok=True)
        
        # Initialize services
        print("\nInitializing services...")
        self.llm_service = LLMService()
        self.whisper_service = WhisperService()
        self.tts_service = TTSService()
        
        print("✅ Batch processor ready!\n")
    
    def get_audio_files(self):
        """Get all audio files from input folder"""
        audio_extensions = ['.wav', '.mp3', '.webm', '.ogg', '.m4a', '.flac']
        audio_files = []
        
        for ext in audio_extensions:
            audio_files.extend(self.input_folder.glob(f'*{ext}'))
        
        return sorted(audio_files)
    
    def process_file(self, audio_file, index):
        """Process a single audio file"""
        print(f"\n{'='*60}")
        print(f"Processing [{index}]: {audio_file.name}")
        print(f"{'='*60}")
        
        result = {
            "file": audio_file.name,
            "timestamp": datetime.now().isoformat(),
            "transcript": "",
            "language": "",
            "response": "",
            "audio_output": ""
        }
        
        try:
            # 1. Transcribe
            print("🔄 Transcribing...")
            transcript, language = self.whisper_service.transcribe(str(audio_file))
            result["transcript"] = transcript
            result["language"] = language
            
            lang_names = {"en": "English", "hi": "Hindi", "te": "Telugu"}
            print(f"🌐 Language: {lang_names.get(language, language)}")
            print(f"📝 Transcript: {transcript}")
            
            # 2. Generate LLM response
            print("🤔 Generating response...")
            response = self.llm_service.generate_response(transcript, language=language)
            result["response"] = response
            print(f"💬 Response: {response}")
            
            # 3. Generate TTS
            print("🔊 Generating speech...")
            output_audio = self.output_folder / "audio" / f"response_{index:03d}.wav"
            self.tts_service.speak(
                response,
                output_file=str(output_audio),
                speaker_wav=str(audio_file),
                language=language,
                play_audio=False
            )
            result["audio_output"] = str(output_audio)
            print(f"✅ Saved: {output_audio.name}")
            
            result["status"] = "success"
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            result["status"] = "error"
            result["error"] = str(e)
        
        return result
    
    def process_all(self):
        """Process all audio files in input folder"""
        audio_files = self.get_audio_files()
        
        if not audio_files:
            print(f"⚠️  No audio files found in '{self.input_folder}' folder")
            print(f"\nSupported formats: .wav, .mp3, .webm, .ogg, .m4a, .flac")
            print(f"Place your audio files in the '{self.input_folder}' folder and run again.")
            return
        
        print(f"📁 Found {len(audio_files)} audio file(s)")
        print(f"📂 Input folder: {self.input_folder.absolute()}")
        print(f"📂 Output folder: {self.output_folder.absolute()}")
        
        # Process each file
        results = []
        for i, audio_file in enumerate(audio_files, 1):
            result = self.process_file(audio_file, i)
            results.append(result)
        
        # Save results
        self.save_results(results)
        
        # Print summary
        self.print_summary(results)
    
    def save_results(self, results):
        """Save all results to files"""
        print(f"\n{'='*60}")
        print("💾 Saving results...")
        print(f"{'='*60}")
        
        # Save JSON
        json_file = self.output_folder / "results.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"✅ Saved: {json_file}")
        
        # Save transcripts
        transcript_file = self.output_folder / "transcripts.txt"
        with open(transcript_file, 'w', encoding='utf-8') as f:
            f.write("="*60 + "\n")
            f.write("TRANSCRIPTS\n")
            f.write("="*60 + "\n\n")
            for i, result in enumerate(results, 1):
                f.write(f"[{i}] {result['file']}\n")
                f.write(f"Language: {result['language']}\n")
                f.write(f"Transcript: {result['transcript']}\n")
                f.write("-"*60 + "\n\n")
        print(f"✅ Saved: {transcript_file}")
        
        # Save responses
        response_file = self.output_folder / "responses.txt"
        with open(response_file, 'w', encoding='utf-8') as f:
            f.write("="*60 + "\n")
            f.write("AI RESPONSES\n")
            f.write("="*60 + "\n\n")
            for i, result in enumerate(results, 1):
                f.write(f"[{i}] {result['file']}\n")
                f.write(f"Question: {result['transcript']}\n")
                f.write(f"Response: {result['response']}\n")
                f.write("-"*60 + "\n\n")
        print(f"✅ Saved: {response_file}")
    
    def print_summary(self, results):
        """Print processing summary"""
        print(f"\n{'='*60}")
        print("📊 SUMMARY")
        print(f"{'='*60}")
        
        total = len(results)
        success = sum(1 for r in results if r.get('status') == 'success')
        failed = total - success
        
        print(f"Total files: {total}")
        print(f"✅ Success: {success}")
        print(f"❌ Failed: {failed}")
        
        print(f"\n📂 Results saved in: {self.output_folder.absolute()}")
        print(f"   - results.json (detailed JSON)")
        print(f"   - transcripts.txt (all transcriptions)")
        print(f"   - responses.txt (all AI responses)")
        print(f"   - audio/ (TTS audio files)")
        
        print(f"\n{'='*60}")
        print("✅ Batch processing complete!")
        print(f"{'='*60}\n")
    
    def cleanup(self):
        """Clean up resources"""
        self.tts_service.cleanup()

def main():
    """Main entry point"""
    print("\n")
    processor = BatchAudioProcessor(input_folder="input", output_folder="output")
    
    try:
        processor.process_all()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    finally:
        processor.cleanup()

if __name__ == "__main__":
    main()
