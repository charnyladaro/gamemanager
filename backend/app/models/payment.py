from datetime import datetime
from app.models.user import db
from flask import current_app, request

class Payment(db.Model):
    __tablename__ = 'payments'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'), nullable=False)

    # Payment details
    amount = db.Column(db.Float, nullable=False)  # Amount in PHP
    payment_method = db.Column(db.String(50), default='gcash')  # gcash, paymongo, etc.

    # GCash specific fields
    gcash_reference_number = db.Column(db.String(255))  # GCash transaction reference
    gcash_transaction_id = db.Column(db.String(255))  # GCash internal transaction ID

    # Payment status
    status = db.Column(db.String(50), default='pending')  # pending, completed, failed, refunded

    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)

    # Relationships
    user = db.relationship('User', backref='payments')
    game = db.relationship('Game', backref='payments')

    def _get_file_url(self, filepath, file_type='static'):
        """
        Generate full URL for a file based on deployment configuration.

        Args:
            filepath: Filename (e.g., 'gcash_qr.jpg')
            file_type: Type of file ('static' for QR codes)

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

        # Build the file path
        if file_type == 'static':
            path = f'/static/{filepath}'
        else:
            path = f'/{filepath}'

        return f'{storage_base_url}{path}'

    def to_dict(self, include_qr_url=True):
        """
        Convert Payment model to dictionary with optional QR code URL.

        Args:
            include_qr_url: If True, includes the QR code URL for payment
        """
        # Legacy: Simple dictionary without URLs
        # New: Includes QR code URL for production deployment
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'game_id': self.game_id,
            'game_title': self.game.title if self.game else None,
            'amount': self.amount,
            'payment_method': self.payment_method,
            'gcash_reference_number': self.gcash_reference_number,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }

        # Add QR code URL if requested
        if include_qr_url:
            # QR code is served from /api/payments/{id}/qrcode OR directly from static folder
            # For production, provide both options
            api_base_url = current_app.config.get('API_BASE_URL')
            if api_base_url:
                data['qr_code_url_api'] = f'{api_base_url}/api/payments/{self.id}/qrcode'
            else:
                try:
                    data['qr_code_url_api'] = f'{request.host_url.rstrip("/")}/api/payments/{self.id}/qrcode'
                except RuntimeError:
                    data['qr_code_url_api'] = f'http://localhost:5000/api/payments/{self.id}/qrcode'

            # Direct static file URL (for Cloudflare Tunnel deployments)
            data['qr_code_url_direct'] = self._get_file_url('gcash_qr.jpg', 'static')

        return data
