"""
Favorite / Pinning Service — runs as a standalone process.
Communicates with the main program via JSON files:
  Request:  favorites_request.json
  Response: favorites_response.json
"""
import json
import os
import time


REQUEST_FILE  = "favorites_request.json"
RESPONSE_FILE = "favorites_response.json"
DATA_FILE     = "favorites.json"

VALID_TYPES = ["game", "med", "task"]


# --- Core logic ---

def _set_flag(user, item_type, item_id, flag, value, default_entry):
    """Set a boolean flag ('favorite' or 'pinned') on an item, creating it if needed."""
    if item_type not in VALID_TYPES:
        return {"success": False, "error": f"Unsupported item_type '{item_type}'."}
    data = _load()
    items = _get_user_items(data, user)
    existing = _find_item(items, item_type, item_id)
    if existing:
        existing[flag] = value
    else:
        items.append(default_entry)
    _save(data)
    return {"success": True, "status": "ok", "message": f"Item {flag} set to {value}"}


def favorite_item(user, item_type, item_id):
    """Mark an item as favorited (idempotent)."""
    return _set_flag(user, item_type, item_id, "favorite", True,
                     {"item_type": item_type, "item_id": item_id, "favorite": True, "pinned": False})


def unfavorite_item(user, item_type, item_id):
    """Remove favorite status from an item."""
    data = _load()
    if user not in data:
        return {"success": False, "error": "User has no items"}
    item = _find_item(data[user], item_type, item_id)
    if not item:
        return {"success": False, "error": "Item not found"}
    item["favorite"] = False
    _save(data)
    return {"success": True, "status": "ok", "message": "Item unfavorited"}


def get_favorites(user, item_type=None):
    """Return a user's favorited items, optionally filtered by type."""
    data = _load()
    if user not in data:
        return {"success": True, "results": []}
    favorites = [i for i in data[user] if i["favorite"]]
    if item_type:
        favorites = [i for i in favorites if i["item_type"] == item_type]
    return {"success": True, "results": favorites}


def pin_item(user, item_type, item_id):
    """Pin an item so it appears at the top of the list."""
    return _set_flag(user, item_type, item_id, "pinned", True,
                     {"item_type": item_type, "item_id": item_id, "favorite": False, "pinned": True})


def unpin_item(user, item_type, item_id):
    """Remove pinned status from an item."""
    data = _load()
    if user not in data:
        return {"success": False, "error": "User has no items"}
    item = _find_item(data[user], item_type, item_id)
    if not item:
        return {"success": False, "error": "Item not found"}
    item["pinned"] = False
    _save(data)
    return {"success": True, "status": "ok", "message": "Item unpinned"}


def get_items_ordered(user):
    """Return all items for a user with pinned items first."""
    data = _load()
    if user not in data:
        return {"success": True, "results": []}

    ordered = sorted(data[user], key=lambda x: not x["pinned"])
    return {"success": True, "results": ordered}


# --- File helpers ---

def _load():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {}


def _save(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)


def _get_user_items(data, user):
    if user not in data:
        data[user] = []
    return data[user]


def _find_item(items, item_type, item_id):
    for item in items:
        if item["item_type"] == item_type and item["item_id"] == item_id:
            return item
    return None


def handle_request(request):
    """Route an incoming request dict to the correct function and return a response dict."""
    action = request.get('action')
    user      = request.get('user')
    item_type = request.get('item_type')
    item_id   = request.get('item_id')

    if action == 'favorite_item':
        return favorite_item(user, item_type, item_id)

    if action == 'unfavorite_item':
        return unfavorite_item(user, item_type, item_id)

    if action == 'get_favorites':
        return get_favorites(user, item_type=request.get('item_type_filter'))

    if action == 'pin_item':
        return pin_item(user, item_type, item_id)

    if action == 'unpin_item':
        return unpin_item(user, item_type, item_id)

    if action == 'get_items_ordered':
        return get_items_ordered(user)

    return {'success': False, 'error': f"Unknown action: {action}"}


def run():
    """Main polling loop — watches for request file, processes it, writes response."""
    print("Favorite/Pin service running. Waiting for requests...")

    # Create data file if it doesn't exist yet
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w') as f:
            json.dump({}, f)

    while True:
        if os.path.exists(REQUEST_FILE):
            try:
                with open(REQUEST_FILE, 'r') as f:
                    request = json.load(f)

                os.remove(REQUEST_FILE)
                response = handle_request(request)

                with open(RESPONSE_FILE, 'w') as f:
                    json.dump(response, f, indent=2)

                print(f"Favorites: handled '{request.get('action')}' for '{request.get('user')}'")

            except Exception as e:
                error_response = {'success': False, 'error': str(e)}
                with open(RESPONSE_FILE, 'w') as f:
                    json.dump(error_response, f, indent=2)

        time.sleep(0.1)


if __name__ == "__main__":
    run()
