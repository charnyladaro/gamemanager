from datetime import datetime
from app.models.user import db
from flask import current_app, request

class Game(db.Model):
    __tablename__ = 'games'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    publisher = db.Column(db.String(100))
    developer = db.Column(db.String(100))
    release_date = db.Column(db.Date)
    genre = db.Column(db.String(100))
    cover_image = db.Column(db.String(255))
    banner_image = db.Column(db.String(255))

    # File info
    file_path = db.Column(db.String(500))  # Path to game installer/executable
    file_size = db.Column(db.BigInteger)  # Size in bytes
    version = db.Column(db.String(50))

    # Pricing
    price = db.Column(db.Float, default=0.0)  # Price in PHP (0 = free game)

    # Metadata
    is_available = db.Column(db.Boolean, default=True)
    download_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user_games = db.relationship('UserGame', back_populates='game', cascade='all, delete-orphan')

    def _get_file_url(self, filepath, file_type='uploads'):
        """
        Generate full URL for a file based on deployment configuration.

        Args:
            filepath: Filename (e.g., '12345_cover.jpg')
            file_type: Type of file ('uploads' for games, 'covers' for images, 'static' for QR codes)

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
            # Images are served via /api/games/{id}/cover endpoint OR direct file path
            # For production with Cloudflare Tunnel, use direct path
            path = f'/uploads/covers/{filepath}'
        elif file_type == 'games':
            # Game files are served via /api/games/{id}/download endpoint
            # Return API endpoint URL instead of direct file path for security
            api_base_url = current_app.config.get('API_BASE_URL') or storage_base_url
            return f'{api_base_url}/api/games/{self.id}/download'
        elif file_type == 'static':
            path = f'/static/{filepath}'
        else:
            path = f'/uploads/{filepath}'

        return f'{storage_base_url}{path}'

    def to_dict(self, include_download_url=False):
        """
        Convert Game model to dictionary with full URLs.

        Args:
            include_download_url: If True, includes the download URL (requires authentication)
        """
        # Legacy: Keep original filename fields for backward compatibility
        # New: Add full URL fields for production deployment
        data = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'publisher': self.publisher,
            'developer': self.developer,
            'release_date': self.release_date.isoformat() if self.release_date else None,
            'genre': self.genre,

            # Legacy fields (filename only) - kept for backward compatibility
            # 'cover_image': self.cover_image,
            # 'banner_image': self.banner_image,

            # New fields with full URLs (production-ready)
            'cover_image': self._get_file_url(self.cover_image, 'covers'),
            'banner_image': self._get_file_url(self.banner_image, 'covers'),

            # Also include filenames for debugging/reference
            'cover_image_filename': self.cover_image,
            'banner_image_filename': self.banner_image,

            'file_size': self.file_size,
            'version': self.version,
            'price': self.price,
            'is_available': self.is_available,
            'download_count': self.download_count,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

        # Optionally include download URL (for authenticated requests)
        if include_download_url and self.file_path:
            data['download_url'] = self._get_file_url(self.file_path, 'games')

        return data
