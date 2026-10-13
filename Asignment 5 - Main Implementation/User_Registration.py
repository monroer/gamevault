"""
User Registration and Login Service — runs as a standalone process.
Communicates with the main program via JSON files:
  Request:  user_registration_request.json
  Response: user_registration_response.json
"""
import json
import os
import time
import hashlib
import secrets


REQUEST_FILE  = "user_registration_request.json"
RESPONSE_FILE = "user_registration_response.json"
USERS_FILE    = "users.json"


def register_user(username, password, email=""):
    """Register a new user. Returns dict with success/error."""
    if len(username) < 3:
        return {'success': False, 'error': "Username must be at least 3 characters"}

    if len(password) < 8:
        return {'success': False, 'error': "Password must be at least 8 characters"}

    if _user_exists(username):
        return {'success': False, 'error': "Username already exists"}

    user = {
        'id': secrets.token_hex(8),
        'username': username,
        'password_hash': _hash_password(password),
        'email': email,
    }

    _save_user(user)
    return {'success': True, 'user_id': user['id'], 'username': username}


def login_user(username, password):
    """Authenticate a user. Returns dict with success/error."""
    user = _find_user(username)

    if not user or not _verify_password(password, user['password_hash']):
        return {'success': False, 'error': "Invalid username or password"}

    return {
        'success': True,
        'user_id': user['id'],
        'username': user['username'],
        'token': secrets.token_hex(16)
    }


# --- Helpers ---

def _load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return []


def _save_user(user):
    users = _load_users()
    users.append(user)
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)


def _find_user(username):
    for user in _load_users():
        if user['username'] == username:
            return user
    return None


def _user_exists(username):
    return _find_user(username) is not None


def _hash_password(password):
    salt = secrets.token_hex(16)
    pwd_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}${pwd_hash}"


def _verify_password(password, stored_hash):
    salt, pwd_hash = stored_hash.split('$')
    return hashlib.sha256((password + salt).encode()).hexdigest() == pwd_hash


def handle_request(request):
    """Route an incoming request dict to the correct function and return a response dict."""
    action = request.get('action')

    if action == 'register':
        return register_user(
            request['username'],
            request['password'],
            request.get('email', '')
        )

    if action == 'login':
        return login_user(request['username'], request['password'])

    return {'success': False, 'error': f"Unknown action: {action}"}


def run():
    """Main polling loop — watches for request file, processes it, writes response."""
    print("User Registration service running. Waiting for requests...")

    while True:
        if os.path.exists(REQUEST_FILE):
            try:
                with open(REQUEST_FILE, 'r') as f:
                    request = json.load(f)

                os.remove(REQUEST_FILE)
                response = handle_request(request)

                with open(RESPONSE_FILE, 'w') as f:
                    json.dump(response, f, indent=2)

                print(f"User Registration: handled '{request.get('action')}' for '{request.get('username')}'")

            except Exception as e:
                error_response = {'success': False, 'error': str(e)}
                with open(RESPONSE_FILE, 'w') as f:
                    json.dump(error_response, f, indent=2)

        time.sleep(0.1)


if __name__ == "__main__":
    run()
