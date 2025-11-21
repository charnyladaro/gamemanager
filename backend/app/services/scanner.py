import os
import re
import requests
from datetime import datetime
from config import Config
from app.models.user import db
from app.models.scanned_game import ScannedGame
from app.models.game import Game


class GameScanner:
    """Service for scanning and managing auto-detected game files."""
    
    @staticmethod
    def extract_title_from_filename(filename):
        """
        Extract a clean game title from filename.
        
        Examples:
            'MORTAL KOMBAT XI-PR.rar' -> 'Mortal Kombat Xi Pr'
            'The_Witcher_3_GOTY.zip' -> 'The Witcher 3 Goty'
            'Super-Mario-Bros-v1.2.exe' -> 'Super Mario Bros'
        """
        # Remove file extension
        name = os.path.splitext(filename)[0]
        
        # Replace common separators with spaces
        name = re.sub(r'[-_.]', ' ', name)
        
        # Remove common suffixes (version numbers, region codes, etc.)
        # Match patterns like: v1.2, V1.2, (USA), [REPACK], etc.
        name = re.sub(r'\s+v?\d+[\d.]*\s*$', '', name, flags=re.IGNORECASE)
        name = re.sub(r'\s*\([^)]*\)\s*', ' ', name)
        name = re.sub(r'\s*\[[^\]]*\]\s*', ' ', name)
        
        # Remove common tags
        common_tags = ['REPACK', 'CODEX', 'SKIDROW', 'PLAZA', 'CPY', 'GOTY', 'COMPLETE', 'EDITION']
        for tag in common_tags:
            name = re.sub(r'\b' + tag + r'\b', '', name, flags=re.IGNORECASE)
        
        # Clean up multiple spaces
        name = re.sub(r'\s+', ' ', name).strip()
        
        # Apply title case
        name = name.title()
        
        return name
    
    @staticmethod
    def get_file_metadata(filepath):
        """Extract file metadata (size, extension, modification time)."""
        if not os.path.exists(filepath):
            return None
        
        stats = os.stat(filepath)
        _, ext = os.path.splitext(filepath)
        
        return {
            'size': stats.st_size,
            'extension': ext.lower().lstrip('.'),
            'modified': datetime.fromtimestamp(stats.st_mtime)
        }
    
    @staticmethod
    def scan_folder():
        """
        Scan the scanned_games folder and add new files to database.
        Returns count of new files detected.
        """
        scan_folder = Config.SCAN_FOLDER
        
        if not os.path.exists(scan_folder):
            os.makedirs(scan_folder)
            return 0
        
        new_files_count = 0
        
        # Get all files in scan folder
        for filename in os.listdir(scan_folder):
            filepath = os.path.join(scan_folder, filename)
            
            # Skip directories
            if os.path.isdir(filepath):
                continue
            
            # Get relative path for database storage
            relative_path = filename
            
            # Check if file already exists in database
            existing = ScannedGame.query.filter_by(file_path=relative_path).first()
            if existing:
                continue
            
            # Get file metadata
            metadata = GameScanner.get_file_metadata(filepath)
            if not metadata:
                continue
            
            # Extract suggested title
            suggested_title = GameScanner.extract_title_from_filename(filename)
            
            # Create new scanned game entry
            scanned_game = ScannedGame(
                filename=filename,
                file_path=relative_path,
                file_size=metadata['size'],
                file_extension=metadata['extension'],
                suggested_title=suggested_title
            )
            
            db.session.add(scanned_game)
            new_files_count += 1
        
        if new_files_count > 0:
            db.session.commit()
        
        return new_files_count
    
    @staticmethod
    def sync_scanned_games():
        """
        Remove database entries for files that no longer exist.
        Returns count of removed entries.
        """
        scan_folder = Config.SCAN_FOLDER
        removed_count = 0
        
        # Get all unprocessed scanned games
        scanned_games = ScannedGame.query.filter_by(is_processed=False).all()
        
        for scanned_game in scanned_games:
            filepath = os.path.join(scan_folder, scanned_game.file_path)
            
            if not os.path.exists(filepath):
                db.session.delete(scanned_game)
                removed_count += 1
        
        if removed_count > 0:
            db.session.commit()
        
        return removed_count
    
    @staticmethod
    def move_to_library(scanned_game_id, game_metadata):
        """
        Move scanned game file to library and create Game entry.
        
        Args:
            scanned_game_id: ID of the ScannedGame
            game_metadata: Dict with game information (title, description, etc.)
        
        Returns:
            Created Game object
        """
        scanned_game = ScannedGame.query.get(scanned_game_id)
        if not scanned_game:
            raise ValueError('Scanned game not found')
        
        if scanned_game.is_processed:
            raise ValueError('Game already processed')
        
        # Source and destination paths
        source_path = os.path.join(Config.SCAN_FOLDER, scanned_game.file_path)
        
        if not os.path.exists(source_path):
            raise ValueError('Source file not found')
        
        # Create unique filename for destination
        timestamp = datetime.utcnow().timestamp()
        unique_filename = f"{timestamp}_{scanned_game.filename}"
        dest_path = os.path.join(Config.GAMES_FOLDER, unique_filename)
        
        # Ensure games folder exists
        os.makedirs(Config.GAMES_FOLDER, exist_ok=True)
        
        # Move file
        import shutil
        shutil.move(source_path, dest_path)
        
        # Create Game entry
        game = Game(
            title=game_metadata.get('title', scanned_game.suggested_title),
            description=game_metadata.get('description'),
            publisher=game_metadata.get('publisher'),
            developer=game_metadata.get('developer'),
            genre=game_metadata.get('genre'),
            version=game_metadata.get('version'),
            file_path=unique_filename,
            file_size=scanned_game.file_size,
            cover_image=scanned_game.cover_image,  # Copy cover from scanned game
            is_available=game_metadata.get('is_available', True)
        )
        
        # Handle release date
        if game_metadata.get('release_date'):
            try:
                game.release_date = datetime.strptime(game_metadata['release_date'], '%Y-%m-%d').date()
            except:
                pass
        
        db.session.add(game)
        db.session.flush()  # Get the game ID
        
        # Mark scanned game as processed
        scanned_game.is_processed = True
        scanned_game.processed_at = datetime.utcnow()
        scanned_game.game_id = game.id
        
        db.session.commit()

        return game

    @staticmethod
    def search_game_cover(title):
        """
        Search for game cover image using RAWG API.

        Args:
            title: Game title to search for

        Returns:
            URL of the cover image or None if not found
        """
        if not title:
            return None

        try:
            # RAWG API endpoint
            url = f"{Config.RAWG_API_URL}/games"
            params = {
                'search': title,
                'page_size': 1
            }

            # Add API key if available
            if Config.RAWG_API_KEY:
                params['key'] = Config.RAWG_API_KEY

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            if data.get('results') and len(data['results']) > 0:
                game = data['results'][0]
                # Return the background image (best quality)
                return game.get('background_image') or game.get('image_background')

            return None

        except Exception as e:
            print(f"Error searching for game cover: {e}")
            return None

    @staticmethod
    def download_cover_image(image_url, game_title):
        """
        Download cover image from URL and save to covers folder.

        Args:
            image_url: URL of the image to download
            game_title: Game title (used for filename)

        Returns:
            Filename of saved image or None if failed
        """
        if not image_url:
            return None

        try:
            # Ensure covers folder exists
            os.makedirs(Config.COVERS_FOLDER, exist_ok=True)

            # Download image
            response = requests.get(image_url, timeout=15, stream=True)
            response.raise_for_status()

            # Get file extension from URL or content-type
            ext = 'jpg'
            content_type = response.headers.get('content-type', '')
            if 'png' in content_type:
                ext = 'png'
            elif 'webp' in content_type:
                ext = 'webp'

            # Create unique filename
            timestamp = datetime.utcnow().timestamp()
            safe_title = re.sub(r'[^\w\s-]', '', game_title)[:50]
            safe_title = re.sub(r'[-\s]+', '_', safe_title)
            filename = f"{timestamp}_cover_{safe_title}.{ext}"

            filepath = os.path.join(Config.COVERS_FOLDER, filename)

            # Save image
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            return filename

        except Exception as e:
            print(f"Error downloading cover image: {e}")
            return None

    @staticmethod
    def fetch_and_save_cover(scanned_game_id):
        """
        Fetch cover image for a scanned game and update the database.

        Args:
            scanned_game_id: ID of the ScannedGame

        Returns:
            Dict with cover image info or error message
        """
        scanned_game = ScannedGame.query.get(scanned_game_id)
        if not scanned_game:
            return {'error': 'Scanned game not found'}

        # Search for cover image
        cover_url = GameScanner.search_game_cover(scanned_game.suggested_title)

        if not cover_url:
            return {'error': 'No cover image found for this game', 'searched_title': scanned_game.suggested_title}

        # Download and save the cover
        filename = GameScanner.download_cover_image(cover_url, scanned_game.suggested_title)

        if not filename:
            return {'error': 'Failed to download cover image'}

        # Update scanned game with cover info
        scanned_game.cover_image = filename
        db.session.commit()

        return {
            'success': True,
            'cover_image': filename,
            'cover_url': cover_url
        }
