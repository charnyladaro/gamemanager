import sqlite3

conn = sqlite3.connect('gamemanager.db')
cursor = conn.cursor()
cursor.execute('SELECT id, title, price, cover_image FROM games')

print('Games in database:')
print('-'*70)
for row in cursor.fetchall():
    price = 'FREE' if row[2] is None or row[2] == 0 else f'P{row[2]:.2f}'
    has_cover = 'Yes' if row[3] else 'No'
    print(f'ID: {row[0]} | {row[1]:<30} | {price:<10} | Cover: {has_cover}')
print('-'*70)
conn.close()
