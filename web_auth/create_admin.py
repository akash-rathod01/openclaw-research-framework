"""
Create an admin user for the Flask application
Usage: python create_admin.py
"""
from app import app, db, User
from werkzeug.security import generate_password_hash

def create_admin_user(username="admin", password="admin123"):
    """Create an admin user if one doesn't exist"""
    with app.app_context():
        # Check if user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            print(f"⚠ User '{username}' already exists!")
            if existing_user.role != 'admin':
                existing_user.role = 'admin'
                db.session.commit()
                print(f"✓ Updated '{username}' to admin role")
            return existing_user
        
        # Create new admin user
        hashed_pw = generate_password_hash(password)
        admin_user = User(username=username, password=hashed_pw, role='admin')
        db.session.add(admin_user)
        db.session.commit()
        
        print(f"✓ Admin user created successfully!")
        print(f"  Username: {username}")
        print(f"  Password: {password}")
        print(f"  Role: admin")
        print(f"\n⚠ Please change the password after first login!")
        return admin_user

if __name__ == '__main__':
    import sys
    
    username = sys.argv[1] if len(sys.argv) > 1 else "admin"
    password = sys.argv[2] if len(sys.argv) > 2 else "admin123"
    
    print("Creating admin user...")
    create_admin_user(username, password)
    print("\n✓ You can now login at http://127.0.0.1:5000/login")
