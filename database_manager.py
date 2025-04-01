import sqlite3
import os
import math
from config import DB_PATH
from flask import url_for

CARDS_PER_PAGE = 30

def create_database():
    """Creates the SQLite database and cards table."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            cost INTEGER,
            power INTEGER,
            image TEXT
        )
    """)
    conn.commit()
    conn.close()
    print("Database created or verified.")

def insert_cards_into_db(cards):
    """Inserts card data into the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    for card in cards:
        cursor.execute("""
            INSERT OR REPLACE INTO cards (name, cost, power, image)
            VALUES (?, ?, ?, ?)
        """, (card['name'], card['cost'], card['power'], os.path.join("images", card['art'].rsplit('/', 1)[-1].rsplit('?', 1)[0] + ".png")))
    conn.commit()
    conn.close()
    print("Cards inserted into database.")

def get_card_data_from_db(page, query=None, cost=None, power=None):
    """Retrieves card data from the database with optional filters and pagination."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    sql = "SELECT name, cost, power, image FROM cards WHERE 1=1"
    params = []

    if query:
        sql += " AND name LIKE ?"
        params.append('%' + query + '%')

    if cost:
        cost_values = cost.split(',')
        cost_conditions = []
        for val in cost_values:
            val = val.strip()
            if val == '1':
                cost_conditions.append("cost <= 1")
            elif val == '6':
                cost_conditions.append("cost >= 6")
            else:
                cost_conditions.append("cost = ?")
                params.append(val)
        if cost_conditions:
            sql += " AND (" + " OR ".join(cost_conditions) + ")"

    if power:
        power_values = power.split(',')
        power_conditions = []
        for val in power_values:
            val = val.strip()
            if val == '1':
                power_conditions.append("power <= 1")
            elif val == '6':
                power_conditions.append("power >= 6")
            else:
                power_conditions.append("power = ?")
                params.append(val)
        if power_conditions:
            sql += " AND (" + " OR ".join(power_conditions) + ")"

    cursor.execute(sql, params)
    cards = cursor.fetchall()
    conn.close()

    total_cards = len(cards)
    total_pages = math.ceil(total_cards / CARDS_PER_PAGE)
    start_index = (page - 1) * CARDS_PER_PAGE
    end_index = start_index + CARDS_PER_PAGE
    cards = cards[start_index:end_index]

    card_data = []
    for name, cost, power, image in cards:
        if image.startswith('cards/'):
            image = image.replace('cards/', '', 1)  # Strip out prefix
        card_data.append({
            "name": name,
            "cost": cost,
            "power": power,
            "image": url_for('static', filename=image)
        })
    return card_data, total_pages