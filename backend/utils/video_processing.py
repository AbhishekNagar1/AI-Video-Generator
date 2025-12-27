import os
import google.generativeai as genai
import google.cloud.texttospeech as tts
import moviepy.editor as mp
from PIL import Image
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Set up Gemini API Key - strip any trailing newlines that may be added by Secret Manager
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '').strip()
if not GEMINI_API_KEY:
    # In production on GCP, this will be provided by Secret Manager
    logger.warning("GEMINI_API_KEY not found in environment variables. In production, this should be provided by GCP Secret Manager.")

# Configure Gemini
if GEMINI_API_KEY:
    genai.configure(
        api_key=GEMINI_API_KEY,
        transport='rest',
        client_options={
            'api_endpoint': 'https://generativelanguage.googleapis.com'
        }
    )
    logger.info("Gemini AI configured successfully")
else:
    logger.warning("GEMINI_API_KEY not set. AI features will not work.")

def generate_text_content(topic, level):
    """Use Gemini AI to generate structured educational content."""
    try:
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not set. Cannot generate content without API key.")
        
        model = genai.GenerativeModel("gemini-2.0-flash")
        prompt = f"Create an educational script on '{topic}' with {level} depth. Provide structured content with key points."

        response = model.generate_content(
            contents=[{
                "parts": [{
                    "text": prompt
                }]
            }],
            generation_config={
                "temperature": 0.7,
                "top_p": 0.8,
                "top_k": 40,
                "max_output_tokens": 2048,
            }
        )
        return response.text.strip()
    except Exception as e:
        logger.error(f"Error generating content: {str(e)}")
        raise


def text_to_speech(text, output_audio_path):
    """Convert AI-generated text to speech using Google Cloud TTS."""
    try:
        client = tts.TextToSpeechClient()
        synthesis_input = tts.SynthesisInput(text=text)
        voice = tts.VoiceSelectionParams(language_code="en-US", ssml_gender=tts.SsmlVoiceGender.NEUTRAL)
        audio_config = tts.AudioConfig(audio_encoding=tts.AudioEncoding.MP3)

        response = client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)

        with open(output_audio_path, "wb") as out:
            out.write(response.audio_content)
    except Exception as e:
        logger.error(f"Error in text-to-speech: {str(e)}")
        raise


def create_video_with_slides(topic, duration, level):
    """Generate a video with slides + voiceover."""
    script = generate_text_content(topic, level)

    # Save TTS Audio
    audio_path = "data/temp/audio.mp3"
    text_to_speech(script, audio_path)

    # Generate Slide (Placeholder)
    slide_path = "data/temp/slide.png"
    img = Image.new('RGB', (1280, 720), color=(73, 109, 137))
    img.save(slide_path)

    # Create Video
    clip = mp.ImageClip(slide_path).set_duration(duration)
    audio = mp.AudioFileClip(audio_path)
    clip = clip.set_audio(audio)

    output_path = f"data/output/{topic.replace(' ', '_')}.mp4"
    clip.write_videofile(output_path, fps=24)

    return output_path


def generate_video(topic, duration, level):
    """Main function to generate the educational video."""
    return create_video_with_slides(topic, duration, level)