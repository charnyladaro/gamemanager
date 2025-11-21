"""
Initialize database and create admin user
"""
from app import create_app
from app.models.user import db, User
from werkzeug.security import generate_password_hash
from datetime import datetime

# Create Flask app
app = create_app()

with app.app_context():
    # Create all tables
    print("Creating database tables...")
    db.create_all()
    print("[OK] Database tables created")

    # Check if admin user exists
    admin_user = User.query.filter_by(username='admin').first()

    if not admin_user:
        print("\nCreating default admin user...")
        admin = User(
            username='admin',
            email='admin@gamemanager.local',
            password_hash=generate_password_hash('admin123'),
            display_name='Administrator',
            is_admin=True,
            is_online=False,
            last_seen=datetime.utcnow(),
            created_at=datetime.utcnow()
        )
        db.session.add(admin)
        db.session.commit()

        print("[OK] Admin user created successfully")
        print("\n" + "="*60)
        print("DEFAULT ADMIN CREDENTIALS:")
        print("Username: admin")
        print("Password: admin123")
        print("="*60)
        print("\n[WARNING] IMPORTANT: Please change the admin password after first login!")
    else:
        print("[OK] Admin user already exists")
        # Ensure admin has admin privileges
        if not admin_user.is_admin:
            admin_user.is_admin = True
            db.session.commit()
            print("[OK] Admin privileges granted to existing admin user")

    print("\n[OK] Database initialization completed successfully!")
