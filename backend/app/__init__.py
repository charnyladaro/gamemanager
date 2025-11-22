from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import Config
from app.models.user import db

def create_app(config_class=Config):
    # Configure Flask to use correct static folder
    # (backend/static instead of backend/app/static)
    import os
    static_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')
    app = Flask(__name__, static_folder=static_folder, static_url_path='/static')
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    # CORS: Allow API and static file routes
    # Legacy: CORS(app, resources={r"/api/*": {"origins": "*"}})
    # New: Also allow /static/, /uploads/, /scanned_games/ for Cloudflare Tunnel
    CORS(app, resources={
        r"/api/*": {"origins": "*"},
        r"/static/*": {"origins": "*"},
        r"/uploads/*": {"origins": "*"},
        r"/scanned_games/*": {"origins": "*"}
    })
    jwt = JWTManager(app)

    # Register blueprints
    from app.routes import auth_bp, games_bp, users_bp, friends_bp, game_requests_bp
    from app.routes.admin import admin_bp
    from app.routes.chunked_upload import chunked_upload_bp
    from app.routes.payments import payments_bp
    from app.routes.telegram_webhook import telegram_webhook_bp
    from app.routes.static_files import static_files_bp  # New: for serving static files via Cloudflare Tunnel
    from app.routes.setup import setup_bp  # New: for initial setup
    app.register_blueprint(auth_bp)
    app.register_blueprint(games_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(friends_bp)
    app.register_blueprint(game_requests_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(chunked_upload_bp)
    app.register_blueprint(payments_bp)
    app.register_blueprint(telegram_webhook_bp)
    app.register_blueprint(static_files_bp)  # New: serves /static/, /uploads/, /scanned_games/ routes
    app.register_blueprint(setup_bp)  # New: setup endpoints

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

