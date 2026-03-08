import sys
import os
sys.path.append(os.getcwd())

from app.db.session import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash

def create_initial_user():
    db = SessionLocal()
    
    # Check if user exists
    user = db.query(User).filter(User.email == "test@example.com").first()
    if user:
        print("User already exists")
        return

    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("password123"),
        name="테스트유저",
        is_active=True,
        is_superuser=True,
        location="서울시 강남구"
    )
    db.add(user)
    db.commit()
    print("Test user created")

if __name__ == "__main__":
    create_initial_user()
