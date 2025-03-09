import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Database settings
DATABASE_URL = os.getenv(
    'DATABASE_URL',
    'postgresql://postgres:postgres@localhost:5432/medical_diagnosis_db'
)

# Security settings
SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Application settings
APP_NAME = "AI Medical Diagnosis System"
APP_VERSION = "1.0.0"
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# ML Model settings
MODEL_PATH = Path(__file__).parent.parent / 'models'
ALLOWED_MODELS = ['svm', 'logistic_regression', 'random_forest']
DEFAULT_MODEL = 'random_forest'

# Logging settings
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = Path(__file__).parent.parent / 'logs' / 'app.log'

# API settings
API_V1_PREFIX = "/api/v1"
CORS_ORIGINS = [
    "http://localhost",
    "http://localhost:8501",  # Streamlit default port
    "http://localhost:8000",
] 