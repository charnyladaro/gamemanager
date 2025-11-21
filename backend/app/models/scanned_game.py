from datetime import datetime
from app.models.user import db
from flask import current_app, request

class ScannedGame(db.Model):
    __tablename__ = 'scanned_games'

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(500), nullable=False)
    file_path = db.Column(db.String(500), nullable=False, unique=True)
    file_size = db.Column(db.BigInteger)
    file_extension = db.Column(db.String(10))
    suggested_title = db.Column(db.String(200))
    cover_image = db.Column(db.String(255))
    
    # Timestamps
    detected_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Processing status
    is_processed = db.Column(db.Boolean, default=False)
    processed_at = db.Column(db.DateTime)
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'), nullable=True)
    
    # Relationship
    game = db.relationship('Game', backref='scanned_source', foreign_keys=[game_id])

    def _get_file_url(self, filepath, file_type='uploads'):
        """
        Generate full URL for a file based on deployment configuration.

        Args:
            filepath: Filename (e.g., '12345_cover.jpg')
            file_type: Type of file ('covers' for images, 'scanned_games' for game files)

        Returns:
            Full URL to the file
        """
        if not filepath:
            return None

        # Get base URL from config
        storage_base_url = current_app.config.get('STORAGE_BASE_URL')

        # If no storage URL configured, try to use API_BASE_URL
        if not storage_base_url:
            storage_base_url = current_app.config.get('API_BASE_URL')

        # If still no URL, fall back to request context (for local development)
        if not storage_base_url:
            try:
                storage_base_url = request.host_url.rstrip('/')
            except RuntimeError:
                # Outside request context, use localhost
                storage_base_url = 'http://localhost:5000'

        # Build the file path based on type
        if file_type == 'covers':
            path = f'/uploads/covers/{filepath}'
        elif file_type == 'scanned_games':
            path = f'/scanned_games/{filepath}'
        else:
            path = f'/uploads/{filepath}'

        return f'{storage_base_url}{path}'

    def to_dict(self):
        """Convert ScannedGame model to dictionary with full URLs."""
        return {
            'id': self.id,
            'filename': self.filename,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'file_extension': self.file_extension,
            'suggested_title': self.suggested_title,

            # Legacy field (filename only) - kept for backward compatibility
            # 'cover_image': self.cover_image,

            # New field with full URL (production-ready)
            'cover_image': self._get_file_url(self.cover_image, 'covers'),

            # Also include filename for debugging/reference
            'cover_image_filename': self.cover_image,

            'detected_at': self.detected_at.isoformat() if self.detected_at else None,
            'is_processed': self.is_processed,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None,
            'game_id': self.game_id
        }
