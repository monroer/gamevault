"""
User Preferences and Configuration Service
Stores and retrieves per-user key/value preferences for any application.
No hardcoded preference keys, callers define their own defaults and valid options.
 
Usage example (GameVault):
    MY_DEFAULTS = {'theme': 'dark', 'default_filter': 'All', 'items_per_page': 20}
    get_preferences('alice', defaults=MY_DEFAULTS)
    update_preference('alice', 'theme', 'light')
 
Usage example (recipe app):
    MY_DEFAULTS = {'servings': 4, 'measurement_unit': 'metric'}
    get_preferences('bob', defaults=MY_DEFAULTS)
"""
import json
import os
 
PREFS_FILE = 'user_preferences.json'
 
 
def get_preferences(username, defaults=None, prefs_file=PREFS_FILE):
    """Load a user's saved preferences, merged with any provided defaults."""
    if not username:
        return {'success': False, 'error': 'Username is required.'}
    saved = _load_all(prefs_file).get(username, {})
    merged = {**(defaults or {}), **saved}
    return {'success': True, 'username': username, 'preferences': merged}
 
 
def update_preference(username, key, value, valid_options=None, prefs_file=PREFS_FILE):
    """
    Save a single preference for a user.
    - valid_options: optional dict mapping keys to lists of allowed values.
      If provided, the value is validated before saving.
    """
    if not username:
        return {'success': False, 'error': 'Username is required.'}
    if valid_options and key in valid_options and value not in valid_options[key]:
        return {'success': False, 'error': f"Invalid value '{value}' for '{key}'. Options: {valid_options[key]}"}
    all_prefs = _load_all(prefs_file)
    if username not in all_prefs:
        all_prefs[username] = {}
    all_prefs[username][key] = value
    _save_all(all_prefs, prefs_file)
    return {'success': True, 'username': username, 'updated': {key: value}}
 
 
def reset_preferences(username, prefs_file=PREFS_FILE):
    """Delete all saved preferences for a user, reverting them to whatever defaults the app provides."""
    if not username:
        return {'success': False, 'error': 'Username is required.'}
    all_prefs = _load_all(prefs_file)
    if username in all_prefs:
        del all_prefs[username]
        _save_all(all_prefs, prefs_file)
    return {'success': True, 'username': username, 'message': 'Preferences reset to defaults.'}
 
 
def delete_preference(username, key, prefs_file=PREFS_FILE):
    """Remove a single saved preference key for a user."""
    if not username:
        return {'success': False, 'error': 'Username is required.'}
    all_prefs = _load_all(prefs_file)
    if username in all_prefs and key in all_prefs[username]:
        del all_prefs[username][key]
        _save_all(all_prefs, prefs_file)
        return {'success': True, 'username': username, 'deleted': key}
    return {'success': False, 'error': f"Preference '{key}' not found for user '{username}'."}
 
 
def _load_all(prefs_file):
    if os.path.exists(prefs_file):
        with open(prefs_file, 'r') as f:
            return json.load(f)
    return {}
 
def _save_all(data, prefs_file):
    with open(prefs_file, 'w') as f:
        json.dump(data, f, indent=2)
