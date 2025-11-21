"""
Chunked upload routes for large file uploads with resume capability.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from app.models.game import Game, db
from datetime import datetime
import os
import hashlib
import json

chunked_upload_bp = Blueprint('chunked_upload', __name__, url_prefix='/api/chunked-upload')

# Directory to store temporary chunks
CHUNKS_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'uploads', 'chunks')
os.makedirs(CHUNKS_FOLDER, exist_ok=True)

@chunked_upload_bp.route('/init', methods=['POST'])
@jwt_required()
def init_upload():
    """Initialize a chunked upload session."""
    try:
        data = request.get_json()

        required_fields = ['fileName', 'fileSize', 'totalChunks', 'gameData']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # Generate unique upload ID
        upload_id = hashlib.md5(
            f"{data['fileName']}_{data['fileSize']}_{datetime.utcnow().isoformat()}".encode()
        ).hexdigest()

        # Create upload session directory
        upload_dir = os.path.join(CHUNKS_FOLDER, upload_id)
        os.makedirs(upload_dir, exist_ok=True)

        # Save upload metadata
        metadata = {
            'uploadId': upload_id,
            'fileName': data['fileName'],
            'fileSize': data['fileSize'],
            'totalChunks': data['totalChunks'],
            'uploadedChunks': [],
            'gameData': data['gameData'],
            'userId': get_jwt_identity(),
            'createdAt': datetime.utcnow().isoformat()
        }

        metadata_path = os.path.join(upload_dir, 'metadata.json')
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f)

        return jsonify({
            'uploadId': upload_id,
            'message': 'Upload session initialized'
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@chunked_upload_bp.route('/chunk', methods=['POST'])
@jwt_required()
def upload_chunk():
    """Upload a single chunk."""
    try:
        upload_id = request.form.get('uploadId')
        chunk_index = int(request.form.get('chunkIndex'))
        chunk_file = request.files.get('chunk')

        if not all([upload_id, chunk_index is not None, chunk_file]):
            return jsonify({'error': 'Missing required parameters'}), 400

        upload_dir = os.path.join(CHUNKS_FOLDER, upload_id)
        metadata_path = os.path.join(upload_dir, 'metadata.json')

        if not os.path.exists(metadata_path):
            return jsonify({'error': 'Upload session not found'}), 404

        # Load metadata
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)

        # Check if chunk already uploaded
        if chunk_index in metadata['uploadedChunks']:
            return jsonify({
                'message': 'Chunk already uploaded',
                'chunkIndex': chunk_index,
                'uploadedChunks': metadata['uploadedChunks']
            }), 200

        # Save chunk
        chunk_path = os.path.join(upload_dir, f'chunk_{chunk_index}')
        chunk_file.save(chunk_path)

        # Update metadata
        metadata['uploadedChunks'].append(chunk_index)
        metadata['uploadedChunks'].sort()

        with open(metadata_path, 'w') as f:
            json.dump(metadata, f)

        return jsonify({
            'message': 'Chunk uploaded successfully',
            'chunkIndex': chunk_index,
            'uploadedChunks': metadata['uploadedChunks'],
            'progress': (len(metadata['uploadedChunks']) / metadata['totalChunks']) * 100
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@chunked_upload_bp.route('/status/<upload_id>', methods=['GET'])
@jwt_required()
def get_upload_status(upload_id):
    """Get the status of an upload session."""
    try:
        upload_dir = os.path.join(CHUNKS_FOLDER, upload_id)
        metadata_path = os.path.join(upload_dir, 'metadata.json')

        if not os.path.exists(metadata_path):
            return jsonify({'error': 'Upload session not found'}), 404

        with open(metadata_path, 'r') as f:
            metadata = json.load(f)

        return jsonify({
            'uploadId': upload_id,
            'fileName': metadata['fileName'],
            'fileSize': metadata['fileSize'],
            'totalChunks': metadata['totalChunks'],
            'uploadedChunks': metadata['uploadedChunks'],
            'progress': (len(metadata['uploadedChunks']) / metadata['totalChunks']) * 100
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@chunked_upload_bp.route('/active', methods=['GET'])
@jwt_required()
def get_active_uploads():
    """Get all active (incomplete) upload sessions."""
    try:
        active_uploads = []
        
        if not os.path.exists(CHUNKS_FOLDER):
            return jsonify([]), 200

        # Iterate through all upload directories
        for upload_id in os.listdir(CHUNKS_FOLDER):
            upload_dir = os.path.join(CHUNKS_FOLDER, upload_id)
            metadata_path = os.path.join(upload_dir, 'metadata.json')

            if os.path.isdir(upload_dir) and os.path.exists(metadata_path):
                try:
                    with open(metadata_path, 'r') as f:
                        metadata = json.load(f)
                    
                    # Only include if not fully uploaded (though fully uploaded should be merged/deleted)
                    # But we'll return everything in chunks folder as "active/resumable"
                    active_uploads.append({
                        'id': metadata['uploadId'],
                        'fileName': metadata['fileName'],
                        'fileSize': metadata['fileSize'],
                        'totalChunks': metadata['totalChunks'],
                        'uploadedChunks': len(metadata['uploadedChunks']),
                        'progress': (len(metadata['uploadedChunks']) / metadata['totalChunks']) * 100,
                        'status': 'paused', # Default to paused for recovery
                        'gameData': metadata.get('gameData', {}),
                        'createdAt': metadata.get('createdAt')
                    })
                except Exception as e:
                    print(f"Error reading metadata for {upload_id}: {e}")
                    continue

        return jsonify(active_uploads), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@chunked_upload_bp.route('/complete', methods=['POST'])
@jwt_required()
def complete_upload():
    """Complete the upload by merging all chunks."""
    try:
        data = request.get_json()
        upload_id = data.get('uploadId')
        cover_image_base64 = data.get('coverImage')  # Optional base64 encoded cover

        if not upload_id:
            return jsonify({'error': 'Missing uploadId'}), 400

        upload_dir = os.path.join(CHUNKS_FOLDER, upload_id)
        metadata_path = os.path.join(upload_dir, 'metadata.json')

        if not os.path.exists(metadata_path):
            return jsonify({'error': 'Upload session not found'}), 404

        with open(metadata_path, 'r') as f:
            metadata = json.load(f)

        # Verify all chunks are uploaded
        if len(metadata['uploadedChunks']) != metadata['totalChunks']:
            return jsonify({
                'error': 'Not all chunks uploaded',
                'uploaded': len(metadata['uploadedChunks']),
                'total': metadata['totalChunks']
            }), 400

        # Import config here to avoid circular imports
        from config import Config

        # Merge chunks into final file
        final_filename = secure_filename(metadata['fileName'])
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        final_filename = f"{timestamp}_{final_filename}"
        final_path = os.path.join(Config.GAMES_FOLDER, final_filename)

        with open(final_path, 'wb') as outfile:
            for i in range(metadata['totalChunks']):
                chunk_path = os.path.join(upload_dir, f'chunk_{i}')
                with open(chunk_path, 'rb') as infile:
                    outfile.write(infile.read())

        # Handle cover image if provided
        cover_filename = None
        if cover_image_base64:
            import base64
            cover_data = base64.b64decode(cover_image_base64.split(',')[1] if ',' in cover_image_base64 else cover_image_base64)
            cover_filename = f"{timestamp}_cover.jpg"
            cover_path = os.path.join(Config.COVERS_FOLDER, cover_filename)
            with open(cover_path, 'wb') as f:
                f.write(cover_data)

        # Create game record
        game_data = metadata['gameData']
        game = Game(
            title=game_data.get('title'),
            description=game_data.get('description'),
            publisher=game_data.get('publisher'),
            developer=game_data.get('developer'),
            genre=game_data.get('genre'),
            version=game_data.get('version'),
            file_path=f'/uploads/games/{final_filename}',
            file_size=metadata['fileSize'],
            cover_image=f'/uploads/covers/{cover_filename}' if cover_filename else None,
            is_available=True
        )

        # Parse release date if provided
        if game_data.get('release_date'):
            try:
                game.release_date = datetime.fromisoformat(game_data['release_date']).date()
            except:
                pass

        db.session.add(game)
        db.session.commit()

        # Clean up chunks
        import shutil
        shutil.rmtree(upload_dir)

        return jsonify({
            'message': 'Upload completed successfully',
            'game': game.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@chunked_upload_bp.route('/cancel/<upload_id>', methods=['DELETE'])
@jwt_required()
def cancel_upload(upload_id):
    """Cancel an upload and clean up chunks."""
    try:
        upload_dir = os.path.join(CHUNKS_FOLDER, upload_id)

        if os.path.exists(upload_dir):
            import shutil
            shutil.rmtree(upload_dir)

        return jsonify({'message': 'Upload cancelled successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
