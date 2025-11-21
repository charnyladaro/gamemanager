from app import create_app
from config import Config

app = create_app()

if __name__ == '__main__':
    print(f"Starting GameManager API Server on {Config.HOST}:{Config.PORT}")
    print(f"Database: {Config.SQLALCHEMY_DATABASE_URI}")
    app.run(host=Config.HOST, port=Config.PORT, debug=True)


