from flask import Flask
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # Register API routes
    from app.api.routes import api_bp
    app.register_blueprint(api_bp)
    
    return app