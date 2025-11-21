"""
Easy script to set individual game prices
Usage: python set_game_price.py
"""
from app import create_app
from app.models.game import Game
from app.models.user import db

app = create_app()

def list_games():
    """List all games with their current prices"""
    games = Game.query.all()
    print("\n" + "="*70)
    print("CURRENT GAMES AND PRICES")
    print("="*70)
    for game in games:
        price_display = "FREE" if game.price == 0 or game.price is None else f"P{game.price:.2f}"
        print(f"[{game.id}] {game.title:<40} {price_display}")
    print("="*70)

def set_price(game_id, price):
    """Set price for a specific game"""
    game = Game.query.get(game_id)
    if not game:
        print(f"Error: Game with ID {game_id} not found!")
        return False

    old_price = game.price if game.price else 0.00
    game.price = price
    db.session.commit()

    price_display = "FREE" if price == 0 else f"P{price:.2f}"
    print(f"\n[OK] Updated '{game.title}' to {price_display}")
    return True

if __name__ == '__main__':
    with app.app_context():
        while True:
            list_games()
            print("\nOptions:")
            print("  1. Set game price")
            print("  2. Exit")

            choice = input("\nEnter your choice (1-2): ").strip()

            if choice == '1':
                try:
                    game_id = int(input("Enter game ID: ").strip())
                    price_input = input("Enter price (0 for free, e.g., 99.00): ").strip()
                    price = float(price_input)

                    if price < 0:
                        print("Error: Price cannot be negative!")
                        continue

                    set_price(game_id, price)
                except ValueError:
                    print("Error: Invalid input! Please enter valid numbers.")
                except Exception as e:
                    print(f"Error: {e}")
            elif choice == '2':
                print("\nGoodbye!")
                break
            else:
                print("Invalid choice! Please try again.")
