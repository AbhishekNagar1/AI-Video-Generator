from gtts import gTTS
import os
from typing import Dict, List
from datetime import datetime

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
        
        # Create and save audio
        tts = gTTS(text=narration_text, lang='en', slow=False)
        tts.save(filepath)
        
        return filepath

    def _prepare_narration(self, content: Dict) -> str:
        """Prepare the narration text from the content."""
        narration_parts = []
        
        # Add title and overview
        narration_parts.append(f"Welcome to this presentation about {content['title']}. {content['overview']}")
        
        # Add slide narrations
        for i, slide in enumerate(content['slides'], 1):
            narration_parts.append(f"Slide {i}: {slide['narration']}")
        
        # Add conclusion
        narration_parts.append(f"In conclusion, {content['conclusion']}")
        
        # Join all parts with pauses
        return " ... ".join(narration_parts) 