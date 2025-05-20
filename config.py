import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SCHEMA_DIR = os.path.join(basedir, 'schema')
    OUTPUT_DIR = os.path.join(basedir, 'output')
    OPENROUTE_SERVICE_API_KEY = os.environ.get('OPENROUTE_SERVICE_API_KEY')
    
    # Ensure required directories exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Flask session configuration - use filesystem on dev, secure cookie on Heroku
    SESSION_TYPE = 'filesystem'
    if os.environ.get('DYNO'):  # Check if running on Heroku
        SESSION_TYPE = 'cookie'
        SESSION_PERMANENT = False
        SESSION_USE_SIGNER = True

