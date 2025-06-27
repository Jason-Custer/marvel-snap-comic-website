"""
This is the main Flask application file for the Marvel Snap Card Application.
It handles routing, data retrieval, and rendering of templates.
"""

from flask import Flask, render_template, request, jsonify, url_for
import logging
from marvel_snap_zone_api import get_cards, download_images, download_variants
# Ensure these imports are correct and available
from database_manager import create_database, get_card_data_from_db, insert_cards_into_db, get_variant_detail_from_db, get_card_with_variants_from_db
# You no longer need to import sqlite3 directly here for this route,
# as database_manager.py handles it.
# from config import DATABASE_PATH 

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__, static_folder='static')

# It's good to have both. The basicConfig above sets up the root logger for console output.
# This specific config for a file is also good.
logging.basicConfig(filename='app.log', level=logging.ERROR)

create_database()

def update_cards_data():
    """Updates the database and downloads card images."""
    cards = get_cards()
    if cards:
        insert_cards_into_db(cards)
        download_images(cards)  # This function should handle subdir internally
        download_variants(cards)
    else:
        print("Error: Could not retrieve cards from API. Database not updated.")

update_cards_data()

@app.route("/")
def index():
    """Renders the index page with card data and pagination."""
    page = int(request.args.get('page', 1))
    cards, total_pages = get_card_data_from_db(page)

    print("Main page route accessed")
    print(f"Type of cards: {type(cards)}")
    print(f"Contents of cards (first 5): {cards[:5]}")
    print(f"Total pages: {total_pages}")
    print(f"Current page: {page}")

    return render_template("index.html", cards=cards, total_pages=total_pages, current_page=page)

@app.route("/search_dynamic")
def search_dynamic():
    """Handles dynamic search requests with filters."""
    query = request.args.get('query')
    cost = request.args.get('cost')
    power = request.args.get('power')
    page = int(request.args.get('page', 1))

    print(f"Search Query: {query}, Cost: {cost}, Power: {power}")

    cards, total_pages = get_card_data_from_db(page, query, cost, power)
    return jsonify({"cards": cards, "total_pages": total_pages})

@app.route('/variant/<int:variant_id>')
def variant_detail(variant_id):
    variant_data = get_variant_detail_from_db(variant_id)
    if variant_data:
        return render_template('variant_detail.html', variant=variant_data)
    else:
        # Handle the case where the variant_id is not found
        return render_template('error.html', message="Variant not found.")

@app.route('/card/<cid>')
def card_detail(cid):
    """Displays detailed information for a specific card and its variants with comic links."""
    # This entire block of manual SQLite connection and queries is no longer needed
    # because database_manager.get_card_with_variants_from_db does this for you.
    
    card_data = get_card_with_variants_from_db(cid)
    
    if card_data:
        # The `card_data` dictionary already contains 'variants' key,
        # and each variant within 'variants' has a 'comic_links' key.
        # So you just pass the entire `card_data` to the template.
        return render_template('card_detail.html', card=card_data)
    else:
        return "Card not found", 404

if __name__ == "__main__":
    app.run(debug=True)