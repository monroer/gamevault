import json
import os
from threading import Lock


class FavoritePinService:
    """
    Microservice for handling favorites and pinned items.

    Each user has their own list of items.
    Items can be:
    - favorited
    - pinned
    """

    def __init__(self, file_name="favorites.json"):
        self.file_name = file_name
        self.lock = Lock()

        # allowed item types for this project
        self.valid_types = ["game", "med", "task"]

        # create file if it does not exist yet
        if not os.path.exists(self.file_name):
            with open(self.file_name, "w") as f:
                json.dump({}, f)

    # -----------------------------
    # helper functions
    # -----------------------------

    def _load(self):
        with open(self.file_name, "r") as f:
            return json.load(f)

    def _save(self, data):
        with open(self.file_name, "w") as f:
            json.dump(data, f, indent=2)

    def _validate_type(self, item_type):
        if item_type not in self.valid_types:
            raise ValueError(
                f"Unsupported item_type '{item_type}'. "
                f"Allowed types: {self.valid_types}"
            )

    def _get_user_items(self, data, user):
        if user not in data:
            data[user] = []
        return data[user]

    def _find_item(self, items, item_type, item_id):
        for item in items:
            if item["item_type"] == item_type and item["item_id"] == item_id:
                return item
        return None

    # -----------------------------
    # FAVORITES
    # -----------------------------

    def favorite_item(self, user, item_type, item_id):
        """Favorite an item (idempotent)."""

        self._validate_type(item_type)

        with self.lock:
            data = self._load()
            items = self._get_user_items(data, user)

            existing = self._find_item(items, item_type, item_id)

            # if item already exists
            if existing:
                if existing["favorite"]:
                    return {
                        "status": "ok",
                        "message": "Item already favorited"
                    }

                existing["favorite"] = True
                self._save(data)

                return {
                    "status": "ok",
                    "message": "Item favorited"
                }

            # create new entry
            new_item = {
                "item_type": item_type,
                "item_id": item_id,
                "favorite": True,
                "pinned": False
            }

            items.append(new_item)
            self._save(data)

            return {
                "status": "ok",
                "message": "Item favorited"
            }

    def get_favorites(self, user, item_type=None):
        """Return a user's favorites (optionally filtered)."""

        with self.lock:
            data = self._load()

        if user not in data:
            return []

        favorites = [i for i in data[user] if i["favorite"]]

        if item_type:
            favorites = [i for i in favorites if i["item_type"] == item_type]

        return favorites

    # -----------------------------
    # PINNING
    # -----------------------------

    def pin_item(self, user, item_type, item_id):
        """Pin an item so it shows at the top."""

        self._validate_type(item_type)

        with self.lock:
            data = self._load()
            items = self._get_user_items(data, user)

            existing = self._find_item(items, item_type, item_id)

            if existing:
                existing["pinned"] = True
                self._save(data)

                return {"status": "ok", "message": "Item pinned"}

            # create item if not existing
            items.append({
                "item_type": item_type,
                "item_id": item_id,
                "favorite": False,
                "pinned": True
            })

            self._save(data)

            return {"status": "ok", "message": "Item pinned"}

    def unpin_item(self, user, item_type, item_id):

        with self.lock:
            data = self._load()

            if user not in data:
                return {"status": "error", "message": "User has no items"}

            item = self._find_item(data[user], item_type, item_id)

            if not item:
                return {"status": "error", "message": "Item not found"}

            item["pinned"] = False
            self._save(data)

            return {"status": "ok", "message": "Item unpinned"}

    # -----------------------------
    # ORDERED LIST
    # -----------------------------

    def get_items_ordered(self, user):
        """
        Return items with pinned items first.
        Python sort is stable so order within groups stays the same.
        """

        with self.lock:
            data = self._load()

        if user not in data:
            return []

        items = data[user]

        # pinned items first
        ordered = sorted(items, key=lambda x: not x["pinned"])

        return ordered
