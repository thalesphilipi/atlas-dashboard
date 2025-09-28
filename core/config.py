import os
from datetime import timedelta

class Config:
    """Configurações da aplicação"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'change-this-secret-key-in-production'
    MASTER_PASSWORD = os.environ.get('MASTER_PASSWORD') or 'atlas123'
    
    # Database
    DATABASE_PATH = os.path.join(os.path.dirname(__file__), '..', 'databases', 'app.db')
    
    # Session
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # Rate limiting
    RATE_LIMIT_DELAY = 2  # segundos entre ações