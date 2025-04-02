"""
Configuration file for the Marvel Snap Card Application.

This file stores configuration variables such as database paths, API URLs,
and directory paths to keep them separate from the main application logic.
"""

# config.py
import os

# Database paths
CARDS_DB_PATH = 'database/cards.db'
VARIANTS_DB_PATH = 'database/variants.db'

# Image download directories
CARDS_API_URL = 'https://marvelsnapzone.com/getinfo/?searchtype=cards&searchcardstype=true'
CARDS_IMAGE_DIR = os.path.join("static", "images", "cards")
VARIANTS_IMAGE_DIR = os.path.join("static", "images", "variants")