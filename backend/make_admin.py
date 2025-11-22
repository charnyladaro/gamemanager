"""
Simple script to make a user an admin
Usage: python make_admin.py <username>
"""
import sys
from app import create_app
from app.models.user import db, User

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python make_admin.py <username>")
        print("Example: python make_admin.py admin")
        sys.exit(1)

    username = sys.argv[1]
    app = create_app()

    with app.app_context():
        user = User.query.filter_by(username=username).first()

        if not user:
            print(f"Error: User '{username}' not found")
            sys.exit(1)

        user.is_admin = True
        db.session.commit()

        print(f"Success! User '{username}' (ID: {user.id}) is now an admin.")
