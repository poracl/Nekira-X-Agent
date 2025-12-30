import vertexai
from vertexai.generative_models import GenerativeModel
import os
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(module)s - %(message)s")

_vision_model = None
_text_model = None

def initialize_vertex_ai():
    """Initializes Vertex AI with project ID and location from environment variables."""
    global _vision_model, _text_model
    
    PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT_ID")
    LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")

    if not PROJECT_ID:
        logging.warning("GOOGLE_CLOUD_PROJECT_ID not set. Vertex AI functions may fail.")
        return False

    try:
        vertexai.init(project=PROJECT_ID, location=LOCATION)
        logging.info(f"Vertex AI initialized for project {PROJECT_ID} in {LOCATION}")
        return True
    except Exception as e:
        logging.error(f"Failed to initialize Vertex AI: {e}")
        return False

def get_vision_model() -> GenerativeModel:
    """Returns an initialized Gemini Vision Pro model instance."""
    global _vision_model
    if _vision_model is None:
        if initialize_vertex_ai():
            try:
                # Changed model name here
                _vision_model = GenerativeModel("gemini-2.5-flash-preview-05-20") 
                logging.info("Gemini Vision Pro model initialized.")
            except Exception as e:
                logging.error(f"Failed to initialize Gemini Vision Pro model: {e}")
    return _vision_model

def get_text_model() -> GenerativeModel:
    """Returns an initialized Gemini Pro text model instance."""
    global _text_model
    if _text_model is None:
        if initialize_vertex_ai():
            try:
                _text_model = GenerativeModel("gemini-pro")
                logging.info("Gemini Pro text model initialized.")
            except Exception as e:
                logging.error(f"Failed to initialize Gemini Pro text model: {e}")
    return _text_model