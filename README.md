# GameManager

A Steam-like gaming platform built with Python Flask and Electron.js. Manage your game library, download games, track playtime, connect with friends, and more!

## Features

- **User Authentication** - Secure login and registration system
- **Game Library** - Manage your personal game collection
- **Game Store** - Browse and add games to your library
- **Download & Install** - Download games from the server
- **Friends System** - Add friends, send/accept friend requests
- **Game Requests** - Request games to be added to the platform
- **Playtime Tracking** - Track how long you've played each game
- **Cross-Platform** - Access from multiple PCs using Cloudflare Tunnel

## Tech Stack

- **Backend**: Python Flask, SQLite, Flask-JWT-Extended
- **Frontend**: Electron.js, HTML/CSS/JavaScript
- **Database**: SQLite
- **Remote Access**: Cloudflare Tunnel

## Project Structure

```
GameManager/
├── backend/
│   ├── app/
│   │   ├── models/          # Database models
│   │   └── routes/          # API endpoints
│   ├── uploads/
│   │   ├── games/           # Game files
│   │   └── covers/          # Game cover images
│   ├── config.py            # Configuration
│   ├── run.py              # Main Flask app
│   └── requirements.txt    # Python dependencies
└── frontend/
    ├── src/
    │   ├── assets/         # Images, icons
    │   ├── components/     # Reusable components
    │   ├── pages/          # HTML pages
    │   └── styles/         # CSS files
    ├── main.js             # Electron main process
    └── package.json        # Node dependencies
```

## Installation & Setup

### Backend Setup

1. **Navigate to backend folder**
   ```bash
   cd backend
   ```

2. **Create virtual environment** (recommended)
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # source venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create environment file**
   - Copy `.env.example` to `.env`
   - Update the secret keys:
   ```
   SECRET_KEY=your-random-secret-key-here
   JWT_SECRET_KEY=your-jwt-secret-key-here
   ```

5. **Run the server**
   ```bash
   python run.py
   ```

   The API will be available at `http://localhost:5000`

### Frontend Setup

1. **Navigate to frontend folder**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Run the application**
   ```bash
   npm start
   ```

   The Electron app will launch automatically.

## Usage

### First Time Setup

1. Start the backend server
2. Launch the Electron app
3. Create an account on the registration page
4. Log in with your credentials

### Adding Games (Admin)

To add games to the platform, you can use tools like Postman or curl:

```bash
curl -X POST http://localhost:5000/api/games \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "title=Game Title" \
  -F "description=Game description" \
  -F "genre=Action" \
  -F "game_file=@path/to/game.exe" \
  -F "cover_image=@path/to/cover.jpg"
```

Or create an admin panel (future enhancement).

### Using the Platform

- **Library**: View and manage your owned games
- **Store**: Browse available games and add them to your library
- **Friends**: Add friends and see who's online
- **Game Requests**: Request games you want added to the platform

## Cloudflare Tunnel Setup

To access your GameManager from other PCs or online:

### Prerequisites
- Cloudflare account (free)
- Domain name (or use Cloudflare's free subdomain)

### Setup Steps

1. **Install Cloudflare Tunnel** (cloudflared)
   - Download from: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/
   - Windows: Download the `.exe` and add to PATH

2. **Authenticate**
   ```bash
   cloudflared tunnel login
   ```

3. **Create a tunnel**
   ```bash
   cloudflared tunnel create gamemanager
   ```

4. **Create configuration file** `config.yml`:
   ```yaml
   tunnel: <TUNNEL-ID>
   credentials-file: C:\Users\<USER>\.cloudflared\<TUNNEL-ID>.json

   ingress:
     - hostname: gamemanager.yourdomain.com
       service: http://localhost:5000
     - service: http_status:404
   ```

5. **Route your tunnel**
   ```bash
   cloudflared tunnel route dns gamemanager gamemanager.yourdomain.com
   ```

6. **Run the tunnel**
   ```bash
   cloudflared tunnel run gamemanager
   ```

7. **Update Frontend API URL**
   - Edit `frontend/src/components/api.js`
   - Change `API_URL` to your Cloudflare tunnel URL:
   ```javascript
   const API_URL = 'https://gamemanager.yourdomain.com/api';
   ```

### Running Tunnel as Service (Windows)

To keep the tunnel running permanently:

```bash
cloudflared service install
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login
- `POST /api/auth/logout` - Logout
- `GET /api/auth/me` - Get current user

### Games
- `GET /api/games` - List all games
- `GET /api/games/<id>` - Get game details
- `POST /api/games` - Create new game
- `GET /api/games/<id>/download` - Download game
- `GET /api/games/<id>/cover` - Get cover image

### User Library
- `GET /api/users/library` - Get user's library
- `POST /api/users/library/<game_id>` - Add game to library
- `DELETE /api/users/library/<game_id>` - Remove from library
- `PATCH /api/users/library/<game_id>` - Update game status

### Friends
- `GET /api/friends` - Get friends list
- `GET /api/friends/requests` - Get friend requests
- `POST /api/friends/add/<user_id>` - Send friend request
- `POST /api/friends/requests/<id>/accept` - Accept request
- `DELETE /api/friends/<id>` - Remove friend

### Game Requests
- `GET /api/game-requests` - Get user's game requests
- `POST /api/game-requests` - Create new request
- `PATCH /api/game-requests/<id>` - Update request
- `DELETE /api/game-requests/<id>` - Delete request

## Database Schema

### Users
- User accounts with authentication
- Online status tracking
- Profile information

### Games
- Game metadata (title, description, publisher, etc.)
- File information (path, size, version)
- Cover and banner images

### UserGames
- User's game library
- Installation status and path
- Playtime tracking
- Download progress

### Friendships
- Friend relationships
- Request status (pending/accepted/rejected)

### GameRequests
- User game requests
- Request status and admin notes

## Development

### Adding New Features

1. **Backend**:
   - Add models in `backend/app/models/`
   - Add routes in `backend/app/routes/`
   - Register blueprints in `backend/app/__init__.py`

2. **Frontend**:
   - Add pages in `frontend/src/pages/`
   - Add components in `frontend/src/components/`
   - Update `main.js` for new IPC handlers

### Database Migrations

The app automatically creates tables on first run. To reset:

```bash
# Stop the server and delete the database file
rm backend/gamemanager.db

# Restart the server to recreate tables
python backend/run.py
```

## Troubleshooting

### Backend won't start
- Check Python version (3.8+)
- Ensure all dependencies are installed
- Check if port 5000 is available

### Frontend won't connect
- Verify backend is running
- Check API_URL in `api.js`
- Check browser console for errors

### Games won't download
- Check file permissions in `backend/uploads/`
- Verify game files exist on server
- Check available disk space

## Future Enhancements

- [ ] Admin dashboard for managing games
- [ ] Achievement system
- [ ] Cloud saves
- [ ] Game updates/patching system
- [ ] Chat system between friends
- [ ] Game reviews and ratings
- [ ] Screenshot gallery
- [ ] Stream integration
- [ ] Controller support
- [ ] Offline mode

## License

MIT License - Feel free to use and modify!

## Support

For issues or questions, please create an issue in the repository.
