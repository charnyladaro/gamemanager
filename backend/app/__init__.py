from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import Config
from app.models.user import db

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    jwt = JWTManager(app)

    # Register blueprints
    from app.routes import auth_bp, games_bp, users_bp, friends_bp, game_requests_bp
    from app.routes.admin import admin_bp
    from app.routes.chunked_upload import chunked_upload_bp
    from app.routes.payments import payments_bp
    from app.routes.telegram_webhook import telegram_webhook_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(games_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(friends_bp)
    app.register_blueprint(game_requests_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(chunked_upload_bp)
    app.register_blueprint(payments_bp)
    app.register_blueprint(telegram_webhook_bp)

    # Create database tables
    with app.app_context():
        db.create_all()
        
        # Run initial scan for games
        try:
            from app.services.scanner import GameScanner
            new_count = GameScanner.scan_folder()
            if new_count > 0:
                print(f"[GameScanner] Detected {new_count} new game(s) in scanned_games folder")
        except Exception as e:
            print(f"[GameScanner] Error during initial scan: {e}")

    # Create upload folders if they don't exist
    import os
    os.makedirs(Config.GAMES_FOLDER, exist_ok=True)
    os.makedirs(Config.COVERS_FOLDER, exist_ok=True)
    os.makedirs(Config.SCAN_FOLDER, exist_ok=True)

    return app

