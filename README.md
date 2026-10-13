GameVault 

A desktop video-game library manager built in Python/Tkinter, with a microservice-style architecture. The GUI and four backend services run as independent processes that communicate only through JSON request/response files, with no direct function imports between them.


What It Does

Track games you own across statuses (Playing, Completed, Wishlist, On Hold), search your library, mark favorites, view play statistics, and register/log in as a user all from a themeable (dark/light) desktop GUI.

Architecture

The interesting part of this project is the inter-process communication design: rather than importing service modules directly, the main GameVault.py process communicates with each service by writing a request JSON file and polling for a matching response JSON file:

python
IPC_FILES = {
    'search':      ('search_request.json',            'search_response.json'),
    'auth':        ('user_registration_request.json', 'user_registration_response.json'),
    'stats':       ('stats_request.json',              'stats_response.json'),
    'preferences': ('preferences_request.json',        'preferences_response.json'),
    'favorites':   ('favorites_request.json',          'favorites_response.json'),
}

This constraint — no direct imports or function calls between components — forced each service to be independently runnable and testable, and mirrors (at a small scale) how real service-to-service communication works over a message queue or API, just swapping HTTP/queue for the filesystem.

Services
User_Registration.py — registration/login, with passwords salted and hashed via hashlib.sha256 + secrets.token_hex (never stored in plaintext)
Search_Function.py — library search
StatisticsAnalytics.py — play stats aggregation
UserPreferences.py — theme and default-filter settings
favorite_service.py — favorites list management
Tech Stack
Language: Python
GUI: Tkinter/ttk
Data: JSON file storage
Security: Salted SHA-256 password hashing, cryptographically random tokens (secrets module)
Run It
bash
python GameVault.py

No external dependencies beyond the Python standard library.
