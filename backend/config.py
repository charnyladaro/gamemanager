import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Base directory
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    # Database
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(BASE_DIR, "gamemanager.db")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key-change-in-production'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)

    # Upload folders
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    GAMES_FOLDER = os.path.join(UPLOAD_FOLDER, 'games')
    COVERS_FOLDER = os.path.join(UPLOAD_FOLDER, 'covers')
    SCAN_FOLDER = os.path.join(BASE_DIR, 'scanned_games')
    MAX_CONTENT_LENGTH = 500 * 1024 * 1024 * 1024  # 500GB max file size

    # CORS
    CORS_HEADERS = 'Content-Type'

    # Server
    HOST = '0.0.0.0'
    PORT = 5000

    # Gaming API for cover images (RAWG API)
    # Get your free API key at https://rawg.io/apidocs
    RAWG_API_KEY = os.environ.get('RAWG_API_KEY') or None
    RAWG_API_URL = 'https://api.rawg.io/api'

    # GCash Payment Configuration
    GCASH_MERCHANT_NUMBER = os.environ.get('GCASH_MERCHANT_NUMBER') or '09123456789'

    # Telegram Bot Configuration
    TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
    TELEGRAM_ADMIN_CHAT_ID = os.environ.get('TELEGRAM_ADMIN_CHAT_ID')

    # =========================================================================
    # PRODUCTION URL CONFIGURATION
    # =========================================================================
    # For hybrid deployment architecture:
    # - API_BASE_URL: Where your Flask backend API is hosted (e.g., Render.com)
    # - STORAGE_BASE_URL: Where your files are served from (e.g., Cloudflare Tunnel)
    #
    # Local Development:
    #   API_BASE_URL = http://localhost:5000
    #   STORAGE_BASE_URL = http://localhost:5000
    #
    # Production Hybrid Setup:
    #   API_BASE_URL = https://gamemanager-api.onrender.com
    #   STORAGE_BASE_URL = https://your-tunnel.trycloudflare.com
    # =========================================================================

    # API Base URL - where the Flask backend is hosted
    # Leave as None for local development (uses request.host_url)
    API_BASE_URL = os.environ.get('API_BASE_URL') or None

    # Storage Base URL - where uploads/static files are served from
    # In production, this should point to your Cloudflare Tunnel URL
    # Leave as None for local development (uses API_BASE_URL)
    STORAGE_BASE_URL = os.environ.get('STORAGE_BASE_URL') or None

    # Legacy local-only configuration (commented for reference)
    # Uncomment these lines if you want to force local development URLs
    # API_BASE_URL = 'http://localhost:5000'
    # STORAGE_BASE_URL = 'http://localhost:5000'
