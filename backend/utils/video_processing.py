import os
import google.generativeai as genai
import google.cloud.texttospeech as tts
import moviepy.editor as mp
from PIL import Image

# Set up Gemini API Key
GEMINI_API_KEY = "your-gemini-api-key"  # Replace with your actual API key
genai.configure(api_key='AIzaSyCLQxQwpfGHrCfRNYg_Whp2rdDlMVf1h_8')


def generate_text_content(topic, level):
    """Use Gemini AI to generate structured educational content."""
    model = genai.GenerativeModel("gemini-pro")
    prompt = f"Create an educational script on '{topic}' with {level} depth. Provide structured content with key points."

    response = model.generate_content(prompt)
    return response.text.strip()


def text_to_speech(text, output_audio_path):
    """Convert AI-generated text to speech using Google Cloud TTS."""
    client = tts.TextToSpeechClient()
    synthesis_input = tts.SynthesisInput(text=text)
    voice = tts.VoiceSelectionParams(language_code="en-US", ssml_gender=tts.SsmlVoiceGender.NEUTRAL)
    audio_config = tts.AudioConfig(audio_encoding=tts.AudioEncoding.MP3)

    response = client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)

    with open(output_audio_path, "wb") as out:
        out.write(response.audio_content)


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
