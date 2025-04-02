"""
This is the main Flask application file for the Marvel Snap Card Application.
It handles routing, data retrieval, and rendering of templates.
"""

from flask import Flask, render_template, request, jsonify, url_for
import logging
from marvel_snap_zone_api import get_cards, download_images, download_variants
from database_manager import create_database, get_card_data_from_db, insert_cards_into_db
import logging

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

if __name__ == "__main__":
    app.run(debug=True)