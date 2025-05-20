from flask import Flask
from flask_session import Session
from config import Config
import os

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Configure Flask-Session
    Session(app)
    
    # Configure and create necessary directories
    output_dir = app.config['OUTPUT_DIR']
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)
    
    return app
