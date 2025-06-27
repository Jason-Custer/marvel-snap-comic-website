import sqlite3
import os
import math
from config import DATABASE_PATH
import logging

logging.basicConfig(level=logging.DEBUG)

CARDS_PER_PAGE = 30

def create_database():
    """Creates the SQLite database and the cards, variants, and comics tables if they don't exist."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Create cards table (NO CHANGES NEEDED HERE)
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

    # Create variants table (NO CHANGES NEEDED HERE, as its schema was not altered)
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
            FOREIGN KEY (cid) REFERENCES cards (cid),
            UNIQUE (cid, vid, variant_url, variant_image)
        )
    """)

    # Create comics table (UPDATED SCHEMA HERE)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS comics (
            comic_link_id INTEGER PRIMARY KEY AUTOINCREMENT,
            variant_id INTEGER,
            marvel_link TEXT,
            marvel_unlimited_link TEXT,
            amazon_link TEXT,
            comic_cover_link TEXT,      
            comic_cover_path TEXT,       
            is_original_commission TEXT,
            commission_image_url TEXT,
            commission_image_path TEXT,
            comic_title TEXT,            
            comic_year INTEGER,          
            issue_number TEXT,          
            FOREIGN KEY (variant_id) REFERENCES variants (variant_id)
        )
    """)

    conn.commit()
    conn.close()
    print(f"Database and tables created or verified at: {DATABASE_PATH}")

def insert_cards_into_db(cards):
    """Inserts card data into the cards table of the single database."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    for card in cards:
        if card['art']:
            image_filename = os.path.splitext(os.path.basename(card['art'].split('?', 1)[0]))[0] + ".png"
            image_path = os.path.join("images", "cards", image_filename)
        else:
            image_path = None
        cursor.execute("""
            INSERT OR REPLACE INTO cards (cid, name, type, cost, power, ability, flavor, art, alternate_art, url, status, carddefid)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (card['cid'], card['name'], card['type'], card['cost'], card['power'], card['ability'], card['flavor'], image_path, card['alternate_art'], card['url'], card['status'], card['carddefid']))
        if card['variants']:
            insert_variants_into_db(card['cid'], card['variants'], conn) # Pass the connection
    conn.commit()
    conn.close()
    print(f"{len(cards)} cards inserted/updated in: {DATABASE_PATH}")

def insert_comics_into_db(variant_id, comic_links_data, conn):
    """Inserts comic link data into the comics table for a given variant_id.
       UPDATED to match new 'comics' table schema.
    """
    cursor = conn.cursor()
    for comic_link in comic_links_data:
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO comics (
                    variant_id, marvel_link, marvel_unlimited_link, amazon_link,
                    comic_cover_link,       
                    comic_cover_path,       
                    is_original_commission, commission_image_url, commission_image_path,
                    comic_title,            
                    comic_year,             
                    issue_number            
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                variant_id,
                comic_link.get('marvel_link'),
                comic_link.get('marvel_unlimited_link'),
                comic_link.get('amazon_link'),
                comic_link.get('comic_cover_link'),  
                comic_link.get('comic_cover_path'),  
                comic_link.get('is_original_commission'),
                comic_link.get('commission_image_url'),
                comic_link.get('commission_image_path'),
                comic_link.get('comic_title'),       
                comic_link.get('comic_year'),        
                comic_link.get('issue_number')       
            ))
        except sqlite3.IntegrityError:
            logging.warning(f"Skipping duplicate comic link for variant_id: {variant_id}, Marvel link: {comic_link.get('marvel_link')}")
        except sqlite3.Error as e:
            logging.error(f"Database error during comic link insertion for variant_id {variant_id}: {e}")
            # Do not rollback here, let the calling function handle it.

def insert_variants_into_db(cid, variants, conn=None): # Accept an optional connection
    """Inserts variant data into the variants table of the single database."""
    if conn is None:
        conn = sqlite3.connect(DATABASE_PATH)
        close_conn = True
    else:
        close_conn = False
    cursor = conn.cursor()
    for variant in variants:
        image_url = variant.get('art')
        art_filename = variant.get('art_filename')
        if image_url and art_filename:
            png_filename = os.path.splitext(art_filename.rsplit('?', 1)[0])[0] + ".png"
            image_path = os.path.join("images", "variants", png_filename)
            try:
                # 'variants' insertion is unchanged
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
                if conn.total_changes > 0: # Check if a row was actually inserted or replaced
                    variant_id = cursor.lastrowid # Get the ID of the last inserted variant
                    if variant.get('comic_links'):
                        # Ensure the comic_links data passed to insert_comics_into_db
                        # includes the new fields (comic_title, comic_year, issue_number, comic_cover_path)
                        # and EXCLUDES the removed fields. This depends on how your data source generates comic_links.
                        insert_comics_into_db(variant_id, variant['comic_links'], conn)
            except sqlite3.IntegrityError:
                logging.warning(f"Skipping duplicate variant for CID: {cid}, VID: {variant.get('vid')}, URL: {image_url}, Image: {image_path}")
            except sqlite3.Error as e:
                logging.error(f"Database error during variant insertion for CID {cid}: {e}")
                if close_conn and conn:
                    conn.rollback() # Rollback only if this connection was created here
        else:
            print(f"Warning: Missing art or art_filename for variant of card CID: {cid}")
    if close_conn and conn:
        conn.commit()
        conn.close()
    print(f"Variants for {cid} inserted/updated in: {DATABASE_PATH}")

def get_card_data_from_db(page, query=None, cost=None, power=None):
    """Retrieves card data from the single database with pagination and optional filters."""
    conn = None
    cursor = None
    try:
        conn = sqlite3.connect(DATABASE_PATH)
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

def get_card_with_variants_from_db(cid):
    """Retrieves a single card and its associated variants from the database."""
    conn = None
    cursor = None
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        # Fetch the card details
        cursor.execute("""
            SELECT cid, name, type, cost, power, ability, flavor, art, alternate_art, url, status, carddefid
            FROM cards
            WHERE cid = ?
        """, (cid,))
        card_row = cursor.fetchone()

        if card_row:
            card = {
                'cid': card_row[0],
                'name': card_row[1],
                'type': card_row[2],
                'cost': card_row[3],
                'power': card_row[4],
                'ability': card_row[5],
                'flavor': card_row[6],
                'art': card_row[7],
                'alternate_art': card_row[8],
                'url': card_row[9],
                'status': card_row[10],
                'carddefid': card_row[11]
            }

            # Fetch the associated variants (unchanged)
            cursor.execute("""
                SELECT
                    variant_id, cid, vid, variant_url, variant_image,
                    rarity, rarity_slug, variant_order, status,
                    full_description, inker, sketcher, colorist,
                    ReleaseDate
                FROM variants
                WHERE cid = ?
            """, (cid,))
            variant_rows = cursor.fetchall()
            variants = []
            for row in variant_rows:
                variant_data = {
                    'variant_id': row[0],
                    'cid': row[1],
                    'vid': row[2],
                    'variant_url': row[3],
                    'variant_image': row[4],
                    'rarity': row[5],
                    'rarity_slug': row[6],
                    'variant_order': row[7],
                    'status': row[8],
                    'full_description': row[9],
                    'inker': row[10],
                    'sketcher': row[11],
                    'colorist': row[12],
                    'ReleaseDate': row[13]
                }
                
                # Fetch associated comic links for this variant, including new columns and excluding removed ones
                cursor.execute("""
                    SELECT
                        comic_link_id, marvel_link, marvel_unlimited_link, amazon_link,
                        comic_cover_link,       
                        comic_cover_path,       
                        is_original_commission, commission_image_url, commission_image_path,
                        comic_title,            
                        comic_year,             
                        issue_number            
                    FROM comics
                    WHERE variant_id = ?
                """, (variant_data['variant_id'],))
                comic_link_rows = cursor.fetchall()
                
                comic_links = []
                for comic_row in comic_link_rows:
                    comic_links.append({
                        'comic_link_id': comic_row[0],
                        'marvel_link': comic_row[1],
                        'marvel_unlimited_link': comic_row[2],
                        'amazon_link': comic_row[3],
                        'comic_cover_link': comic_row[4],        
                        'comic_cover_path': comic_row[5],        
                        'is_original_commission': comic_row[6],
                        'commission_image_url': comic_row[7],
                        'commission_image_path': comic_row[8],
                        'comic_title': comic_row[9],             
                        'comic_year': comic_row[10],             
                        'issue_number': comic_row[11]            
                    })
                variant_data['comic_links'] = comic_links
                variants.append(variant_data)
            card['variants'] = variants
            return card
        else:
            return None

    except sqlite3.Error as e:
        logging.error(f"Database error fetching card with variants: {e}")
        return None
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return None 
    finally:
        if conn:
            conn.close()

def get_variant_detail_from_db(variant_id):
    """Retrieves detailed information for a specific variant from the database.
       UPDATED to match new 'comics' table schema when fetching comic links.
    """
    conn = None
    cursor = None
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                v.variant_id, v.cid, v.vid, v.variant_url, v.variant_image,
                v.rarity, v.rarity_slug, v.variant_order, v.status,
                v.full_description, v.inker, v.sketcher, v.colorist,
                v.ReleaseDate,
                c.name AS card_name
            FROM variants v
            JOIN cards c ON v.cid = c.cid
            WHERE v.variant_id = ?
        """, (variant_id,))
        variant_row = cursor.fetchone()

        if variant_row:
            variant_data = {
                'variant_id': variant_row[0],
                'cid': variant_row[1],
                'vid': variant_row[2],
                'variant_url': variant_row[3],
                'variant_image': variant_row[4],
                'rarity': variant_row[5],
                'rarity_slug': variant_row[6],
                'variant_order': variant_row[7],
                'status': variant_row[8],
                'full_description': variant_row[9],
                'inker': variant_row[10],
                'sketcher': variant_row[11],
                'colorist': variant_row[12],
                'ReleaseDate': variant_row[13],
                'card_name': variant_row[14]
            }
            
            # Fetch associated comic links for this specific variant, including new columns and excluding removed ones
            cursor.execute("""
                SELECT
                    comic_link_id, marvel_link, marvel_unlimited_link, amazon_link,
                    comic_cover_link,       
                    comic_cover_path,       
                    is_original_commission, commission_image_url, commission_image_path,
                    comic_title,            
                    comic_year,             
                    issue_number            
                FROM comics
                WHERE variant_id = ?
            """, (variant_data['variant_id'],))
            comic_link_rows = cursor.fetchall()
            
            comic_links = []
            for comic_row in comic_link_rows:
                comic_links.append({
                    'comic_link_id': comic_row[0],
                    'marvel_link': comic_row[1],
                    'marvel_unlimited_link': comic_row[2],
                    'amazon_link': comic_row[3],
                    'comic_cover_link': comic_row[4],        
                    'comic_cover_path': comic_row[5],        
                    'is_original_commission': comic_row[6],
                    'commission_image_url': comic_row[7],
                    'commission_image_path': comic_row[8],
                    'comic_title': comic_row[9],             
                    'comic_year': comic_row[10],             
                    'issue_number': comic_row[11]            
                })
            variant_data['comic_links'] = comic_links
            return variant_data
        else:
            return None
    except sqlite3.Error as e:
        logging.error(f"Database error fetching variant detail: {e}")
        return None
    finally:
        if conn:
            conn.close()