from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import moviepy.editor as mp
from gtts import gTTS
import requests

app = FastAPI()


# Request model
class VideoRequest(BaseModel):
    topic: str
    duration: int
    level: str


# Directory setup
OUTPUT_DIR = "data/output/"
os.makedirs(OUTPUT_DIR, exist_ok=True)


# Text-to-Speech & Video Generation
def generate_video(topic, duration, level):
    # 1️⃣ Generate AI-based text content
    ai_text = f"This is an educational video about {topic}. The level of detail is {level}."

    # 2️⃣ Convert AI Text to Speech
    tts = gTTS(text=ai_text, lang="en")
    audio_path = os.path.join(OUTPUT_DIR, f"{topic}.mp3")
    tts.save(audio_path)

    # 3️⃣ Create Video with Blank Background + Audio
    video = mp.TextClip(f"{topic.upper()} - {level} Level", fontsize=50, color='white', size=(1280, 720))
    video = video.set_duration(duration).set_position("center").set_fps(24)

    # 4️⃣ Add AI Voice to Video
    audio = mp.AudioFileClip(audio_path)
    final_video = video.set_audio(audio)

    # 5️⃣ Save the video
    video_path = os.path.join(OUTPUT_DIR, f"{topic}.mp4")
    final_video.write_videofile(video_path, codec="libx264", fps=24)

    return video_path


@app.post("/generate_video/")
async def generate_video_endpoint(request: VideoRequest):
    try:
        video_path = generate_video(request.topic, request.duration, request.level)
        return {"message": "Video generated successfully!", "video_url": video_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
