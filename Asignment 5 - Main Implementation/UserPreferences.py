"""
User Preferences and Configuration Service — runs as a standalone process.
Communicates with the main program via JSON files:
  Request:  preferences_request.json
  Response: preferences_response.json
"""
import json
import os
import time


REQUEST_FILE  = "preferences_request.json"
RESPONSE_FILE = "preferences_response.json"
PREFS_FILE    = "user_preferences.json"


def get_preferences(username, defaults=None):
    """Load a user's saved preferences, merged with any provided defaults."""
    if not username:
        return {'success': False, 'error': 'Username is required.'}

    saved = _load_all().get(username, {})
    merged = {**(defaults or {}), **saved}
    return {'success': True, 'username': username, 'preferences': merged}


def update_preference(username, key, value, valid_options=None):
    """Save a single preference value for a user."""
    if not username:
        return {'success': False, 'error': 'Username is required.'}

    if valid_options and key in valid_options and value not in valid_options[key]:
        return {'success': False, 'error': f"Invalid value '{value}' for '{key}'. Options: {valid_options[key]}"}

    all_prefs = _load_all()
    if username not in all_prefs:
        all_prefs[username] = {}

    all_prefs[username][key] = value
    _save_all(all_prefs)
    return {'success': True, 'username': username, 'updated': {key: value}}


def reset_preferences(username):
    """Delete all saved preferences for a user."""
    if not username:
        return {'success': False, 'error': 'Username is required.'}

    all_prefs = _load_all()
    if username in all_prefs:
        del all_prefs[username]
        _save_all(all_prefs)

    return {'success': True, 'username': username, 'message': 'Preferences reset to defaults.'}


def delete_preference(username, key):
    """Remove a single saved preference key for a user."""
    if not username:
        return {'success': False, 'error': 'Username is required.'}

    all_prefs = _load_all()
    if username in all_prefs and key in all_prefs[username]:
        del all_prefs[username][key]
        _save_all(all_prefs)
        return {'success': True, 'username': username, 'deleted': key}

    return {'success': False, 'error': f"Preference '{key}' not found for user '{username}'."}


def _load_all():
    if os.path.exists(PREFS_FILE):
        with open(PREFS_FILE, 'r') as f:
            return json.load(f)
    return {}


def _save_all(data):
    with open(PREFS_FILE, 'w') as f:
        json.dump(data, f, indent=2)


def handle_request(request):
    """Route an incoming request dict to the correct function and return a response dict."""
    action = request.get('action')

    if action == 'get_preferences':
        return get_preferences(
            request['username'],
            defaults=request.get('defaults')
        )

    if action == 'update_preference':
        return update_preference(
            request['username'],
            request['key'],
            request['value'],
            valid_options=request.get('valid_options')
        )

    if action == 'reset_preferences':
        return reset_preferences(request['username'])

    if action == 'delete_preference':
        return delete_preference(request['username'], request['key'])

    return {'success': False, 'error': f"Unknown action: {action}"}


def run():
    """Main polling loop — watches for request file, processes it, writes response."""
    print("User Preferences service running. Waiting for requests...")

    while True:
        if os.path.exists(REQUEST_FILE):
            try:
                with open(REQUEST_FILE, 'r') as f:
                    request = json.load(f)

                os.remove(REQUEST_FILE)
                response = handle_request(request)

                with open(RESPONSE_FILE, 'w') as f:
                    json.dump(response, f, indent=2)

                print(f"Preferences: handled '{request.get('action')}' for '{request.get('username')}'")

            except Exception as e:
                error_response = {'success': False, 'error': str(e)}
                with open(RESPONSE_FILE, 'w') as f:
                    json.dump(error_response, f, indent=2)

        time.sleep(0.1)


if __name__ == "__main__":
    run()
