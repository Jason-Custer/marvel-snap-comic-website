import sqlite3
import os
import math
from config import CARDS_DB_PATH, VARIANTS_DB_PATH
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
    """Inserts card data into the database with corrected art paths."""
    conn = sqlite3.connect(CARDS_DB_PATH)
    cursor = conn.cursor()
    for card in cards:
        if card['art']:
            image_filename = os.path.splitext(os.path.basename(card['art'].split('?', 1)[0]))[0] + ".png"
            image_path = os.path.join("images", "cards", image_filename)  # Removed "static"
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
    """Creates the SQLite variants table with all desired columns."""
    conn = sqlite3.connect(VARIANTS_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS variants (
            variant_id INTEGER PRIMARY KEY AUTOINCREMENT,
            cid TEXT,
            vid INTEGER,
            variant_url TEXT,
            variant_image TEXT,
            rarity TEXT,
            rarity_slug TEXT,
            variant_order TEXT,
            status TEXT,
            full_description TEXT,
            inker TEXT,
            sketcher TEXT,
            colorist TEXT,
            ReleaseDate INTEGER,
            FOREIGN KEY (cid) REFERENCES cards (cid)
        )
    """)
    conn.commit()
    conn.close()
    print("Variants table created or verified.")

def insert_variants_into_db(cid, variants):
    """Inserts variant data into the variants table with specified fields."""
    conn = sqlite3.connect(VARIANTS_DB_PATH)
    cursor = conn.cursor()
    for variant in variants:
        image_url = variant.get('art')
        art_filename = variant.get('art_filename')
        if image_url and art_filename:
            png_filename = os.path.splitext(art_filename.rsplit('?', 1)[0])[0] + ".png"
            image_path = os.path.join("images", "variants", png_filename)
            cursor.execute("""
                INSERT OR REPLACE INTO variants (cid, vid, variant_url, variant_image, rarity, rarity_slug, variant_order, status, full_description, inker, sketcher, colorist, ReleaseDate)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                cid,
                variant.get('vid'),
                image_url,
                image_path,
                variant.get('rarity'),
                variant.get('rarity_slug'),
                variant.get('variant_order'),
                variant.get('status'),
                variant.get('full_description'),
                variant.get('inker'),
                variant.get('sketcher'),
                variant.get('colorist'),
                variant.get('ReleaseDate')
            ))
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

        base_sql = """
            SELECT cid, name, type, cost, power, ability, flavor, art, alternate_art, url, status, carddefid
            FROM cards
            WHERE 1=1
        """
        count_sql = "SELECT COUNT(*) FROM cards WHERE 1=1"
        
        params = []
        count_params = []

        if query and query.strip():
            base_sql += " AND name LIKE ?"
            count_sql += " AND name LIKE ?"
            param_value = f"%{query}%"
            params.append(param_value)
            count_params.append(param_value)

        if cost and cost.strip():
            cost_values = cost.split(',')
            placeholders = ",".join(["?"] * len(cost_values))
            base_sql += f" AND cost IN ({placeholders})"
            count_sql += f" AND cost IN ({placeholders})"
            params.extend(cost_values)
            count_params.extend(cost_values)

        if power and power.strip():
            power_values = power.split(',')
            placeholders = ",".join(["?"] * len(power_values))
            base_sql += f" AND power IN ({placeholders})"
            count_sql += f" AND power IN ({placeholders})"
            params.extend(power_values)
            count_params.extend(power_values)

        # Execute count query
        cursor.execute(count_sql, count_params)
        total_cards = cursor.fetchone()[0]
        total_pages = math.ceil(total_cards / CARDS_PER_PAGE) if total_cards > 0 else 1

        # Add pagination
        base_sql += " LIMIT ? OFFSET ?"
        params.append(CARDS_PER_PAGE)
        params.append((page - 1) * CARDS_PER_PAGE)

        logging.debug(f"Executing SQL: {base_sql} with params: {params}")
        cursor.execute(base_sql, params)
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