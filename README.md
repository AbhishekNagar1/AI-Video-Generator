# AI Educational Video Generator

An AI-powered tool that generates educational videos based on user input, featuring dynamic presentations, human-like voiceovers, and synchronized content.
Demo Link: https://drive.google.com/file/d/1QMGzcwZa6ghGn4ciNXwBfA6fWbNRi9VX/view?usp=sharing

## 🌟 Features

- **Smart Content Generation**: Uses Gemini AI to create structured educational content
- **Dynamic Presentations**: Automatically generates beautiful slide decks
- **Natural Voiceovers**: Creates human-like narration using TTS
- **Synchronized Videos**: Combines slides and audio into engaging educational videos
- **Customizable Learning**: Adjust duration and detail level to match learning needs

## 🛠 Tech Stack

- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Python (Flask)
- **AI/ML**: 
  - Gemini AI for content generation
  - Google TTS for voice synthesis
- **Video Processing**: FFmpeg
- **Presentation**: python-pptx
- **Deployment**: Render/Vercel

## 📁 Project Structure

```
.
├── backend/         # Flask backend API
├── frontend/        # HTML/CSS/JS frontend
├── env/             # Environment variables
├── data/            # Generated content storage
├── docs/            # Documentation
└── tests/           # Test cases
```

## 🚀 Getting Started

<div align="center">
  <a href="https://license-instructions.netlify.app/" target="_blank">
    <img src="https://img.shields.io/badge/🚨-READ%20BEFORE%20FORKING-red?style=for-the-badge&labelColor=darkred" alt="Read Before Forking">
  </a>
</div>

1. Clone the repository
2. Set up environment variables in `env/.env`
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the development server:
   ```bash
   python backend/app.py
   ```

## 🔑 Environment Variables

Create a `.env` file in the `env/` directory with:

```
GEMINI_API_KEY=your_gemini_api_key
GOOGLE_TTS_KEY=your_tts_key
```

## 📝 License

MIT License - feel free to use this project for educational purposes.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
