"""Check scanned games for cover images"""
from app.models.scanned_game import ScannedGame
from app.models.user import db
from app import create_app

app = create_app()

with app.app_context():
    scanned = ScannedGame.query.all()
    print(f'\nTotal scanned games: {len(scanned)}\n')

    if len(scanned) == 0:
        print('No scanned games found!')
        print('Place game files in backend/scanned_games/ folder')
        print('Then use Admin Dashboard to scan them')
    else:
        print('Scanned Game Details:')
        print('-' * 80)
        for sg in scanned:
            print(f'ID: {sg.id}')
            print(f'Filename: {sg.filename}')
            print(f'Suggested Title: {sg.suggested_title}')
            print(f'Cover Image: {sg.cover_image}')
            print(f'Is Processed: {sg.is_processed}')
            print(f'Game ID: {sg.game_id}')
            print('-' * 80)
