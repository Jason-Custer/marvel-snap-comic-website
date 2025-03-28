import sqlite3
import os
from api_integration import get_cards, download_card_images

def create_database():
    """
    Creates the SQLite database and inserts card data from the API.
    """
    conn = sqlite3.connect("database/cards.db")
    cursor = conn.cursor()

    # Create the cards table if it doesn't exist.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            energy INTEGER,
            power INTEGER,
            image TEXT
        )
    """)

    # Get card data from the API.
    card_data = get_cards()

    if not card_data:
        print("Error: Could not retrieve card data from API.")
        conn.close()
        return

    # Download card images.
    download_card_images(card_data)

    # Insert card data into the database.
    for card in card_data:
        image_filename = card['image'].rsplit('/', 1)[-1].rsplit('?', 1)[0].replace(".webp", "")
        image_path = os.path.join("cards", image_filename).replace("\\", "/")

        cursor.execute("""
            INSERT INTO cards (name, energy, power, image)
            VALUES (?, ?, ?, ?)
        """, (card['name'], card['energy'], card['power'], image_path + ".png"))

    conn.commit()
    conn.close()
    print("Database and card data updated successfully.")

if __name__ == "__main__":
    create_database()