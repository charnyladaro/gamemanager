"""
Update game prices - set some games as free and others with low prices
"""
from app import create_app
from app.models.game import Game
from app.models.user import db

app = create_app()

with app.app_context():
    # Get all games
    games = Game.query.all()

    if not games:
        print("No games found in database!")
    else:
        print(f"Found {len(games)} games. Updating prices...\n")

        # Define prices for each game
        # You can customize these prices as needed
        game_prices = {
            'Mortal Kombat Xi Pr': 150.00,  # ₱150
            'Mortal Kombat Komplete Pr': 99.00,  # ₱99
            'Super Mario': 0.00,  # Free
        }

        for game in games:
            if game.title in game_prices:
                old_price = game.price if game.price else 0.00
                new_price = game_prices[game.title]
                game.price = new_price

                status = "FREE" if new_price == 0 else f"P{new_price:.2f}"
                print(f"[OK] {game.title}: {status}")
            else:
                # Default to free if not specified
                game.price = 0.00
                print(f"[OK] {game.title}: FREE (default)")

        db.session.commit()

        print(f"\n{'='*60}")
        print("GAME PRICES UPDATED SUCCESSFULLY!")
        print(f"{'='*60}")
        print("\nCurrent prices:")
        for game in Game.query.all():
            price_display = "FREE" if game.price == 0 or game.price is None else f"P{game.price:.2f}"
            print(f"  - {game.title}: {price_display}")
        print(f"{'='*60}")
