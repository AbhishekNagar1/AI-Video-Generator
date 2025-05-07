import google.generativeai as genai
import os
from typing import Dict, List
import logging
import json
import traceback
from pathlib import Path
import re

# Set up detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ContentGenerator:
    def __init__(self):
        try:
            # Get API key from environment
            api_key = os.getenv('GEMINI_API_KEY')
            logger.info(f"API Key found: {'Yes' if api_key else 'No'}")
            if api_key:
                logger.debug(f"API Key length: {len(api_key)}")
            
            if not api_key:
                raise ValueError("GEMINI_API_KEY not found in environment variables. Please check your .env file.")
            
            # Configure the API with the correct base URL
            logger.info("Configuring Gemini AI...")
            genai.configure(
                api_key=api_key,
                transport='rest',
                client_options={
                    'api_endpoint': 'https://generativelanguage.googleapis.com'
                }
            )
            logger.info("Gemini AI configured successfully")
            
            # List available models
            logger.info("Fetching available models...")
            models = genai.list_models()
            available_models = [model.name for model in models]
            logger.info(f"Available models: {available_models}")
            
            # Use gemini-1.5-pro model
            if 'models/gemini-1.5-pro' in available_models:
                logger.info("Initializing gemini-1.5-pro model...")
                self.model = genai.GenerativeModel('gemini-1.5-pro')
                logger.info("Model initialized successfully")
            else:
                raise ValueError(f"gemini-1.5-pro model not found. Available models: {available_models}")
                
        except Exception as e:
            logger.error(f"Error in ContentGenerator initialization: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def generate(self, topic: str, duration: int, detail_level: str) -> Dict:
        """
        Generate educational content based on topic, duration, and detail level.
        
        Args:
            topic (str): The topic to generate content for
            duration (int): Duration in minutes
            detail_level (str): 'low', 'medium', or 'high'
            
        Returns:
            Dict: Structured content with slides and narration
        """
        try:
            logger.info(f"Generating content for topic: {topic}, duration: {duration}, detail_level: {detail_level}")
            
            # Create prompt
            prompt = self._create_prompt(topic, duration, detail_level)
            logger.debug(f"Generated prompt: {prompt}")
            
            # Generate content with safety settings
            logger.info("Sending request to Gemini AI...")
            response = self.model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.7,
                    "top_p": 0.8,
                    "top_k": 40,
                    "max_output_tokens": 2048,
                },
                safety_settings=[
                    {
                        "category": "HARM_CATEGORY_HARASSMENT",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    },
                    {
                        "category": "HARM_CATEGORY_HATE_SPEECH",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    },
                    {
                        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    },
                    {
                        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    }
                ]
            )
            logger.info("Received response from Gemini AI")
            
            # Log response details
            logger.debug(f"Response type: {type(response)}")
            logger.debug(f"Response text: {response.text}")
            
            # Parse and structure the response
            content = self._parse_response(response.text)
            logger.info("Successfully parsed response")
            return content
            
        except Exception as e:
            logger.error(f"Error generating content: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def _create_prompt(self, topic: str, duration: int, detail_level: str) -> str:
        """Create a detailed prompt for the AI model."""
        try:
            prompt = f"""
            Create an educational presentation about {topic} that is {duration} minutes long.
            Detail level: {detail_level}
            
            Please structure the content as follows:
            1. Title slide with topic and brief overview
            2. Main content slides (3-5 slides for low detail, 5-7 for medium, 7-10 for high)
            3. Each slide should have:
               - A clear heading
               - 3-5 bullet points or a brief paragraph
               - Key concepts to emphasize
            4. Conclusion slide with main takeaways
            
            Format the response as JSON with the following structure:
            {{
                "title": "Presentation Title",
                "overview": "Brief overview",
                "slides": [
                    {{
                        "title": "Slide Title",
                        "content": "Slide content",
                        "key_points": ["point1", "point2"],
                        "narration": "Detailed narration text"
                    }}
                ],
                "conclusion": "Conclusion text"
            }}
            """
            logger.debug(f"Created prompt: {prompt}")
            return prompt
        except Exception as e:
            logger.error(f"Error creating prompt: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def _parse_response(self, response_text: str) -> Dict:
        """Parse the AI response into structured content."""
        try:
            text = response_text.strip()
            # Remove triple backticks and optional 'json' after them
            text = re.sub(r'^```json\s*|```$', '', text, flags=re.IGNORECASE | re.MULTILINE).strip()
            data = json.loads(text)
            logger.info("Successfully parsed response")
            return data
        except Exception as e:
            logger.error(f"Failed to parse response as JSON: {str(e)}")
            logger.error(f"Response text: {response_text}")
            logger.warning("Returning sample structure")
            return self._sample_structure()

    def _sample_structure(self):
        # Implementation of _sample_structure method
        pass 