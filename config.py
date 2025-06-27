"""
Configuration file for the Marvel Snap Card Application.

This file stores configuration variables such as database paths, API URLs,
and directory paths to keep them separate from the main application logic.
"""

# config.py
import os

# Data
DATABASE_PATH = 'data/snap_data.db'
MARVEL_PUBLIC_KEY = 'c87c0772facd699263979d1bbe58084d'
MARVEL_PRIVATE_KEY = 'b23f93bf9cadc3e2b81dec9a94afa6313041358b'
YOUR_DOMAIN_FOR_STATIC_ASSETS = "127.0.0.1:5000"

# Google Sheets Configuration
GOOGLE_SHEET_ID = "1FIb0pd8CraOrO7bTAk9I2q0i7N-lwTt5eJIcDvRmiIg"
GOOGLE_SHEET_WORKSHEET_NAME = "Variant Data"

# Path to your Google Service Account Key JSON file
SERVICE_ACCOUNT_KEY_PATH = "service_account_key.json"

# Image download directories
CARDS_API_URL = 'https://marvelsnapzone.com/getinfo/?searchtype=cards&searchcardstype=true'
CARDS_IMAGE_DIR = os.path.join("static", "images", "cards")
VARIANTS_IMAGE_DIR = os.path.join("static", "images", "variants")