import sqlite3  # Imports the library to work with SQLite.

def create_database():
    conn = sqlite3.connect("database/cards.db")  # Connects to (or creates) the database file.
    cursor = conn.cursor()  # Creates a tool to send commands to the database.

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            energy INTEGER,
            power INTEGER,
            image TEXT
        )
    """)  # This SQL command creates a table named 'cards' with specified columns.

    conn.commit()  # Saves the changes to the database.
    conn.close()  # Closes the connection to the database.

if __name__ == "__main__":
    create_database()
    print("Database and table created successfully!")  # Prints a confirmation message.