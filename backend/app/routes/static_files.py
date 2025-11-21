"""
Static Files Route for GameManager

Serves static files (QR codes, images) via Cloudflare Tunnel
This is needed because Flask's default static serving doesn't work with blueprints
"""

from flask import Blueprint, send_from_directory, current_app
import os

static_files_bp = Blueprint('static_files', __name__)


@static_files_bp.route('/static/<path:filename>')
def serve_static(filename):
    """
    Serve static files from backend/static/ folder.

    This route is needed for production deployment where static files
    are served via Cloudflare Tunnel from local machine.

    Examples:
        /static/gcash_qr.jpg
        /static/payment_screenshots/12345.jpg
    """
    static_folder = os.path.join(current_app.config['BASE_DIR'], 'static')
    return send_from_directory(static_folder, filename)


@static_files_bp.route('/uploads/covers/<path:filename>')
def serve_cover(filename):
    """
    Serve game cover images from backend/uploads/covers/ folder.

    Examples:
        /uploads/covers/12345_mario.jpg
    """
    return send_from_directory(current_app.config['COVERS_FOLDER'], filename)


@static_files_bp.route('/uploads/games/<path:filename>')
def serve_game(filename):
    """
    Serve game files from backend/uploads/games/ folder.

    Note: In production, game downloads should use the authenticated
    /api/games/{id}/download endpoint instead for security.
    """
    return send_from_directory(current_app.config['GAMES_FOLDER'], filename)


@static_files_bp.route('/scanned_games/<path:filename>')
def serve_scanned_game(filename):
    """
    Serve scanned game files from backend/scanned_games/ folder.
    """
    return send_from_directory(current_app.config['SCAN_FOLDER'], filename)
