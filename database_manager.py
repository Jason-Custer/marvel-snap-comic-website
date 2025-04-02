import sqlite3
import os
import math
from config import CARDS_DB_PATH, VARIANTS_DB_PATH
from flask import url_for
import logging

logging.basicConfig(level=logging.DEBUG)

CARDS_PER_PAGE = 30

def create_database():
    """Creates the SQLite database and cards table."""
    os.makedirs(os.path.dirname(CARDS_DB_PATH), exist_ok=True)
    conn = sqlite3.connect(CARDS_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cards (
            cid TEXT PRIMARY KEY,
            name TEXT,
            type TEXT,
            cost INTEGER,
            power INTEGER,
            ability TEXT,
            flavor TEXT,
            art TEXT,
            alternate_art TEXT,
            url TEXT,
            status TEXT,
            carddefid TEXT
        )
    """)
    conn.commit()
    conn.close()
    print("Database created or verified.")

def insert_cards_into_db(cards):
    """Inserts card data into the database."""
    conn = sqlite3.connect(CARDS_DB_PATH)
    cursor = conn.cursor()
    for card in cards:
        if card['art']:
            image_filename = os.path.splitext(os.path.basename(card['art'].split('?', 1)[0]))[0] + ".png"
            image_path = os.path.join("static", "images", "cards", image_filename)
        else:
            image_path = None
        cursor.execute("""
            INSERT OR REPLACE INTO cards (cid, name, type, cost, power, ability, flavor, art, alternate_art, url, status, carddefid)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (card['cid'], card['name'], card['type'], card['cost'], card['power'], card['ability'], card['flavor'], image_path, card['alternate_art'], card['url'], card['status'], card['carddefid']))
        if card['variants']:
            insert_variants_into_db(card['cid'], card['variants'])
    conn.commit()
    conn.close()
    print("Cards inserted into database.")

def create_variants_table():
    """Creates the SQLite variants table."""
    conn = sqlite3.connect(VARIANTS_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS variants (
            variant_id INTEGER PRIMARY KEY AUTOINCREMENT,
            cid TEXT,
            variant_url TEXT,
            variant_image TEXT,
            FOREIGN KEY (cid) REFERENCES cards (cid)
        )
    """)
    conn.commit()
    conn.close()
    print("Variants table created or verified.")

def insert_variants_into_db(cid, variants):
    """Inserts variant data into the variants table with PNG paths."""
    conn = sqlite3.connect(VARIANTS_DB_PATH)
    cursor = conn.cursor()
    for variant in variants:
        image_url = variant.get('art')
        art_filename = variant.get('art_filename')
        if image_url and art_filename:
            png_filename = os.path.splitext(art_filename.rsplit('?', 1)[0])[0] + ".png" #convert to png extension
            image_path = os.path.join("static", "images", "variants", png_filename) #use the png filename.
            cursor.execute("""
                INSERT OR REPLACE INTO variants (cid, variant_url, variant_image)
                VALUES (?, ?, ?)
            """, (cid, image_url, image_path))
        else:
            print(f"Warning: Missing art or art_filename for variant of card CID: {cid}")
    conn.commit()
    conn.close()
    print(f"Variants for {cid} downloaded and inserted.")

def get_card_data_from_db(page, query=None, cost=None, power=None):
    """Retrieves card data from the database with pagination and optional filters."""
    conn = None
    cursor = None
    try:
        conn = sqlite3.connect(CARDS_DB_PATH)
        cursor = conn.cursor()

        sql = """
            SELECT cid, name, type, cost, power, ability, flavor, art, alternate_art, url, status, carddefid
            FROM cards
            WHERE 1=1
        """
        params = []

        if query:
            sql += " AND name LIKE ?"
            params.append(f"%{query}%")
        if cost:
            cost_values = cost.split(',')
            sql += " AND cost IN (" + ",".join(["?"] * len(cost_values)) + ")"
            params.extend(cost_values)
        if power:
            power_values = power.split(',')
            sql += " AND power IN (" + ",".join(["?"] * len(power_values)) + ")"
            params.extend(power_values)

        count_sql = "SELECT COUNT(*) FROM cards WHERE 1=1"
        count_params = params[:]

        cursor.execute(count_sql, count_params)
        total_cards = cursor.fetchone()[0]
        total_pages = math.ceil(total_cards / CARDS_PER_PAGE)

        sql += f" LIMIT {CARDS_PER_PAGE} OFFSET {(page - 1) * CARDS_PER_PAGE}"

        logging.debug(f"Executing SQL: {sql} with params: {params}")

        cursor.execute(sql, params)
        cards = cursor.fetchall()

        logging.debug(f"Fetched {len(cards)} cards from database.")

        cards = [{
            'cid': row[0],
            'name': row[1],
            'type': row[2],
            'cost': row[3],
            'power': row[4],
            'ability': row[5],
            'flavor': row[6],
            'art': row[7],
            'alternate_art': row[8],
            'url': row[9],
            'status': row[10],
            'carddefid': row[11]
        } for row in cards]

        return cards, total_pages

    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")
        return [], 1
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return [], 1
    finally:
        if conn:
            conn.close()
            logging.debug("Database connection closed.")