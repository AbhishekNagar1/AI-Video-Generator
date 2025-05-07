from flask import Blueprint, request, jsonify
from services.content_generator import ContentGenerator
from services.presentation_generator import PresentationGenerator
import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('content', __name__, url_prefix='/api/content')

@bp.route('/generate', methods=['POST'])
def generate_content():
    try:
        data = request.get_json()
        topic = data.get('topic')
        duration = data.get('duration')
        detail_level = data.get('detailLevel')

        if not all([topic, duration, detail_level]):
            return jsonify({
                'error': 'Missing required parameters'
            }), 400

        # Generate content using Gemini
        content_gen = ContentGenerator()
        content = content_gen.generate(topic, duration, detail_level)
        logger.info("Content generated successfully")

        # Generate presentation
        pres_gen = PresentationGenerator()
        presentation_path = pres_gen.create_presentation(content)
        logger.info(f"Presentation generated at: {presentation_path}")

        # Convert to relative path for response
        base_dir = Path(__file__).resolve().parent.parent
        relative_presentation_path = os.path.relpath(presentation_path, base_dir)

        return jsonify({
            'status': 'success',
            'content': content,
            'presentation_path': relative_presentation_path
        })

    except FileNotFoundError as e:
        logger.error(f"File not found: {str(e)}")
        return jsonify({
            'error': str(e)
        }), 404
    except Exception as e:
        logger.error(f"Error generating content: {str(e)}")
        return jsonify({
            'error': str(e)
        }), 500 