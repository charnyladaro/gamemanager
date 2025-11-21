from .auth import auth_bp
from .games import games_bp
from .users import users_bp
from .friends import friends_bp
from .game_requests import game_requests_bp

__all__ = ['auth_bp', 'games_bp', 'users_bp', 'friends_bp', 'game_requests_bp']
