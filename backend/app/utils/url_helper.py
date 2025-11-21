"""
URL Helper Utility for GameManager

Provides centralized URL generation for production deployment with hybrid architecture:
- Backend API hosted on Render.com
- File storage served via Cloudflare Tunnel (local server)
- Static website on GitHub Pages

This utility ensures consistent URL generation across all models and routes.
"""

from flask import current_app, request


def get_storage_base_url():
    """
    Get the base URL for file storage (uploads, covers, static files).

    Returns:
        str: Base URL for storage (e.g., 'https://your-tunnel.trycloudflare.com')
    """
    # Get from config
    storage_url = current_app.config.get('STORAGE_BASE_URL')

    # Fallback to API base URL if storage URL not configured
    if not storage_url:
        storage_url = current_app.config.get('API_BASE_URL')

    # Fallback to request context for local development
    if not storage_url:
        try:
            storage_url = request.host_url.rstrip('/')
        except RuntimeError:
            # Outside request context, use localhost
            storage_url = 'http://localhost:5000'

    return storage_url


def get_api_base_url():
    """
    Get the base URL for API endpoints.

    Returns:
        str: Base URL for API (e.g., 'https://gamemanager-api.onrender.com')
    """
    # Get from config
    api_url = current_app.config.get('API_BASE_URL')

    # Fallback to request context for local development
    if not api_url:
        try:
            api_url = request.host_url.rstrip('/')
        except RuntimeError:
            # Outside request context, use localhost
            api_url = 'http://localhost:5000'

    return api_url


def get_file_url(filename, file_type='uploads'):
    """
    Generate full URL for a file based on deployment configuration.

    Args:
        filename: Filename only (e.g., '12345_cover.jpg')
        file_type: Type of file - determines path structure
            - 'covers': /uploads/covers/{filename}
            - 'games': /uploads/games/{filename}
            - 'scanned_games': /scanned_games/{filename}
            - 'static': /static/{filename}
            - 'uploads': /uploads/{filename}

    Returns:
        str: Full URL to the file, or None if filename is empty

    Examples:
        >>> get_file_url('12345_mario.jpg', 'covers')
        'https://your-tunnel.trycloudflare.com/uploads/covers/12345_mario.jpg'

        >>> get_file_url('gcash_qr.jpg', 'static')
        'https://your-tunnel.trycloudflare.com/static/gcash_qr.jpg'
    """
    if not filename:
        return None

    storage_url = get_storage_base_url()

    # Build path based on file type
    if file_type == 'covers':
        path = f'/uploads/covers/{filename}'
    elif file_type == 'games':
        path = f'/uploads/games/{filename}'
    elif file_type == 'scanned_games':
        path = f'/scanned_games/{filename}'
    elif file_type == 'static':
        path = f'/static/{filename}'
    else:
        path = f'/uploads/{filename}'

    return f'{storage_url}{path}'


def get_api_endpoint_url(endpoint):
    """
    Generate full URL for an API endpoint.

    Args:
        endpoint: API endpoint path (e.g., '/api/games/123/download')

    Returns:
        str: Full URL to the API endpoint

    Examples:
        >>> get_api_endpoint_url('/api/games/123/download')
        'https://gamemanager-api.onrender.com/api/games/123/download'
    """
    api_url = get_api_base_url()
    endpoint = endpoint.lstrip('/')  # Remove leading slash if present
    return f'{api_url}/{endpoint}'


# Legacy compatibility - keep old function names as aliases
# (commented out to force migration to new functions)
# def build_file_url(filename, file_type='uploads'):
#     """Deprecated: Use get_file_url() instead"""
#     return get_file_url(filename, file_type)
