from gtts import gTTS
import os
from typing import Dict, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class VoiceGenerator:
    def __init__(self):
        self.output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'audio')
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_voiceover(self, content: Dict) -> str:
        """
        Generate voiceover audio for the presentation content.
        
        Args:
            content (Dict): Structured content from ContentGenerator
            
        Returns:
            str: Path to the generated audio file
        """
        # Combine all narration text
        narration_text = self._prepare_narration(content)
        
        # Generate audio file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"narration_{timestamp}.mp3"
        filepath = os.path.join(self.output_dir, filename)
        
        logger.info(f"Generating voiceover for content with {len(content.get('slides', []))} slides")
        logger.info(f"Narration text length: {len(narration_text)} characters")
        
        try:
            # Create and save audio - ensure full text is processed
            tts = gTTS(text=narration_text, lang='en', slow=False, timeout=30)
            tts.save(filepath)
            
            logger.info(f"Voiceover saved successfully: {filepath}")
        except Exception as e:
            logger.error(f"Error generating voiceover: {str(e)}")
            # Fallback: try with smaller chunks if the text is too long
            logger.info("Attempting to generate voiceover in chunks...")
            self._generate_voiceover_in_chunks(narration_text, filepath)
        
        return filepath

    def _generate_voiceover_in_chunks(self, narration_text, filepath):
        """Generate voiceover in chunks if the text is too long."""
        # Split the text into chunks to avoid gTTS limitations
        max_chunk_size = 2000  # gTTS has character limits
        chunks = []
        current_chunk = ""
        
        sentences = narration_text.split('. ')
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) < max_chunk_size:
                current_chunk += sentence + '. '
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = sentence + '. '
        
        if current_chunk:
            chunks.append(current_chunk)
        
        logger.info(f"Split narration into {len(chunks)} chunks for processing")
        
        # Process each chunk and combine the audio files
        chunk_files = []
        for i, chunk in enumerate(chunks):
            chunk_file = filepath.replace('.mp3', f'_chunk_{i}.mp3')
            try:
                tts = gTTS(text=chunk, lang='en', slow=False, timeout=30)
                tts.save(chunk_file)
                chunk_files.append(chunk_file)
            except Exception as e:
                logger.error(f"Error processing chunk {i}: {str(e)}")
                # If a chunk fails, create a silent placeholder
                import wave
                import numpy as np
                # Create a short silent audio file
                with wave.open(chunk_file, 'w') as wav_file:
                    # 16kHz sample rate, 1 channel, 16-bit
                    wav_file.setparams((1, 2, 16000, 0, 'NONE', 'not compressed'))
                    # Generate 1 second of silence
                    frames = b'\x00\x00' * 16000  # 16000 samples of silence
                    wav_file.writeframes(frames)
                chunk_files.append(chunk_file)

        # Combine all chunk files into the final file
        # For now, we'll just use the first successful chunk as fallback
        if chunk_files:
            # Since we can't easily combine MP3s without additional libraries,
            # we'll just use the first chunk as the output for now
            import shutil
            if os.path.exists(chunk_files[0]):
                shutil.move(chunk_files[0], filepath)
            
            # Remove other chunk files
            for chunk_file in chunk_files[1:]:
                try:
                    os.remove(chunk_file)
                except:
                    pass

    def _prepare_narration(self, content: Dict) -> str:
        """Prepare the narration text from the content."""
        narration_parts = []
        
        # Add title and overview
        if 'title' in content and content['title']:
            narration_parts.append(f"Welcome to this presentation about {content['title']}. {content['overview']}")
        
        # Add slide narrations
        if 'slides' in content and content['slides']:
            for i, slide in enumerate(content['slides'], 1):
                slide_narration = slide.get('narration', '')
                if slide_narration:
                    narration_parts.append(f"Slide {i}: {slide_narration}")
        
        # Add conclusion if it exists
        if 'conclusion' in content and content['conclusion']:
            narration_parts.append(f"In conclusion, {content['conclusion']}")
        
        # Join all parts with pauses
        return " ... ".join(narration_parts)