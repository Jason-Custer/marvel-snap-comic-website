from flask import Flask, render_template
import sqlite3
import logging

app = Flask(__name__, static_url_path='/marvel-snap', static_folder='marvel-snap')

# Configure logging
logging.basicConfig(filename='app.log', level=logging.ERROR)

def get_card_data_from_db():
    """Fetches card data from the SQLite database with error handling."""
    try:
        conn = sqlite3.connect("database/cards.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name, energy, power, image FROM cards")
        cards = cursor.fetchall()
        conn.close()
        card_data = [{"name": name, "energy": energy, "power": power, "image": image} for name, energy, power, image in cards]
        return card_data
    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")
        return []  # Return an empty list in case of error.

@app.route("/")
def index():
    card_data = get_card_data_from_db()
    if not card_data:
        return render_template("index.html", error="Failed to fetch card data from the database.")
    return render_template("index.html", cards=card_data)

if __name__ == "__main__":
    app.run(debug=True)