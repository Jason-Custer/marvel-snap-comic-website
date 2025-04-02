"""
This is the main Flask application file for the Marvel Snap Card Application.
It handles routing, data retrieval, and rendering of templates.
"""

from flask import Flask, render_template, request, jsonify, url_for
import logging
from marvel_snap_zone_api import get_cards, download_images, download_variants
from database_manager import create_database, get_card_data_from_db, insert_cards_into_db, create_variants_table
import sqlite3
from config import CARDS_DB_PATH, VARIANTS_DB_PATH

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__, static_folder='static')

logging.basicConfig(filename='app.log', level=logging.ERROR)

create_database()
create_variants_table() 

def update_cards_data():
    """Updates the database and downloads card images."""
    cards = get_cards()
    if cards:
        insert_cards_into_db(cards)
        download_images(cards)  # Remove the "cards" subdir argument
        download_variants(cards)
    else:
        print("Error: Could not retrieve cards from API. Database not updated.")

update_cards_data()

@app.route("/")
def index():
    """Renders the index page with card data and pagination."""
    page = int(request.args.get('page', 1))
    cards, total_pages = get_card_data_from_db(page)

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

@app.route('/card/<cid>')
def card_detail(cid):
    """Displays detailed information for a specific card and its variants."""
    try:
        conn = sqlite3.connect(CARDS_DB_PATH)
        cursor = conn.cursor()

        # Get base card data
        cursor.execute("SELECT * FROM cards WHERE cid = ?", (cid,))
        card = cursor.fetchone()

        if not card:
            return "Card not found", 404

        card_dict = {
            'cid': card[0], 'name': card[1], 'type': card[2], 'cost': card[3],
            'power': card[4], 'ability': card[5], 'flavor': card[6], 'art': card[7],
            'alternate_art': card[8], 'url': card[9], 'status': card[10], 'carddefid': card[11]
        }

        # Get variant data
        conn_variants = sqlite3.connect(VARIANTS_DB_PATH)
        cursor_variants = conn_variants.cursor()
        cursor_variants.execute("SELECT * FROM variants WHERE cid = ?", (cid,))
        variants = cursor_variants.fetchall()
        variants_list = []
        for variant in variants:
            variants_list.append({
                'variant_id': variant[0], 'cid': variant[1], 'variant_url': variant[2],
                'variant_image': variant[3]
            })

        # Placeholder comic data
        comic_links = {
            variant['variant_id']: {
                'marvel_link': 'https://www.marvel.com/comics/issue/0/example_issue_1',
                'marvel_unlimited_link': 'https://www.marvel.com/comics/series/0/example_series_1',
                'amazon_link': 'https://www.amazon.com/dp/B00EXAMPLE',
                'cover_image': 'https://via.placeholder.com/150' # Placeholder image
            } for variant in variants_list
        }

        return render_template('card_detail.html', card=card_dict, variants=variants_list, comic_links=comic_links)

    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")
        return "Database error", 500
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return "Internal server error", 500
    finally:
        if conn:
            conn.close()
        if conn_variants:
            conn_variants.close()

if __name__ == "__main__":
    app.run(debug=True)