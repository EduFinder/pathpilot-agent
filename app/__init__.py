from flask import Flask
from dotenv import load_dotenv
from werkzeug.middleware.proxy_fix import ProxyFix
import os


load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # Handle Vercel's reverse proxy so url_for() generates correct external URLs
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

    app.secret_key = os.getenv("FLASK_SECRET_KEY", "super_secret_key_change_me")


    # Run auto-migrations on startup
    try:
        from app.db.migrations import auto_migrate
        auto_migrate()
    except Exception as e:
        print(f"Migration skipped: {e}")

    # Register API routes
    from app.api.routes import api_bp
    app.register_blueprint(api_bp)

    from app.api.auth import auth_bp
    app.register_blueprint(auth_bp)

    @app.route('/')
    def index():
        from flask import render_template
        return render_template('index.html')
    
    return app