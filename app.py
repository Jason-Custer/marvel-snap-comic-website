from flask import Flask, render_template, request, jsonify, url_for
import sqlite3
import logging

app = Flask(__name__, static_folder='marvel-snap') # Removed static_url_path

# Configure logging
logging.basicConfig(filename='app.log', level=logging.ERROR)

CARDS_PER_PAGE = 30

def get_card_data_from_db(page, query=None):
    conn = sqlite3.connect("database/cards.db")
    cursor = conn.cursor()
    sql = "SELECT name, energy, power, image FROM cards"
    params = []
    if query:
        sql += " WHERE name LIKE ?"
        params.append('%' + query + '%')
    cursor.execute(sql, params)
    cards = cursor.fetchall()
    conn.close()
    
    total_cards = len(cards)
    total_pages = (total_cards + CARDS_PER_PAGE - 1) // CARDS_PER_PAGE
    start_index = (page - 1) * CARDS_PER_PAGE
    end_index = start_index + CARDS_PER_PAGE
    cards = cards[start_index:end_index]

    card_data = []
    for name, energy, power, image in cards:
        if image.startswith('marvel-snap/'):
            image = image.replace('marvel-snap/', '', 1)  # Strip out prefix
        card_data.append({
            "name": name,
            "energy": energy,
            "power": power,
            "image": url_for('static', filename=image)  # Store correct path
        })
    return card_data, total_pages

@app.route("/")
def index():
    page = int(request.args.get('page', 1))
    cards, total_pages = get_card_data_from_db(page)
    return render_template("index.html", cards=cards, total_pages=total_pages)

@app.route("/search_dynamic")
def search_dynamic():
    query = request.args.get('query')
    energy = request.args.get('energy')
    power = request.args.get('power')
    page = int(request.args.get('page', 1))
    print(f"Search Query: {query}, Energy: {energy}, Power: {power}, Page: {page}")

    conn = sqlite3.connect("database/cards.db")
    cursor = conn.cursor()
    sql = "SELECT name, energy, power, image FROM cards WHERE 1=1"
    params = []
    if query:
        sql += " AND name LIKE ?"
        params.append('%' + query + '%')
    if energy:
        energy_values = energy.split(',')
        energy_conditions = []
        for val in energy_values:
            val = val.strip()
            if val == '1':
                energy_conditions.append("energy <= 1")
            elif val == '6':
                energy_conditions.append("energy >= 6")
            else:
                energy_conditions.append("energy = ?")
                params.append(val)
        if energy_conditions:
            sql += " AND (" + " OR ".join(energy_conditions) + ")"
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

    print(f"SQL Query: {sql}")
    print(f"SQL Params: {params}")

    cursor.execute(sql, params)
    all_cards = cursor.fetchall()

    total_cards = len(all_cards)
    total_pages = (total_cards + CARDS_PER_PAGE - 1) // CARDS_PER_PAGE

    start_index = (page - 1) * CARDS_PER_PAGE
    end_index = start_index + CARDS_PER_PAGE
    cards = all_cards[start_index:end_index]

    print(f"Database Results: {cards}")

    conn.close()
    card_data = []
    for name, energy, power, image in cards:
        if image.startswith('marvel-snap/'):
            image = image.replace('marvel-snap/', '', 1) # Strip out prefix
        card_data.append({
            "name": name,
            "energy": energy,
            "power": power,
            "image": url_for('static', filename=image) # Ensure correct URL formatting
        })

    print(f"Total Cards: {total_cards}")
    print(f"Total Pages: {total_pages}")
    return jsonify({"cards": card_data, "total_pages": total_pages})        

if __name__ == "__main__":
    app.run(debug=True)