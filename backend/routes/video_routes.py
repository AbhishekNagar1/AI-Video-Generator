from flask import Blueprint, request, jsonify, send_file
from services.voice_generator import VoiceGenerator
from services.video_generator import VideoGenerator
import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('video', __name__, url_prefix='/api/video')

@bp.route('/generate', methods=['POST'])
def generate_video():
    try:
        data = request.get_json()
        content = data.get('content')
        presentation_path = data.get('presentation_path')

        if not all([content, presentation_path]):
            return jsonify({
                'error': 'Missing required parameters'
            }), 400

        # Convert to absolute path if relative
        if not os.path.isabs(presentation_path):
            base_dir = Path(__file__).resolve().parent.parent
            presentation_path = os.path.join(base_dir, presentation_path)

        logger.info(f"Using presentation path: {presentation_path}")
        
        if not os.path.exists(presentation_path):
            raise FileNotFoundError(f"Presentation file not found: {presentation_path}")

        # Generate voiceover
        voice_gen = VoiceGenerator()
        audio_path = voice_gen.generate_voiceover(content)
        logger.info(f"Generated audio at: {audio_path}")

        # Generate final video
        video_gen = VideoGenerator()
        video_path = video_gen.create_video(presentation_path, audio_path)
        logger.info(f"Generated video at: {video_path}")

        # Convert to relative path for response
        base_dir = Path(__file__).resolve().parent.parent
        relative_video_path = os.path.relpath(video_path, base_dir)

        return jsonify({
            'status': 'success',
            'video_path': relative_video_path
        })

    except FileNotFoundError as e:
        logger.error(f"File not found: {str(e)}")
        return jsonify({
            'error': 'File not found during processing'
        }), 404
    except Exception as e:
        logger.error(f"Error generating video: {str(e)}")
        return jsonify({
            'error': 'Something went wrong while generating the video. Please try again.'
        }), 500

@bp.route('/download/<path:filename>')
def download_video(filename):
    try:
        # Convert to absolute path
        base_dir = Path(__file__).resolve().parent.parent
        file_path = os.path.join(base_dir, filename)
        
        logger.info(f"Attempting to download file: {file_path}")
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Video file not found: {file_path}")
            
        return send_file(
            file_path,
            as_attachment=True,
            download_name=os.path.basename(filename)
        )
    except FileNotFoundError as e:
        logger.error(f"File not found: {str(e)}")
        return jsonify({
            'error': 'File not found during download'
        }), 404
    except Exception as e:
        logger.error(f"Error downloading video: {str(e)}")
        return jsonify({
            'error': 'Something went wrong during download. Please try again.'
        }), 500