import sqlite3
import requests
import logging
import os
from datetime import datetime

# You might need to add your Marvel API keys to config.py later if you integrate that
# from config import MARVEL_PUBLIC_KEY, MARVEL_PRIVATE_KEY

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_db_connection(db_path):
    """Establishes a connection to the SQLite database."""
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row # Allows accessing columns by name
        return conn
    except sqlite3.Error as e:
        logging.error(f"Database connection error: {e}")
        raise

def create_comic_metadata_table(conn):
    """
    Creates the comic_metadata table if it doesn't exist.
    This table stores the enriched comic book information for each variant.
    """
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS comic_metadata (
            variant_id INTEGER PRIMARY KEY,
            snap_card_name TEXT,
            snap_card_vid TEXT,
            variant_image_url TEXT,
            artist_name TEXT,
            is_original_commission BOOLEAN,
            source_type TEXT,
            comic_title TEXT,
            comic_year INTEGER,
            issue_number INTEGER,
            variant_description TEXT,
            comic_cover_link TEXT,
            source_url_type TEXT,
            marvel_api_found BOOLEAN,
            marvel_link TEXT,
            marvel_unlimited_link TEXT,
            amazon_link TEXT,
            identified_date TEXT, -- Stored as ISO format string 'YYYY-MM-DDTHH:MM:SS.ffffff'
            manual_status TEXT,   -- e.g., 'Needs Identification', 'Identified - Needs API Lookup', 'Fully Processed', 'Manually Verified', 'Skip API'
            manual_notes TEXT,
            reference_links TEXT,
            marvel_comic_id INTEGER,
            marvel_creators_summary TEXT,
            FOREIGN KEY (variant_id) REFERENCES variants(variant_id)
        );
    """)
    conn.commit()
    logging.info("Ensured comic_metadata table exists.")

def update_or_insert_comic_metadata(conn, data):
    """
    Updates an existing record or inserts a new one into comic_metadata.
    The 'data' dictionary should contain all relevant fields.
    """
    cursor = conn.cursor()
    # Convert Python booleans to SQLite integers (0 or 1)
    is_original_commission_db = 1 if data.get('is_original_commission') else 0
    marvel_api_found_db = 1 if data.get('marvel_api_found') else 0

    try:
        cursor.execute("""
            INSERT OR REPLACE INTO comic_metadata (
                variant_id, snap_card_name, snap_card_vid, variant_image_url, artist_name,
                is_original_commission, source_type, comic_title, comic_year, issue_number,
                variant_description, comic_cover_link, source_url_type, marvel_api_found,
                marvel_link, marvel_unlimited_link, amazon_link, identified_date,
                manual_status, manual_notes, reference_links, marvel_comic_id, marvel_creators_summary
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get('variant_id'),
            data.get('snap_card_name'),
            data.get('snap_card_vid'),
            data.get('variant_image_url'),
            data.get('artist_name'),
            is_original_commission_db,
            data.get('source_type'),
            data.get('comic_title'),
            data.get('comic_year'),
            data.get('issue_number'),
            data.get('variant_description'),
            data.get('comic_cover_link'),
            data.get('source_url_type'),
            marvel_api_found_db,
            data.get('marvel_link'),
            data.get('marvel_unlimited_link'),
            data.get('amazon_link'),
            data.get('identified_date'),
            data.get('manual_status'),
            data.get('manual_notes'),
            data.get('reference_links'),
            data.get('marvel_comic_id'),
            data.get('marvel_creators_summary')
        ))
        conn.commit()
        logging.info(f"Successfully updated/inserted comic metadata for variant_id: {data.get('variant_id')}")
    except sqlite3.Error as e:
        logging.error(f"Failed to update/insert comic metadata for variant_id {data.get('variant_id')}: {e}")
        # Optionally, you might want to rollback the transaction if this is part of a larger one
        # conn.rollback()


def search_marvel_api(comic_title, issue_number, public_key=None, private_key=None):
    """
    Searches the Marvel API for a comic.
    NOTE: You'll need to obtain and configure your Marvel API keys for this function to work.
    This is a simplified example; full implementation requires proper authentication (hash, timestamp).
    """
    # Placeholder for actual Marvel API integration
    # For a real implementation, you'd need your public and private keys
    # and to generate a hash (ts + private_key + public_key) using md5.
    
    # from config import MARVEL_PUBLIC_KEY, MARVEL_PRIVATE_KEY
    # import hashlib
    # import time
    # ts = str(time.time())
    # auth_string = ts + MARVEL_PRIVATE_KEY + MARVEL_PUBLIC_KEY
    # hash_value = hashlib.md5(auth_string.encode('utf-8')).hexdigest()
    # params = {
    #     'title': comic_title,
    #     'issueNumber': issue_number,
    #     'apikey': MARVEL_PUBLIC_KEY,
    #     'ts': ts,
    #     'hash': hash_value
    # }
    
    logging.info(f"Attempting Marvel API search for: {comic_title} #{issue_number}. (Marvel API keys not configured/used in this dummy function.)")
    
    # Dummy data for demonstration if API keys are not used
    # In a real scenario, this would be populated by the API response
    if "spider-man" in comic_title.lower() and issue_number == 1:
        return {
            'marvel_api_found': True,
            'comic_cover_link': 'https://example.com/marvel_spiderman_cover.jpg',
            'marvel_link': 'https://www.marvel.com/comics/spiderman_1',
            'marvel_unlimited_link': 'https://www.marvel.com/unlimited/spiderman_1',
            'amazon_link': 'https://www.amazon.com/spiderman_1',
            'marvel_comic_id': 12345,
            'marvel_creators_summary': 'Writer: Stan Lee, Artist: Steve Ditko'
        }
    else:
        return {
            'marvel_api_found': False,
            'comic_cover_link': '',
            'marvel_link': '',
            'marvel_unlimited_link': '',
            'amazon_link': '',
            'marvel_comic_id': None,
            'marvel_creators_summary': ''
        }

def process_variant_for_automated_enrichment(variant_data):
    """
    Takes variant data (e.g., from Google Sheet), attempts Marvel API enrichment,
    and returns a dictionary with all fields, including API results.
    """
    processed_data = variant_data.copy() # Start with a copy of the input data
    
    comic_title = processed_data.get('comic_title')
    issue_number = processed_data.get('issue_number')

    if comic_title and issue_number:
        # Attempt Marvel API search
        # Replace with your actual Marvel API public/private keys if you implement
        marvel_api_results = search_marvel_api(comic_title, issue_number)
        
        # Merge API results into processed_data
        processed_data.update(marvel_api_results)
        
        if marvel_api_results.get('marvel_api_found'):
            processed_data['manual_status'] = 'Fully Processed'
            logging.info(f"Variant {processed_data.get('variant_id')}: Marvel API match found.")
        else:
            processed_data['manual_status'] = 'Identified - API No Match'
            logging.warning(f"Variant {processed_data.get('variant_id')}: No Marvel API match found for '{comic_title}' #{issue_number}.")
    else:
        # If comic_title or issue_number are missing, API search cannot be performed
        processed_data['marvel_api_found'] = False
        processed_data['manual_status'] = 'Needs Identification' # Or a specific status like 'Missing Identification Data'
        logging.info(f"Variant {processed_data.get('variant_id')}: Skipping API lookup due to missing comic_title or issue_number.")

    # Set identified_date if it's new or being processed
    if not processed_data.get('identified_date') or processed_data['manual_status'] in ['Fully Processed', 'Identified - API No Match']:
        processed_data['identified_date'] = datetime.now().isoformat()
    
    return processed_data