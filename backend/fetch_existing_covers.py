"""
Fetch covers for existing games in library that don't have covers yet.
Run this to add covers to games that were added before the cover feature.
"""
from app.models.game import Game
from app.models.user import db
from app.services.scanner import GameScanner
from app import create_app

app = create_app()

with app.app_context():
    # Get all games without covers
    games_without_covers = Game.query.filter(
        (Game.cover_image == None) | (Game.cover_image == '')
    ).all()

    print(f'\nFound {len(games_without_covers)} games without covers\n')

    if len(games_without_covers) == 0:
        print('All games already have covers!')
        exit(0)

    success_count = 0
    failed_count = 0

    for game in games_without_covers:
        print(f'\nProcessing: {game.title}')
        print('-' * 60)

        # Search for cover
        cover_url = GameScanner.search_game_cover(game.title)

        if not cover_url:
            print(f'  [X] No cover found for "{game.title}"')
            failed_count += 1
            continue

        print(f'  [OK] Found cover URL: {cover_url[:60]}...')

        # Download cover
        filename = GameScanner.download_cover_image(cover_url, game.title)

        if not filename:
            print(f'  [X] Failed to download cover')
            failed_count += 1
            continue

        # Update game
        game.cover_image = filename
        db.session.commit()

        print(f'  [OK] Cover saved as: {filename}')
        success_count += 1

    print('\n' + '=' * 60)
    print(f'COMPLETE! Success: {success_count}, Failed: {failed_count}')
    print('=' * 60)

    if success_count > 0:
        print('\nCovers have been added to your games!')
        print('Refresh your GameManager app to see the changes.')
