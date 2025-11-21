"""Check if games have cover images in database"""
from app.models.game import Game
from app.models.user import db
from app import create_app

app = create_app()

with app.app_context():
    games = Game.query.all()
    print(f'\nTotal games: {len(games)}\n')

    if len(games) == 0:
        print('No games in database yet!')
    else:
        print('Game Details:')
        print('-' * 80)
        for g in games:
            print(f'ID: {g.id}')
            print(f'Title: {g.title}')
            print(f'Cover Image: {g.cover_image}')
            print(f'File Path: {g.file_path}')
            print('-' * 80)
