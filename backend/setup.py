import os
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_directory(path):
    """Create directory if it doesn't exist."""
    try:
        os.makedirs(path, exist_ok=True)
        logger.info(f"Created directory: {path}")
    except Exception as e:
        logger.error(f"Error creating directory {path}: {str(e)}")

def setup_directories():
    """Create all required directories for the application."""
    # Get the base directory (where this script is located)
    base_dir = Path(__file__).resolve().parent
    
    # Define required directories
    directories = [
        base_dir / 'data' / 'presentations',
        base_dir / 'data' / 'audio',
        base_dir / 'data' / 'videos',
        base_dir / 'data' / 'output',
        base_dir / 'logs'
    ]
    
    # Create each directory
    for directory in directories:
        create_directory(directory)
        
    # Create empty __init__.py files in Python package directories
    package_dirs = [
        base_dir / 'routes',
        base_dir / 'services',
        base_dir / 'utils',
        base_dir / 'models'
    ]
    
    for package_dir in package_dirs:
        init_file = package_dir / '__init__.py'
        if not init_file.exists():
            try:
                init_file.touch()
                logger.info(f"Created __init__.py in {package_dir}")
            except Exception as e:
                logger.error(f"Error creating __init__.py in {package_dir}: {str(e)}")

if __name__ == '__main__':
    logger.info("Setting up application directories...")
    setup_directories()
    logger.info("Setup complete!") 