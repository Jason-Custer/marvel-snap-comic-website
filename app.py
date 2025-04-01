"""
This is the main Flask application file for the Marvel Snap Card Application.
It handles routing, data retrieval, and rendering of templates.
"""

from flask import Flask, render_template, request, jsonify, url_for
import logging
from marvel_snap_zone_api import get_cards, download_images
from database_manager import create_database, get_card_data_from_db, insert_cards_into_db # Import get_card_data_from_db
from config import DB_PATH

app = Flask(__name__, static_folder='static')

logging.basicConfig(filename='app.log', level=logging.ERROR)

# Call create_database() to ensure the cards table exists
print(f"Database Path: {DB_PATH}")  # Added print statement
create_database()

def update_cards_data():
    """Updates card data and images."""
    cards = get_cards()
    print(f"API Cards Data: {cards}")
    if cards:
        download_images(cards)
        print("Attempting to insert cards into database.")
        insert_cards_into_db(cards)
        print("Card data inserted into database.")
    else:
        print("Failed to retrieve card data.")

update_cards_data()

@app.route("/")
def index():
    """Renders the index page with card data and pagination."""
    page = int(request.args.get('page', 1))
    cards, total_pages = get_card_data_from_db(page)

    print(f"Cards data: {cards}") # Print the card data

    return render_template("index.html", cards=cards, total_pages=total_pages, current_page=page)

@app.route("/search_dynamic")
def search_dynamic():
    """Handles dynamic search requests with filters."""
    query = request.args.get('query')
    cost = request.args.get('cost')
    power = request.args.get('power')
    page = int(request.args.get('page', 1))

    cards, total_pages = get_card_data_from_db(page, query, cost, power)
    return jsonify({"cards": cards, "total_pages": total_pages})

if __name__ == "__main__":
    app.run(debug=True)