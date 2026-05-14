"""Authentication utilities"""

import bcrypt
from typing import Optional, Tuple
from models.models import User
from utils.storage import StorageManager


class AuthManager:
    """Manage user authentication"""

    def __init__(self, storage: StorageManager):
        self.storage = storage

    def hash_password(self, password: str) -> str:
        """Hash password with bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def verify_password(self, password: str, hash_value: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hash_value.encode('utf-8'))

    def authenticate(self, username: str, password: str) -> Optional[User]:
        """Authenticate user"""
        user = self.storage.get_user_by_username(username)
        if user and user.is_active and self.verify_password(password, user.password_hash):
            return user
        return None

    def create_user(self, username: str, password: str, role: str = "staff", name: str = "") -> Tuple[bool, str]:
        """Create new user"""
        if self.storage.get_user_by_username(username):
            return False, "User already exists"
        
        user = User(
            username=username,
            password_hash=self.hash_password(password),
            role=role,
            name=name
        )
        self.storage.add_user(user)
        return True, "User created successfully"

    def change_password(self, user_id: str, old_password: str, new_password: str) -> Tuple[bool, str]:
        """Change user password"""
        users = self.storage.get_all_users()
        user = None
        for u in users:
            if u.user_id == user_id:
                user = u
                break
        
        if not user:
            return False, "User not found"
        
        if not self.verify_password(old_password, user.password_hash):
            return False, "Old password is incorrect"
        
        user.password_hash = self.hash_password(new_password)
        self.storage.update_user(user)
        return True, "Password changed successfully"
