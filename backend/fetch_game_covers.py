"""
Fetch and save cover images for games that don't have covers.
"""
from app import create_app
from app.models.game import Game
from app.models.user import db
from app.services.scanner import GameScanner

app = create_app()

with app.app_context():
    # Get all games without cover images
    games_without_covers = Game.query.filter(
        (Game.cover_image == None) | (Game.cover_image == '')
    ).all()

    if not games_without_covers:
        print("All games already have cover images!")
    else:
        print(f"Found {len(games_without_covers)} games without covers")
        print("Fetching cover images...\n")

        success_count = 0
        failed_count = 0

        for game in games_without_covers:
            print(f"Processing: {game.title}...")

            # Search for cover image
            cover_url = GameScanner.search_game_cover(game.title)

            if not cover_url:
                print(f"  [X] No cover found for '{game.title}'")
                failed_count += 1
                continue

            # Download and save the cover
            filename = GameScanner.download_cover_image(cover_url, game.title)

            if not filename:
                print(f"  [X] Failed to download cover for '{game.title}'")
                failed_count += 1
                continue

            # Update game with cover info
            game.cover_image = filename
            db.session.commit()

            print(f"  [OK] Cover saved as: {filename}")
            success_count += 1

        print(f"\n{'='*60}")
        print(f"SUMMARY:")
        print(f"  Success: {success_count}")
        print(f"  Failed: {failed_count}")
        print(f"  Total: {len(games_without_covers)}")
        print(f"{'='*60}")
