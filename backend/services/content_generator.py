import google.generativeai as genai
import os
from typing import Dict, List
import logging
import json
import traceback
from pathlib import Path
import re
import time
from tenacity import retry, stop_after_attempt, wait_exponential

# Set up detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ContentGenerator:
    def __init__(self):
        try:
            # Get API key from environment and strip any trailing newlines - critical for Cloud Run
            api_key = os.getenv('GEMINI_API_KEY', '').strip()
            logger.info(f"API Key found: {'Yes' if api_key else 'No'}")
            if api_key:
                logger.debug(f"API Key length: {len(api_key) if api_key else 0}")
            
            if not api_key:
                # In production, if not found in environment, you might want to try other methods
                # For now, we'll log this as a warning since it will be provided by Secret Manager in Cloud Run
                logger.warning("GEMINI_API_KEY not found in environment variables. In production, this should be provided by GCP Secret Manager.")
                # You can raise an exception in development, but for production deployment we'll continue
                # raise ValueError("GEMINI_API_KEY not found in environment variables. Please check your .env file.")
            
            # Configure the API with the correct base URL and new model
            logger.info("Configuring Gemini AI...")
            if api_key:  # Only configure if we have an API key
                genai.configure(
                    api_key=api_key,
                    transport='rest',
                    client_options={
                        'api_endpoint': 'https://generativelanguage.googleapis.com'
                    }
                )
                logger.info("Gemini AI configured successfully")
                
                # Initialize with the latest model
                logger.info("Initializing gemini-2.0-flash model...")
                self.model = genai.GenerativeModel('gemini-2.0-flash')
                logger.info("Model initialized successfully")
            else:
                logger.error("No API key provided - AI features will not work")
                raise ValueError("GEMINI_API_KEY not provided")
                
        except Exception as e:
            logger.error(f"Error in ContentGenerator initialization: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True
    )
    def generate(self, topic: str, duration: int, detail_level: str) -> Dict:
        """
        Generate educational content based on topic, duration, and detail level.
        Includes retry logic for rate limiting.
        
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
            
            # Generate content with safety settings and rate limiting
            logger.info("Sending request to Gemini AI...")
            try:
                response = self.model.generate_content(
                    contents=[{
                        "parts": [{
                            "text": prompt
                        }]
                    }],
                    generation_config={
                        "temperature": 0.7,
                        "top_p": 0.8,
                        "top_k": 40,
                        "max_output_tokens": 4096,  # Increased to allow for longer responses
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
            except Exception as api_error:
                if "429" in str(api_error):
                    logger.warning("Rate limit exceeded, waiting before retry...")
                    time.sleep(10)  # Wait 10 seconds before retry
                    raise  # This will trigger the retry decorator
                raise
            
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
            # Don't expose internal error details to the caller
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

            Ensure the response is complete and properly formatted JSON.
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
            
            # Handle potential truncation by trying to fix common JSON issues
            # Look for incomplete conclusion and try to complete it
            if not text.strip().endswith('}'):
                # Find if there's an incomplete conclusion and try to complete the JSON
                if '"conclusion":' in text:
                    # Add closing braces to complete the JSON
                    text += "\n  }\n}"
            
            data = json.loads(text)
            logger.info("Successfully parsed response")
            return data
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse response as JSON: {str(e)}")
            logger.error(f"Response text: {response_text}")
            
            # Try to fix common JSON issues
            try:
                # Try to find and extract the JSON portion
                start_idx = response_text.find('{')
                end_idx = response_text.rfind('}') + 1
                
                if start_idx != -1 and end_idx != 0:
                    json_part = response_text[start_idx:end_idx]
                    # Remove triple backticks again if they're in the extracted part
                    json_part = re.sub(r'^```json\s*|```$', '', json_part, flags=re.IGNORECASE | re.MULTILINE).strip()
                    
                    # Try to fix common issues
                    json_part = self._fix_json_issues(json_part)
                    
                    data = json.loads(json_part)
                    logger.info("Successfully parsed response after fixing JSON issues")
                    return data
            except Exception as fix_error:
                logger.error(f"Failed to fix JSON issues: {str(fix_error)}")
            
            logger.warning("Returning sample structure")
            return self._sample_structure()
        except Exception as e:
            logger.error(f"Error in _parse_response: {str(e)}")
            logger.warning("Returning sample structure")
            return self._sample_structure()

    def _fix_json_issues(self, json_text: str) -> str:
        """Attempt to fix common JSON parsing issues."""
        # Replace problematic characters
        json_text = json_text.replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
        
        # Try to balance braces
        open_braces = json_text.count('{')
        close_braces = json_text.count('}')
        
        while close_braces < open_braces:
            json_text += '}'
            close_braces += 1
            
        # Try to balance brackets
        open_brackets = json_text.count('[')
        close_brackets = json_text.count(']')
        
        while close_brackets < open_brackets:
            json_text += ']'
            close_brackets += 1
        
        # Try to ensure proper string termination
        try:
            # Find conclusion and ensure it's properly closed
            if '"conclusion":' in json_text:
                # Find the start of the conclusion value
                conclusion_start = json_text.find('"conclusion":') + len('"conclusion":')
                # Find the start of the next field or end of object
                next_field = json_text.find('"', conclusion_start)
                if next_field != -1:
                    # Extract the conclusion value
                    conclusion_value = json_text[conclusion_start:next_field].strip()
                    if conclusion_value.startswith('"') and not conclusion_value.endswith('"'):
                        # Add closing quote if missing
                        json_text = json_text[:next_field] + '"' + json_text[next_field:]
        except:
            pass  # If we can't fix it, return as is
        
        return json_text

    def _sample_structure(self):
        """Return a sample structure when parsing fails."""
        return {
            "title": "Sample Presentation",
            "overview": "This is a sample presentation.",
            "slides": [
                {
                    "title": "Sample Slide",
                    "content": "This is sample content.",
                    "key_points": ["Sample point"],
                    "narration": "This is sample narration."
                }
            ],
            "conclusion": "This is a sample conclusion."
        }