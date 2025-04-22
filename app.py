"""
This is the main Flask application file for the Marvel Snap Card Application.
It handles routing, data retrieval, and rendering of templates.
"""

from flask import Flask, render_template, request, jsonify, url_for
import logging
from marvel_snap_zone_api import get_cards, download_images, download_variants
from database_manager import create_database, get_card_data_from_db, insert_cards_into_db, get_variant_detail_from_db, get_card_with_variants_from_db
import sqlite3
from config import DATABASE_PATH

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__, static_folder='static')

logging.basicConfig(filename='app.log', level=logging.ERROR)

create_database()

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
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.row_factory = sqlite3.Row  # Allows accessing columns by name

        # Get base card data
        cursor.execute("SELECT * FROM cards WHERE cid = ?", (cid,))
        card = cursor.fetchone()

        if not card:
            return "Card not found", 404

        card_dict = dict(card)

        # Get variant data
        cursor.execute("""
            SELECT
                variant_id, cid, vid, variant_url, variant_image,
                rarity, rarity_slug, variant_order, status,
                full_description, inker, sketcher, colorist,
                ReleaseDate
            FROM variants
            WHERE cid = ?
            ORDER BY variant_order
        """, (cid,))
        variants_data = cursor.fetchall()

        variants_list = [dict(row) for row in variants_data]
        for variant in variants_list:
            print(f"Variant data: {variant}")

        # Attach variants to the card_dict
        card_dict['variants'] = variants_list

        # Get comic link data
        cursor.execute("""
            SELECT variant_id, marvel_link, marvel_unlimited_link, amazon_link, cover_image
            FROM comics
            WHERE variant_id IN (SELECT variant_id FROM variants WHERE cid = ?)
        """, (cid,))
        comics_data = cursor.fetchall()

        comic_links = {}
        for row in comics_data:
            comic_links[row['variant_id']] = {
                'marvel_link': row['marvel_link'],
                'marvel_unlimited_link': row['marvel_unlimited_link'],
                'amazon_link': row['amazon_link'],
                'cover_image': row['cover_image']
            }

        return render_template('card_detail.html', card=card_dict, variants=variants_list, comic_links=comic_links)

    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")
        return "Database error", 500
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    app.run(debug=True)