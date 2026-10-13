"""
CS361 - GameVault: Video Game Library Manager
Track your games. Discover new favorites.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime
import time

import User_Registration
import Search_Function
import StatisticsAnalytics
import UserPreferences
from favorite_service import FavoritePinService


PREF_DEFAULTS = {
    'default_filter': 'All',
    'theme': 'dark',
}
PREF_VALID = {
    'default_filter': ['All', 'Playing', 'Completed', 'Wishlist', 'On Hold'],
    'theme': ['dark', 'light']
}

THEMES = {
    'dark': {
        'bg':      '#1a1a2e',
        'header':  '#16213e',
        'accent':  '#e94560',
        'nav':     '#0f3460',
        'fg':      'white',
        'muted':   '#94a3b8',
    },
    'light': {
        'bg':      '#f0f4f8',
        'header':  '#dce3ed',
        'accent':  '#e94560',
        'nav':     '#3a6491',
        'fg':      '#1a1a2e',
        'muted':   '#555e6e',
    },
}

class GameVaultApp:
    def __init__(self, root):
        self.root = root
        self.root.title("GameVault - Video Game Library Manager")
        self.root.geometry("1000x700")
        self.root.configure(bg="#1a1a2e")

        # Data storage
        self.games_file = "games.json"
        self.games = self.load_games()
        self.current_user = None
        self.current_page = None
        self.current_search_results = None # Track active search

        # Microservice instances
        self.favorites = FavoritePinService()

        # Theme defaults to dark until user prefs are loaded after login
        self.theme = THEMES['dark']
        self.root.configure(bg=self.theme['bg'])

        # Track load time for performance quality attribute
        self.start_time = time.time()

        # Start with login page
        self.show_login_page()

        # Log load time
        load_time = time.time() - self.start_time
        print(f"GameVault loaded in {load_time:.3f} seconds")

    #----------------------------------
    # Theme Helper
    #----------------------------------

    def load_user_prefs(self):
        """Load preferences for the current user and apply theme"""
        result = UserPreferences.get_preferences(self.current_user, defaults=PREF_DEFAULTS)
        if result['success']:
            prefs = result['preferences']
            theme_name = prefs.get('theme', 'dark')
            self.theme = THEMES.get(theme_name, THEMES['dark'])
            self.root.configure(bg=self.theme['bg'])
            return prefs
        return dict(PREF_DEFAULTS)

    #---------------------------------
    # Window helper
    #---------------------------------

    def clear_window(self):
        """Clear all widgets from window"""
        for widget in self.root.winfo_children():
            widget.destroy()

    #--------------------------------
    # Login / Startup
    #--------------------------------

    def show_login_page(self):
        """IH#1: Welcome/Login page explaining benefits"""
        self.clear_window()
        self.current_page = "Login"
        t = self.theme
 
        container = tk.Frame(self.root, bg=t['bg'])
        container.pack(expand=True)
 
        tk.Label(
            container,
            text="🎮GameVault",
            font=("Arial", 36, "bold"),
            bg=t['bg'],
            fg=t['accent']
        ).pack(pady=(20, 10))
 
        # IH#1: Tagline explaining benefits
        tk.Label(
            container,
            text="Track your games. Discover new favorites.",
            font=("Arial", 16, "italic"),
            bg=t['bg'],
            fg=t['nav']
        ).pack(pady=(0, 5))
 
        # IH#2: Communicate costs - assessibility note
        tk.Label(
            container,
            text="Getting started takes about 2 minutes",
            font=("Arial", 10),
            bg=t['bg'],
            fg=t['muted']
        ).pack(pady=(0, 30))
 
        form_frame = tk.Frame(container, bg=t['header'], padx=40, pady=30)
        form_frame.pack()
 
        tk.Label(form_frame, text="Username:", bg=t['header'], fg=t['fg'], font=("Arial", 11)).grid(row=0, column=0, sticky=tk.W, padx=5)
        self.username_entry = tk.Entry(form_frame, width=30, font=("Arial", 11))
        self.username_entry.grid(row=0, column=1, pady=5, padx=(10, 0))
 
        tk.Label(form_frame, text="Password:", bg=t['header'], fg=t['fg'], font=("Arial", 11)).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.password_entry = tk.Entry(form_frame, width=30, show="*", font=("Arial", 11))
        self.password_entry.grid(row=1, column=1, pady=5, padx=(10, 0))
 
        # IH#2: Communicate password requirements
        tk.Label(
            form_frame,
            text="Password must be at least 8 characters",
            bg=t['header'],
            fg=t['muted'],
            font=("Arial", 9, "italic")
        ).grid(row=2, column=1, sticky=tk.W, pady=(0, 10))
 
        # IH#6 and IH#7: Clear path and multiple ways
        login_button = tk.Button(
            form_frame,
            text="Login (or press Enter)",
            command=self.login,
            bg=t['accent'],
            fg="white",
            font=("Arial", 12, "bold"),
            padx=20, pady=10, cursor="hand2"
        )
        login_button.grid(row=3, column=0, columnspan=2, pady=(10, 5))
 
        # IH#7: Alternative method - Enter key
        self.username_entry.bind("<Return>", lambda e: self.login())
        self.password_entry.bind("<Return>", lambda e: self.login())
 
        tk.Button(
            form_frame,
            text="Sign Up",
            command=self.show_signup_page,
            bg=t['nav'],
            fg="white",
            font=("Arial", 11),
            padx=20, pady=8, cursor="hand2"
        ).grid(row=4, column=0, columnspan=2)

    def login(self):
        """User story #1: login functionality"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
 
        # IH#2: Validate and communicate requirements
        if not username or not password:
            messagebox.showwarning("Required Fields", "Please enter both username and password.")
            return
 
        result = User_Registration.login_user(username, password)
 
        if result['success']:
            self.current_user = result['username']
            self.load_user_prefs()  # Microservice 9: load saved preferences on login
            self.show_dashboard()
        else:
            messagebox.showerror("Error", result['error'])
 
    def show_signup_page(self):
        """Registration page using User_Registration microservice"""
        self.clear_window()
        self.current_page = "Signup"
        t = self.theme
 
        container = tk.Frame(self.root, bg=t['bg'])
        container.pack(expand=True)
 
        tk.Label(
            container,
            text="Create Account",
            font=("Arial", 28, "bold"),
            bg=t['bg'],
            fg=t['accent']
        ).pack(pady=(20, 30))
 
        form_frame = tk.Frame(container, bg=t['header'], padx=40, pady=30)
        form_frame.pack()
 
        tk.Label(form_frame, text="Username:", bg=t['header'], fg=t['fg'], font=("Arial", 11)).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.signup_username = tk.Entry(form_frame, width=30, font=("Arial", 11))
        self.signup_username.grid(row=0, column=1, pady=5, padx=(10, 0))
 
        tk.Label(form_frame, text="Email (optional):", bg=t['header'], fg=t['fg'], font=("Arial", 11)).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.signup_email = tk.Entry(form_frame, width=30, font=("Arial", 11))
        self.signup_email.grid(row=1, column=1, pady=5, padx=(10, 0))
 
        tk.Label(form_frame, text="Password:", bg=t['header'], fg=t['fg'], font=("Arial", 11)).grid(row=2, column=0, sticky=tk.W, pady=5)
        self.signup_password = tk.Entry(form_frame, width=30, show="*", font=("Arial", 11))
        self.signup_password.grid(row=2, column=1, pady=5, padx=(10, 0))
 
        tk.Label(form_frame, text="Password must be 8+ characters", bg=t['header'], fg=t['muted'], font=("Arial", 9, "italic")).grid(row=3, column=1, sticky=tk.W)
 
        tk.Button(
            form_frame,
            text="Create Account",
            command=self.signup,
            bg=t['accent'], fg="white",
            font=("Arial", 12, "bold"),
            padx=20, pady=10, cursor="hand2"
        ).grid(row=4, column=0, columnspan=2, pady=(20, 5))
 
        tk.Button(
            form_frame,
            text="Back to Login",
            command=self.show_login_page,
            bg=t['nav'], fg="white",
            font=("Arial", 11),
            padx=20, pady=8, cursor="hand2"
        ).grid(row=5, column=0, columnspan=2)
 
    def signup(self):
        """Handle signup using User_Registration microservice"""
        username = self.signup_username.get().strip()
        email = self.signup_email.get().strip()
        password = self.signup_password.get().strip()
 
        if not username or not password:
            messagebox.showwarning("Required Fields", "Username and password are required.")
            return
 
        result = User_Registration.register_user(username, password, email)
 
        if result['success']:
            messagebox.showinfo("Success", f"Account created! Welcome, {result['username']}!")
            self.current_user = result['username']
            self.load_user_prefs()  # Microservice 9: load preferences for new user
            self.show_dashboard()
        else:
            messagebox.showerror("Registration Failed", result['error'])

    #------------------------------------
    # Dashboard
    #------------------------------------

    def show_dashboard(self):
        """Dashboard/Library Home page"""
        self.clear_window()
        self.current_page = "dashboard"
        t = self.theme
 
        # Load user's saved default filter (Microservice 9: User Preferences)
        prefs = self.load_user_prefs()
        saved_filter = prefs.get('default_filter', 'All')
 
        # Header with navigation (IH#4: Familiar features avaliable)
        header = tk.Frame(self.root, bg=t['header'], height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
 
        tk.Label(header, text="🎮GameVault", font=("Arial", 16, "bold"), bg=t['header'], fg=t['fg']).pack(side=tk.LEFT, padx=20)
 
        nav_frame = tk.Frame(header, bg=t['header'])
        nav_frame.pack(side=tk.LEFT, padx=20)
 
        # Navigation buttons (IH#4: Keep familiar features avaliable)
        tk.Button(nav_frame, text="Home", command=self.show_dashboard, bg=t['nav'], fg="white", font=("Arial", 10), padx=15, pady=5).pack(side=tk.LEFT, padx=5)
        # Stats button — Microservice 7: Statistics/Analytics
        tk.Button(nav_frame, text="📊 Stats", command=self.show_stats_page, bg=t['nav'], fg="white", font=("Arial", 10), padx=15, pady=5).pack(side=tk.LEFT, padx=5)
        # Preferences button — Microservice 9: User Preferences
        tk.Button(nav_frame, text="⚙ Preferences", command=self.show_preferences_page, bg=t['nav'], fg="white", font=("Arial", 10), padx=15, pady=5).pack(side=tk.LEFT, padx=5)
 
        # IH#4: Search in familiar location (top right)
        search_frame = tk.Frame(header, bg=t['header'])
        search_frame.pack(side=tk.RIGHT, padx=20)
 
        tk.Label(search_frame, text="Search:", bg=t['header'], fg=t['fg']).pack(side=tk.LEFT)
        self.search_entry = tk.Entry(search_frame, width=20)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(search_frame, text="Search🔍", command=self.search_games, bg=t['nav'], fg="white").pack(side=tk.LEFT)
        tk.Button(search_frame, text="Clear", command=self.clear_search, bg=t['nav'], fg="white").pack(side=tk.LEFT, padx=(5, 0))
 
        # Main content area
        main_frame = tk.Frame(self.root, bg=t['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
 
        tk.Label(main_frame, text="My Game Library", font=("Arial", 24, "bold"), bg=t['bg'], fg=t['fg']).pack(pady=(0, 10))
 
        # Controls row
        controls_frame = tk.Frame(main_frame, bg=t['bg'])
        controls_frame.pack(fill=tk.X, pady=(0, 15))
 
        # Filter controls (IH#3: Let users decide what to see)
        tk.Label(controls_frame, text="Filter by status:", bg=t['bg'], fg=t['fg'], font=("Arial", 10)).pack(side=tk.LEFT, padx=(0, 10))
 
        self.filter_var = tk.StringVar(value=saved_filter)
        for option in ["All", "Playing", "Completed", "Wishlist", "⭐ Favorites"]:
            tk.Radiobutton(
                controls_frame, text=option,
                variable=self.filter_var, value=option,
                command=self.refresh_game_list,
                bg=t['bg'], fg=t['fg'], selectcolor=t['nav'],
                font=("Arial", 9)
            ).pack(side=tk.LEFT, padx=5)
 
        # Add Game Button (IH#6: Make next step clear)
        tk.Button(
            controls_frame, text="+ Add Game",
            command=self.show_add_game_page,
            bg=t['accent'], fg="white",
            font=("Arial", 11, "bold"),
            padx=15, pady=5, cursor="hand2"
        ).pack(side=tk.RIGHT)
 
        # Game list with scrollbar
        list_frame = tk.Frame(main_frame, bg=t['bg'])
        list_frame.pack(fill=tk.BOTH, expand=True)
 
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
 
        self.game_listbox = tk.Listbox(
            list_frame, bg=t['header'], fg=t['fg'],
            font=("Arial", 11), selectbackground=t['accent'],
            yscrollcommand=scrollbar.set, height=15
        )
        self.game_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.game_listbox.yview)
 
        # Double click to view details
        self.game_listbox.bind("<Double-Button-1>", lambda e: self.view_game_details())
 
        # Bottom info bar
        self.info_label = tk.Label(
            self.root, text="",
            bg=t['header'], fg=t['fg'],
            font=("Arial", 10), anchor=tk.W, padx=10, pady=5
        )
        self.info_label.pack(side=tk.BOTTOM, fill=tk.X)
 
        self.refresh_game_list()

    #----------------------------
    # Add Game
    #----------------------------

    def show_add_game_page(self):
        """Add Game page - User story 2"""
        self.clear_window()
        self.current_page = "add_game"

        # Header (IH#4: Consistent navigation)
        self.create_header()

        # Main content
        main_frame = tk.Frame(self.root, bg="#1a1a2e")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=20)

        # Page title
        title_label = tk.Label(
            main_frame,
            text="Add New Game",
            font=("Arial", 24, "bold"),
            bg="#1a1a2e",
            fg="#94a3b8"
        )
        title_label.pack(pady=(0, 20))

        # IH#2: Communicate required fields
        req_label = tk.Label(
            main_frame,
            text="* Title and Platform required",
            font=("Arial", 10, "italic"),
            bg="#1a1a2e",
            fg="#94a3b8"
        )
        req_label.pack(pady=(0, 15))

        # IH#6: Form with clear top to bottom path
        form_frame = tk.Frame(main_frame, bg="#16213e", padx=30, pady=25)
        form_frame.pack()

        # Game Title *
        tk.Label(
            form_frame,
            text="Game Title: *",
            bg="#16213e",
            fg="white",
            font=("Arial", 11)
        ).grid(row=0, column=0, sticky=tk.W, pady=8)

        self.title_entry = tk.Entry(form_frame, width=40, font=("Arial", 11))
        self.title_entry.grid(row=0, column=1, pady=8, padx=(10, 0))

        # Platform * (IH#4: Familiar dropdown)
        tk.Label(
            form_frame,
            text="Platform: *",
            bg="#16213e",
            fg="white",
            font=("Arial", 11)
        ).grid(row=1, column=0, sticky=tk.W, pady=8)

        self.platform_var = tk.StringVar()
        platform_dropdown = ttk.Combobox(
            form_frame,
            textvariable=self.platform_var,
            values=["PC", "Playstation", "Xbox", "Nintendo Switch", "Mobile"],
            width=37,
            font=("Arial", 11),
            state="readonly"
        )
        platform_dropdown.grid(row=1, column=1, pady=8, padx=(10, 0))
        platform_dropdown.set("PC")

        # Completion Status
        tk.Label(
            form_frame,
            text="Completion Status:",
            bg="#16213e",
            fg="white",
            font=("Arial", 11)
        ).grid(row=2, column=0, sticky=tk.W, pady=8)

        self.status_var = tk.StringVar()
        status_dropdown = ttk.Combobox(
            form_frame,
            textvariable=self.status_var,
            values=["Wishlist", "Playing", "Completed", "On Hold"],
            width=37,
            font=("Arial", 11),
            state="readonly"
        )
        status_dropdown.grid(row=2, column=1, pady=8, padx=(10, 0))
        status_dropdown.set("Wishlist")

        # Playtime
        tk.Label(
            form_frame,
            text="Playtime (hours):",
            bg="#16213e",
            fg="white",
            font=("Arial", 11)
        ).grid(row=3, column=0, sticky=tk.W, pady=8)

        self.playtime_entry = tk.Entry(form_frame, width=40, font=("Arial", 11))
        self.playtime_entry.insert(0, "0")
        self.playtime_entry.grid(row=3, column=1, pady=8, padx=(10, 0))

        # Personal Rating
        tk.Label(
            form_frame,
            text="Personal Rating (1-10):",
            bg="#16213e",
            fg="white",
            font=("Arial", 11)
        ).grid(row=4, column=0, sticky=tk.W, pady=8)
        
        self.rating_entry = tk.Entry(form_frame, width=40, font=("Arial", 11))
        self.rating_entry.grid(row=4, column=1, pady=8, padx=(10, 0))

        # IH#6: Clear buttons at bottom
        button_frame = tk.Frame(form_frame, bg="#16213e")
        button_frame.grid(row=5, column=0, columnspan=2, pady=(20, 0))

        save_btn = tk.Button(
            button_frame,
            text="Save Game",
            command=self.save_game,
            bg="#e94560",
            fg="white",
            font=("Arial", 12, "bold"),
            padx=30,
            pady=10,
            cursor="hand2"
        )
        save_btn.pack(side=tk.LEFT, padx=10)

        # IH#5: Cancel button for backtracking
        cancel_btn = tk.Button(
            button_frame,
            text="Cancel",
            command=self.cancel_with_confirmation,
            bg="#0f3460",
            fg="white",
            font=("Arial", 12),
            padx=30,
            pady=10,
            cursor="hand2"
        )
        cancel_btn.pack(side=tk.LEFT, padx=10)

    def save_game(self):
        """Save new game - User Story #2 completion"""
        title = self.title_entry.get().strip()
        platform = self.platform_var.get()
        status = self.status_var.get()
        playtime = self.playtime_entry.get().strip()
        rating = self.rating_entry.get().strip()

        # Validate required fields
        if not title or not platform:
            messagebox.showwarning("Required Fields", "Title and Platform are required")
            return
        
        # Validate playtime
        try:
            playtime_hours = float(playtime) if playtime else 0
        except ValueError:
            messagebox.showwarning("Invalid Input", "Playtime must be a number.")
            return
        
        # Validate rating
        if rating:
            try:
                rating_val = int(rating)
                if rating_val < 1 or rating_val > 10:
                    messagebox.showwarning("Invalid Rating", "Rating must be between 1 and 10.")
                    return
            except ValueError:
                messagebox.showwarning("Invalid Input", "Rating must be a number.")
                return
            
        # Create game object
        game = {
            "id": len(self.games) + 1,
            "title": title,
            "platform": platform,
            "status": status,
            "playtime": playtime_hours,
            "rating": rating if rating else "Not rated",
            "date_added": datetime.now().strftime("%Y-%m-%d")
        }

        self.games.append(game)
        self.save_games()

        messagebox.showinfo("Success", f"{title} added to your library!")
        self.show_dashboard()

    #---------------------------------
    # View / Edit / Delete Game
    #---------------------------------

    def view_game_details(self):
        """View Game Details page - User Story #3"""
        selection = self.game_listbox.curselection()
        if not selection:
            messagebox.showinfo("No Selection", "Please select a game to view details.")
            return
 
        game_index = self.get_filtered_game_index(selection[0])
        if game_index is None:
            return
 
        game = self.games[game_index]
 
        self.clear_window()
        self.current_page = "view_details"
        t = self.theme
 
        self.create_header()
 
        main_frame = tk.Frame(self.root, bg=t['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=20)
 
        # IH#5: Back button for backtracking
        tk.Button(main_frame, text="<- Back to Library", command=self.show_dashboard, bg=t['nav'], fg="white", font=("Arial", 10), cursor="hand2").pack(anchor=tk.W, pady=(0, 15))
 
        tk.Label(main_frame, text=game["title"], font=("Arial", 28, "bold"), bg=t['bg'], fg=t['fg']).pack(pady=(0, 10))
 
        # Details frame (IH#3: Show info users want)
        details_frame = tk.Frame(main_frame, bg=t['header'], padx=30, pady=25)
        details_frame.pack(fill=tk.BOTH, expand=True)
 
        tk.Label(details_frame, text=f"Platform: {game['platform']}", bg=t['accent'], fg="white", font=("Arial", 11, "bold"), padx=10, pady=5).pack(anchor=tk.W, pady=5)
        tk.Label(details_frame, text=f"Status: {game['status']}", bg=t['nav'], fg="white", font=("Arial", 11, "bold"), padx=10, pady=5).pack(anchor=tk.W, pady=5)
 
        info_text = f"""
        Playtime: {game['playtime']} hours
        Personal Rating: {game['rating']}
        Date Added: {game['date_added']}
        """
        tk.Label(details_frame, text=info_text, bg=t['header'], fg=t['fg'], font=("Arial", 12), justify=tk.LEFT).pack(anchor=tk.W, pady=15)
 
        # Show favorite/pin status from Microservice 5
        game_id = str(game.get('id', ''))
        user_favs = self.favorites.get_favorites(self.current_user, item_type="game")
        fav_ids = [f['item_id'] for f in user_favs]
        pinned_items = [i for i in self.favorites.get_items_ordered(self.current_user) if i.get('pinned') and i.get('item_type') == 'game']
        pin_ids = [i['item_id'] for i in pinned_items]
 
        is_favorited = game_id in fav_ids
        is_pinned = game_id in pin_ids
 
        status_text = ""
        if is_favorited:
            status_text += "⭐ Favorited   "
        if is_pinned:
            status_text += "📌 Pinned"
        if status_text:
            tk.Label(details_frame, text=status_text.strip(), bg=t['header'], fg=t['muted'], font=("Arial", 10, "italic")).pack(anchor=tk.W, pady=(0, 10))
 
        # Action buttons
        action_frame = tk.Frame(details_frame, bg=t['header'])
        action_frame.pack(pady=20)
 
        # IH#7: Multiple ways - quick toggle or full edit
        if game['status'] != "Completed":
            tk.Button(action_frame, text="Mark as Completed", command=lambda: self.quick_mark_complete(game_index), bg="#4CAF50", fg="white", font=("Arial", 11, "bold"), padx=15, pady=8, cursor="hand2").pack(side=tk.LEFT, padx=10)
 
        tk.Button(action_frame, text="Edit Details", command=lambda: self.show_edit_game_page(game_index), bg=t['nav'], fg="white", font=("Arial", 11), padx=15, pady=8, cursor="hand2").pack(side=tk.LEFT, padx=10)
 
        # Favorite / Unfavorite button — Microservice 5: Favorite/Pinning
        fav_label = "★ Unfavorite" if is_favorited else "☆ Favorite"
        tk.Button(action_frame, text=fav_label, command=lambda: self.toggle_favorite(game_index), bg=t['nav'], fg="white", font=("Arial", 11), padx=15, pady=8, cursor="hand2").pack(side=tk.LEFT, padx=10)
 
        # Pin / Unpin button — Microservice 5: Favorite/Pinning
        pin_label = "📌 Unpin" if is_pinned else "📌 Pin"
        tk.Button(action_frame, text=pin_label, command=lambda: self.toggle_pin(game_index), bg=t['nav'], fg="white", font=("Arial", 11), padx=15, pady=8, cursor="hand2").pack(side=tk.LEFT, padx=10)
 
        # IH#8: Delete with confirmation to prevent mistakes
        tk.Button(action_frame, text="Delete Game", command=lambda: self.delete_game_with_confirmation(game_index), bg="#f44336", fg="white", font=("Arial", 11), padx=15, pady=8, cursor="hand2").pack(side=tk.LEFT, padx=10)
 
    def toggle_favorite(self, game_index):
        """Toggle favorite status for a game using Microservice 5."""
        game = self.games[game_index]
        game_id = str(game.get('id', ''))
 
        user_favs = self.favorites.get_favorites(self.current_user, item_type="game")
        fav_ids = [f['item_id'] for f in user_favs]
 
        if game_id in fav_ids:
            # FavoritePinService doesn't expose an unfavorite method, so patch the file directly
            data = json.load(open(self.favorites.file_name))
            for entry in data.get(self.current_user, []):
                if entry['item_type'] == 'game' and entry['item_id'] == game_id:
                    entry['favorite'] = False
            with open(self.favorites.file_name, 'w') as f:
                json.dump(data, f, indent=2)
            messagebox.showinfo("Removed", f"'{game['title']}' removed from favorites.")
        else:
            result = self.favorites.favorite_item(self.current_user, "game", game_id)
            messagebox.showinfo("Favorited", f"'{game['title']}' added to favorites!")
 
        self.view_game_details_by_index(game_index)
 
    def toggle_pin(self, game_index):
        """Toggle pin status for a game using Microservice 5."""
        game = self.games[game_index]
        game_id = str(game.get('id', ''))
 
        pinned = [i for i in self.favorites.get_items_ordered(self.current_user) if i.get('pinned') and i.get('item_type') == 'game']
        pin_ids = [i['item_id'] for i in pinned]
 
        if game_id in pin_ids:
            result = self.favorites.unpin_item(self.current_user, "game", game_id)
            messagebox.showinfo("Unpinned", f"'{game['title']}' unpinned.")
        else:
            result = self.favorites.pin_item(self.current_user, "game", game_id)
            messagebox.showinfo("Pinned", f"'{game['title']}' pinned to the top of your library!")
 
        self.view_game_details_by_index(game_index)
 
    def view_game_details_by_index(self, game_index):
        """Re-open the details page for a specific game index (used after favorites/pin toggle)."""
        target_game = self.games[game_index]
 
        self.show_dashboard()
 
        # _get_display_games() is now available after show_dashboard rebuilds filter_var
        display, _, _ = self._get_display_games()
        listbox_index = next(
            (i for i, g in enumerate(display) if g.get('id') == target_game.get('id')),
            None
        )
        if listbox_index is not None:
            self.game_listbox.selection_set(listbox_index)
            self.view_game_details()
 
    def show_edit_game_page(self, game_index):
        """Edit Game Details page"""
        game = self.games[game_index]
        self.clear_window()
        self.current_page = "edit_game"
        self.editing_game_index = game_index
        t = self.theme
 
        self.create_header()
 
        main_frame = tk.Frame(self.root, bg=t['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=20)
 
        tk.Label(main_frame, text="Edit Game Details", font=("Arial", 24, "bold"), bg=t['bg'], fg=t['fg']).pack(pady=(0, 20))
 
        form_frame = tk.Frame(main_frame, bg=t['header'], padx=30, pady=25)
        form_frame.pack()
 
        tk.Label(form_frame, text="Game Title: *", bg=t['header'], fg=t['fg'], font=("Arial", 11)).grid(row=0, column=0, sticky=tk.W, pady=8)
        self.edit_title_entry = tk.Entry(form_frame, width=40, font=("Arial", 11))
        self.edit_title_entry.insert(0, game["title"])
        self.edit_title_entry.grid(row=0, column=1, pady=8, padx=(10, 0))
 
        tk.Label(form_frame, text="Platform: *", bg=t['header'], fg=t['fg'], font=("Arial", 11)).grid(row=1, column=0, sticky=tk.W, pady=8)
        self.edit_platform_var = tk.StringVar(value=game["platform"])
        ttk.Combobox(form_frame, textvariable=self.edit_platform_var, values=["PC", "Playstation", "Xbox", "Nintendo Switch", "Mobile"], width=37, font=("Arial", 11), state="readonly").grid(row=1, column=1, pady=8, padx=(10, 0))
 
        tk.Label(form_frame, text="Completion Status:", bg=t['header'], fg=t['fg'], font=("Arial", 11)).grid(row=2, column=0, sticky=tk.W, pady=8)
        self.edit_status_var = tk.StringVar(value=game["status"])
        ttk.Combobox(form_frame, textvariable=self.edit_status_var, values=["Wishlist", "Playing", "Completed", "On Hold"], width=37, font=("Arial", 11), state="readonly").grid(row=2, column=1, pady=8, padx=(10, 0))
 
        tk.Label(form_frame, text="Playtime (hours):", bg=t['header'], fg=t['fg'], font=("Arial", 11)).grid(row=3, column=0, sticky=tk.W, pady=8)
        self.edit_playtime_entry = tk.Entry(form_frame, width=40, font=("Arial", 11))
        self.edit_playtime_entry.insert(0, str(game["playtime"]))
        self.edit_playtime_entry.grid(row=3, column=1, pady=8, padx=(10, 0))
 
        tk.Label(form_frame, text="Personal Rating (1-10):", bg=t['header'], fg=t['fg'], font=("Arial", 11)).grid(row=4, column=0, sticky=tk.W, pady=8)
        self.edit_rating_entry = tk.Entry(form_frame, width=40, font=("Arial", 11))
        if game["rating"] != "Not rated":
            self.edit_rating_entry.insert(0, game["rating"])
        self.edit_rating_entry.grid(row=4, column=1, pady=8, padx=(10, 0))
 
        button_frame = tk.Frame(form_frame, bg=t['header'])
        button_frame.grid(row=5, column=0, columnspan=2, pady=(20, 0))
 
        tk.Button(button_frame, text="Save Changes", command=self.update_game, bg=t['accent'], fg="white", font=("Arial", 12, "bold"), padx=30, pady=10, cursor="hand2").pack(side=tk.LEFT, padx=10)
 
        # IH#5 and IH#8: Cancel with unsaved changes warning
        tk.Button(button_frame, text="Cancel", command=self.cancel_edit_with_warning, bg=t['nav'], fg="white", font=("Arial", 12), padx=30, pady=10, cursor="hand2").pack(side=tk.LEFT, padx=10)
 
    def update_game(self):
        """Update game details"""
        title = self.edit_title_entry.get().strip()
        platform = self.edit_platform_var.get()
        status = self.edit_status_var.get()
        playtime = self.edit_playtime_entry.get().strip()
        rating = self.edit_rating_entry.get().strip()
 
        if not title or not platform:
            messagebox.showwarning("Required Fields", "Title and Platform are required.")
            return
 
        try:
            playtime_hours = float(playtime) if playtime else 0
        except ValueError:
            messagebox.showwarning("Invalid Input", "Playtime must be a number.")
            return
 
        if rating:
            try:
                rating_val = int(rating)
                if rating_val < 1 or rating_val > 10:
                    messagebox.showwarning("Invalid Rating", "Rating must be between 1 and 10.")
                    return
            except ValueError:
                messagebox.showwarning("Invalid Input", "Rating must be a number.")
                return
 
        self.games[self.editing_game_index]["title"] = title
        self.games[self.editing_game_index]["platform"] = platform
        self.games[self.editing_game_index]["status"] = status
        self.games[self.editing_game_index]["playtime"] = playtime_hours
        self.games[self.editing_game_index]["rating"] = rating if rating else "Not rated"
 
        self.save_games()
        messagebox.showinfo("Success", "Game updated successfully!")
        self.show_dashboard()
 
    def quick_mark_complete(self, game_index):
        """IH#7: Quick way to mark complete"""
        self.games[game_index]["status"] = "Completed"
        self.save_games()
        messagebox.showinfo("Success", "Game marked as completed!")
        self.show_dashboard()
 
    def delete_game_with_confirmation(self, game_index):
        """IH#8: Prevent mistakes with confirmation"""
        game_title = self.games[game_index]["title"]
        confirm = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to delete '{game_title}'?\n\nThis action cannot be undone."
        )
        if confirm:
            self.games.pop(game_index)
            self.save_games()
            messagebox.showinfo("Deleted", f"'{game_title}' has been removed from your library.")
            self.show_dashboard()
 
    def cancel_with_confirmation(self):
        """IH#5 and IH#8: cancel with confirmation"""
        confirm = messagebox.askyesno("Cancel", "Are you sure you want to cancel? Any unsaved changes will be lost.")
        if confirm:
            self.show_dashboard()
 
    def cancel_edit_with_warning(self):
        """IH#5 and IH#8: Warn about unsaved changes"""
        confirm = messagebox.askyesno("Unsaved Changes", "You have unsaved changes. Are you sure you want to cancel?")
        if confirm:
            self.show_dashboard()
 
    # --------------------------------------------------
    # Stats Page — Microservice 7: Statistics/Analytics
    # --------------------------------------------------
 
    def show_stats_page(self):
        """Stats page using StatisticsAnalytics microservice"""
        self.clear_window()
        self.current_page = "stats"
        t = self.theme
 
        self.create_header()
 
        main_frame = tk.Frame(self.root, bg=t['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=20)
 
        tk.Button(main_frame, text="<- Back to Library", command=self.show_dashboard, bg=t['nav'], fg="white", font=("Arial", 10), cursor="hand2").pack(anchor=tk.W, pady=(0, 15))
        tk.Label(main_frame, text="📊 Library Stats", font=("Arial", 24, "bold"), bg=t['bg'], fg=t['fg']).pack(pady=(0, 15))
 
        # Call StatisticsAnalytics microservice
        stats_result = StatisticsAnalytics.get_stats(
            self.games_file,
            numeric_fields=['playtime', 'rating'],
            group_by='status'
        )
        top_result = StatisticsAnalytics.get_top_items(self.games_file, sort_field='playtime', limit=5)
 
        stats_frame = tk.Frame(main_frame, bg=t['header'], padx=30, pady=20)
        stats_frame.pack(fill=tk.X)
 
        if not stats_result['success']:
            tk.Label(stats_frame, text="No games in library yet. Add some games to see stats!", bg=t['header'], fg=t['muted'], font=("Arial", 12)).pack()
            return
 
        s = stats_result['stats']
 
        # Summary row
        tk.Label(stats_frame, text=f"Total Games: {s['total_items']}", bg=t['header'], fg=t['fg'], font=("Arial", 13, "bold")).pack(anchor=tk.W, pady=3)
 
        # Status breakdown
        if 'status_breakdown' in s:
            tk.Label(stats_frame, text="By Status:", bg=t['header'], fg=t['muted'], font=("Arial", 11, "italic")).pack(anchor=tk.W, pady=(10, 2))
            for status, count in s['status_breakdown'].items():
                tk.Label(stats_frame, text=f"  {status}: {count}", bg=t['header'], fg=t['fg'], font=("Arial", 11)).pack(anchor=tk.W)
 
        # Numeric summaries
        if 'numeric_summaries' in s:
            ns = s['numeric_summaries']
            tk.Label(stats_frame, text="Playtime & Ratings:", bg=t['header'], fg=t['muted'], font=("Arial", 11, "italic")).pack(anchor=tk.W, pady=(10, 2))
            if 'playtime' in ns:
                p = ns['playtime']
                tk.Label(stats_frame, text=f"  Total Playtime: {p['total']} hrs  |  Avg: {p['average']} hrs  |  Max: {p['max']} hrs", bg=t['header'], fg=t['fg'], font=("Arial", 11)).pack(anchor=tk.W)
            if 'rating' in ns:
                r = ns['rating']
                tk.Label(stats_frame, text=f"  Avg Rating: {r['average']} / 10  |  Highest: {r['max']}  |  Lowest: {r['min']}", bg=t['header'], fg=t['fg'], font=("Arial", 11)).pack(anchor=tk.W)
 
        # Top 5 most played
        if top_result['success'] and top_result['results']:
            tk.Label(stats_frame, text="Top 5 Most Played:", bg=t['header'], fg=t['muted'], font=("Arial", 11, "italic")).pack(anchor=tk.W, pady=(10, 2))
            for i, game in enumerate(top_result['results'], 1):
                tk.Label(stats_frame, text=f"  {i}. {game['title']} — {game['playtime']} hrs ({game['platform']})", bg=t['header'], fg=t['fg'], font=("Arial", 11)).pack(anchor=tk.W)
 
    # ----------------------------------------------------
    # Preferences Page — Microservice 9: User Preferences
    # ----------------------------------------------------
 
    def show_preferences_page(self):
        """Preferences page using UserPreferences microservice"""
        self.clear_window()
        self.current_page = "preferences"
        t = self.theme
 
        self.create_header()
 
        main_frame = tk.Frame(self.root, bg=t['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=20)
 
        tk.Button(main_frame, text="<- Back to Library", command=self.show_dashboard, bg=t['nav'], fg="white", font=("Arial", 10), cursor="hand2").pack(anchor=tk.W, pady=(0, 15))
        tk.Label(main_frame, text="⚙ Preferences", font=("Arial", 24, "bold"), bg=t['bg'], fg=t['fg']).pack(pady=(0, 20))
 
        # Load current preferences
        prefs_result = UserPreferences.get_preferences(self.current_user, defaults=PREF_DEFAULTS)
        current_prefs = prefs_result['preferences'] if prefs_result['success'] else dict(PREF_DEFAULTS)
 
        form_frame = tk.Frame(main_frame, bg=t['header'], padx=30, pady=25)
        form_frame.pack()
 
        # Theme preference
        tk.Label(form_frame, text="Theme:", bg=t['header'], fg=t['fg'], font=("Arial", 11)).grid(row=0, column=0, sticky=tk.W, pady=10)
        self.pref_theme_var = tk.StringVar(value=current_prefs.get('theme', 'dark'))
        ttk.Combobox(form_frame, textvariable=self.pref_theme_var, values=PREF_VALID['theme'], width=25, state="readonly").grid(row=0, column=1, pady=10, padx=(15, 0))
 
        # Default filter preference
        tk.Label(form_frame, text="Default Library Filter:", bg=t['header'], fg=t['fg'], font=("Arial", 11)).grid(row=1, column=0, sticky=tk.W, pady=10)
        self.pref_filter_var = tk.StringVar(value=current_prefs.get('default_filter', 'All'))
        ttk.Combobox(form_frame, textvariable=self.pref_filter_var, values=PREF_VALID['default_filter'], width=25, state="readonly").grid(row=1, column=1, pady=10, padx=(15, 0))
 
        # Buttons
        btn_frame = tk.Frame(form_frame, bg=t['header'])
        btn_frame.grid(row=2, column=0, columnspan=2, pady=(20, 0))
 
        tk.Button(btn_frame, text="Save Preferences", command=self.save_preferences, bg=t['accent'], fg="white", font=("Arial", 12, "bold"), padx=20, pady=8, cursor="hand2").pack(side=tk.LEFT, padx=10)
 
        # IH#8: Reset with confirmation
        tk.Button(btn_frame, text="Reset to Defaults", command=self.reset_preferences_with_confirmation, bg=t['nav'], fg="white", font=("Arial", 11), padx=20, pady=8, cursor="hand2").pack(side=tk.LEFT, padx=10)
 
    def save_preferences(self):
        """Save user preferences using UserPreferences microservice"""
        theme = self.pref_theme_var.get()
        default_filter = self.pref_filter_var.get()
 
        UserPreferences.update_preference(self.current_user, 'theme', theme, valid_options=PREF_VALID)
        UserPreferences.update_preference(self.current_user, 'default_filter', default_filter, valid_options=PREF_VALID)
 
        # Apply the new theme immediately
        self.theme = THEMES.get(theme, THEMES['dark'])
        messagebox.showinfo("Saved", "Preferences saved! Changes will apply on your next page load.")
        self.show_dashboard()
 
    def reset_preferences_with_confirmation(self):
        """IH#8: Reset preferences with confirmation"""
        confirm = messagebox.askyesno("Reset Preferences", "Reset all preferences back to defaults?")
        if confirm:
            UserPreferences.reset_preferences(self.current_user)
            self.theme = THEMES['dark']
            messagebox.showinfo("Reset", "Preferences reset to defaults.")
            self.show_dashboard()
 
    # -----------------------------------------------
    # Header (consistent across all inner pages)
    # -----------------------------------------------
 
    def create_header(self):
        """IH#4: Consistent header on all pages"""
        t = self.theme
        header = tk.Frame(self.root, bg=t['header'], height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
 
        tk.Label(header, text="🎮GameVault", font=("Arial", 16, "bold"), bg=t['header'], fg=t['fg']).pack(side=tk.LEFT, padx=20)
 
        nav_frame = tk.Frame(header, bg=t['header'])
        nav_frame.pack(side=tk.LEFT, padx=20)
 
        tk.Button(nav_frame, text="Home", command=self.show_dashboard, bg=t['nav'], fg="white", font=("Arial", 10), padx=15, pady=5).pack(side=tk.LEFT, padx=5)
        tk.Button(nav_frame, text="📊 Stats", command=self.show_stats_page, bg=t['nav'], fg="white", font=("Arial", 10), padx=15, pady=5).pack(side=tk.LEFT, padx=5)
        tk.Button(nav_frame, text="⚙ Preferences", command=self.show_preferences_page, bg=t['nav'], fg="white", font=("Arial", 10), padx=15, pady=5).pack(side=tk.LEFT, padx=5)
 
        search_frame = tk.Frame(header, bg=t['header'])
        search_frame.pack(side=tk.RIGHT, padx=20)
 
        tk.Label(search_frame, text="Search:", bg=t['header'], fg=t['fg']).pack(side=tk.LEFT)
        self.search_entry = tk.Entry(search_frame, width=20)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(search_frame, text="🔍Search", command=self.search_games, bg=t['nav'], fg="white").pack(side=tk.LEFT)
 
    # ---------------------------------------------
    # Search
    # ---------------------------------------------
 
    def search_games(self):
        """Search and display matching games"""
        query = self.search_entry.get().strip()
        if not query:
            return
 
        # Use Search_Function microservice
        result = Search_Function.search_games(query, self.games_file)
 
        if result['success'] and result['count'] > 0:
            self.game_listbox.delete(0, tk.END)
            status_icon = {"Wishlist": "⭐", "Playing": "🎮", "Completed": "✓", "On Hold": "⏸"}
            for game in result['results']:
                icon = status_icon.get(game["status"], "○")
                self.game_listbox.insert(tk.END, f"{icon} {game['title']} | {game['platform']} | {game['playtime']}h")
            self.info_label.config(text=f"Search Results: {result['count']} game(s) matching '{query}' | Total Games: {len(self.games)}")
            self.current_search_results = result['results']
        else:
            messagebox.showinfo("No Results", f"No games found matching '{query}'")
 
    def clear_search(self):
        """Clear search and show all games"""
        self.search_entry.delete(0, tk.END)
        self.current_search_results = None
        self.refresh_game_list()
 
    # --------------------------------------------
    # Game list / Display
    # --------------------------------------------
 
    def _get_display_games(self):
        """
        Returns the ordered list of games to show in the listbox, plus the sets of
        pinned and favorited IDs. Handles all three filter modes:
          - Status filters (All / Playing / Completed / Wishlist / On Hold):
              Pinned games always appear at the top regardless of their status,
              marked with 📌 so the user knows why they're visible.
          - '⭐ Favorites': shows only favorited games, pinned ones still float first.
        """
        ordered = self.favorites.get_items_ordered(self.current_user)
        pinned_ids  = {str(i['item_id']) for i in ordered if i.get('pinned')   and i.get('item_type') == 'game'}
        fav_ids     = {str(i['item_id']) for i in ordered if i.get('favorite') and i.get('item_type') == 'game'}
 
        filter_status = self.filter_var.get() if hasattr(self, 'filter_var') else 'All'
 
        if filter_status == "⭐ Favorites":
            # Show only favorited games; pinned ones still go first
            base = [g for g in self.games if str(g.get('id', '')) in fav_ids]
        elif filter_status == "All":
            base = list(self.games)
        else:
            # Status filter: include matching games PLUS any pinned games that don't match,
            # so pinned games are never hidden by a status filter.
            status_matches = [g for g in self.games if g["status"] == filter_status]
            pinned_extras  = [g for g in self.games
                              if str(g.get('id', '')) in pinned_ids
                              and g["status"] != filter_status]
            base = status_matches + pinned_extras
 
        # Pinned games always float to the top within whatever set we have
        display = sorted(base, key=lambda g: str(g.get('id', '')) not in pinned_ids)
        return display, pinned_ids, fav_ids
 
    def refresh_game_list(self):
        """Refresh the game list — pinned games shown first through any filter"""
        self.game_listbox.delete(0, tk.END)
 
        display, pinned_ids, fav_ids = self._get_display_games()
        filter_status = self.filter_var.get() if hasattr(self, 'filter_var') else 'All'
 
        status_icon = {"Wishlist": "⭐", "Playing": "🎮", "Completed": "✓", "On Hold": "⏸"}
        for game in display:
            game_id = str(game.get('id', ''))
            icon = status_icon.get(game["status"], "○")
            pin_marker = "📌 " if game_id in pinned_ids else ""
            # When a status filter is active, show the game's actual status next to pinned extras
            # so the user understands why a game from another category is showing
            status_note = ""
            if filter_status not in ("All", "⭐ Favorites") and game["status"] != filter_status:
                status_note = f" [{game['status']}]"
            self.game_listbox.insert(tk.END, f"{pin_marker}{icon} {game['title']} | {game['platform']} | {game['playtime']}h{status_note}")
 
        total    = len(self.games)
        showing  = len(display)
        completed = sum(1 for g in self.games if g["status"] == "Completed")
        self.info_label.config(text=f"Total Games: {total} | Showing: {showing} | Completed: {completed}")
 
    def get_filtered_game_index(self, listbox_index):
        """Get actual game index from the current filtered/sorted display"""
        if self.current_search_results:
            if listbox_index < len(self.current_search_results):
                search_game = self.current_search_results[listbox_index]
                for i, game in enumerate(self.games):
                    if game.get('title') == search_game.get('title') and game.get('platform') == search_game.get('platform'):
                        return i
            return None
 
        display, _, _ = self._get_display_games()
        if listbox_index < len(display):
            target = display[listbox_index]
            for i, game in enumerate(self.games):
                if game.get('id') == target.get('id'):
                    return i
        return None
 
    # ------------------------------------------------------------------
    # FILE I/O
    # ------------------------------------------------------------------
 
    def load_games(self):
        """Load games from JSON file"""
        if os.path.exists(self.games_file):
            try:
                with open(self.games_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []
 
    def save_games(self):
        """Save games to JSON file"""
        with open(self.games_file, 'w') as f:
            json.dump(self.games, f, indent=2)
 
 
def main():
    """Main entry point"""
    root = tk.Tk()
    app = GameVaultApp(root)
    root.mainloop()
 
 
if __name__ == "__main__":
    main()