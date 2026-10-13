"""
User Registration and Login Service
"""

import json
import os
import hashlib
import secrets

def register_user(username, password, email=""):
    """Register a new user. Returns dict with success/error"""

    # Validate
    if len(password) < 8:
        return {'success': False, 'error': "Password must be at least 8 characters"}
    
    if len(username) < 3:
        return {'success': False, 'error': "Username must be at least 3 characters"}
    
    # Check if duplicate
    if user_exists(username):
        return {'success': False, 'error': "Username already exists"}
    
    # Create and save user
    user = {
        'id': secrets.token_hex(8),
        'username': username,
        'password_hash': hash_password(password),
        'email': email,
    }

    save_user(user)

    return {'success': True, 'user_id': user['id'], 'username': username}

def login_user(username, password):
    """Authenticate and login user. Returns dict with success/error"""

    # Find user
    user = find_user(username)

    if not user or not verify_password(password, user['password_hash']):
        return {'success': False, 'error': "Invalid username or password"}
    
    return {
        'success': True,
        'user_id': user['id'],
        'username': user['username'],
        'token': secrets.token_hex(16)
    }

# Helper functions
def save_user(user):
    """Save user to JSON file"""
    users = load_users()
    users.append(user)
    with open('users.json', 'w') as f:
        json.dump(users, f, indent=2)

def load_users():
    """Load all users from JSON"""
    if os.path.exists('users.json'):
        with open('users.json', 'r') as f:
            return json.load(f)
    return []

def find_user(username):
    """Find user by username"""
    for user in load_users():
        if user['username'] == username:
            return user
    return None

def user_exists(username):
    return find_user(username) is not None

def hash_password(password):
    salt = secrets.token_hex(16)
    pwd_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}${pwd_hash}"

def verify_password(password, stored_hash):
    salt, pwd_hash = stored_hash.split('$')
    return hashlib.sha256((password + salt).encode()).hexdigest() == pwd_hash