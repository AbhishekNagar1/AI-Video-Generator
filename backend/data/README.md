# Data Directory

This directory contains all generated content for the AI Educational Video Generator.

## Directory Structure

```
data/
├── presentations/    # Generated PowerPoint presentations
├── audio/           # Generated voiceover audio files
└── videos/          # Final generated videos
```

## File Naming Convention

- Presentations: `presentation_YYYYMMDD_HHMMSS.pptx`
- Audio: `narration_YYYYMMDD_HHMMSS.mp3`
- Videos: `video_YYYYMMDD_HHMMSS.mp4`

## Cleanup

The system automatically manages these files, but you may want to periodically clean up old files to save disk space. You can safely delete files older than your desired retention period. 