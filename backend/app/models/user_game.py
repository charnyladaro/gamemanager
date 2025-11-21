from datetime import datetime
from app.models.user import db

class UserGame(db.Model):
    __tablename__ = 'user_games'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'), nullable=False)

    # Installation info
    is_installed = db.Column(db.Boolean, default=False)
    install_path = db.Column(db.String(500))
    executable_path = db.Column(db.String(500))

    # Play statistics
    playtime_minutes = db.Column(db.Integer, default=0)
    last_played = db.Column(db.DateTime)
    is_favorite = db.Column(db.Boolean, default=False)

    # Download/Install tracking
    download_progress = db.Column(db.Float, default=0.0)  # 0-100
    is_downloading = db.Column(db.Boolean, default=False)

    # Timestamps
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    installed_at = db.Column(db.DateTime)

    # Relationships
    user = db.relationship('User', back_populates='games')
    game = db.relationship('Game', back_populates='user_games')

    # Unique constraint
    __table_args__ = (db.UniqueConstraint('user_id', 'game_id', name='_user_game_uc'),)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'game_id': self.game_id,
            'game': self.game.to_dict() if self.game else None,
            'is_installed': self.is_installed,
            'install_path': self.install_path,
            'playtime_minutes': self.playtime_minutes,
            'playtime_hours': round(self.playtime_minutes / 60, 1),
            'last_played': self.last_played.isoformat() if self.last_played else None,
            'is_favorite': self.is_favorite,
            'download_progress': self.download_progress,
            'is_downloading': self.is_downloading,
            'added_at': self.added_at.isoformat()
        }
