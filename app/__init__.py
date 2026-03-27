from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os
import logging
import google.generativeai as genai

load_dotenv()


def create_app():
    app = Flask(__name__)
    CORS(app)

    # Configuration
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-key")
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024

    # Logging
    logging.basicConfig(level=logging.INFO)

    # Configure Gemini AI with correct model
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        genai.configure(api_key=api_key)
        # Use the correct model name
        try:
            # Try different model names
            model_names = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"]
            for model_name in model_names:
                try:
                    app.config["GEMINI_MODEL"] = genai.GenerativeModel(model_name)
                    logging.info(f"Using Gemini model: {model_name}")
                    break
                except:
                    continue
        except Exception as e:
            logging.warning(f"Could not initialize Gemini: {e}")
            app.config["GEMINI_MODEL"] = None
    else:
        app.config["GEMINI_MODEL"] = None
        logging.warning("GEMINI_API_KEY not found")

    # Register blueprints
    from .main import main_bp

    app.register_blueprint(main_bp)

    return app
