from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import logging
from pathlib import Path
import traceback

# Create logs directory if it doesn't exist
logs_dir = Path(__file__).resolve().parent / 'logs'
logs_dir.mkdir(exist_ok=True)
log_file = logs_dir / 'app.log'

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(str(log_file)),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
try:
    # Get the absolute path to the .env file
    env_path = Path(__file__).resolve().parent / 'env' / '.env'
    logger.info(f"Loading .env file from: {env_path}")
    
    if not env_path.exists():
        logger.error(f".env file not found at {env_path}")
        raise FileNotFoundError(f".env file not found at {env_path}")
    
    load_dotenv(env_path)
    logger.info("Environment variables loaded successfully")
    
    # Verify GEMINI_API_KEY
    api_key = os.getenv('GEMINI_API_KEY')
    if api_key:
        logger.info("GEMINI_API_KEY found in environment variables")
        logger.debug(f"API Key length: {len(api_key)}")
    else:
        logger.error("GEMINI_API_KEY not found in environment variables")
        raise ValueError("GEMINI_API_KEY not found in environment variables")
        
except Exception as e:
    logger.error(f"Error loading environment variables: {str(e)}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    raise

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Import routes after app initialization
try:
    from routes.content_routes import bp as content_bp
    from routes.video_routes import bp as video_bp
    logger.info("Routes imported successfully")
except Exception as e:
    logger.error(f"Error importing routes: {str(e)}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    raise

# Register blueprints
try:
    app.register_blueprint(content_bp)
    app.register_blueprint(video_bp)
    logger.info("Blueprints registered successfully")
except Exception as e:
    logger.error(f"Error registering blueprints: {str(e)}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    raise

@app.route('/health')
def health_check():
    try:
        logger.info("Health check requested")
        return jsonify({
            'status': 'healthy',
            'message': 'Server is running'
        })
    except Exception as e:
        logger.error(f"Error in health check: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    try:
        logger.info("Starting Flask application...")
        app.run(debug=True, port=5000)
    except Exception as e:
        logger.error(f"Error starting Flask application: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise 