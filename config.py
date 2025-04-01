"""
Configuration file for the Marvel Snap Card Application.

This file stores configuration variables such as database paths, API URLs,
and directory paths to keep them separate from the main application logic.
"""

# Database Configuration
DB_PATH = 'database/cards.db'  # Path to the SQLite database file

# Marvel Snap Zone API Configuration
CARDS_API_URL = 'https://marvelsnapzone.com/getinfo/?searchtype=cards&searchcardstype=true'  # API URL for card data
ROOT_DIR = 'images'  # Root directory for storing downloaded images
CARDS_DIR = 'cards'  # Directory for storing card images