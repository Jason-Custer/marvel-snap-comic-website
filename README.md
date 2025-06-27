# Marvel Snap Comic Cover Art Variants

This project is a web application designed to highlight the connection between Marvel Snap in-game variants and classic Marvel comic book cover art. It fetches card data and variant information from the Marvel Snap Zone API, emphasizing the comic origins of these variants.

## File Structure

marvel-snap-project/
├── app.py                      # Flask application for web interface to view cards and variants
├── config.py                   # Configuration settings: database path, Google Sheets ID, API keys
├── database_manager.py         # Handles all SQLite database interactions
├── marvel_snap_zone_api.py     # Manages fetching card data and variant images from Snap.fan (or similar source)
├── initial_export.py           # Script to perform the initial export of variant data to a new Google Sheet
├── sheets_sync.py              # Script to synchronize data between the SQLite DB and Google Sheet, including Marvel API lookup
├── comic_integration.py        # Contains logic for Marvel API interaction and data processing for comic metadata
├── service_account_key.json    # Google Service Account Key for Sheets API access
├── data/
│   └── snap_data.db            # SQLite database file for cards, variants, and comic metadata
├── static/
│   ├── images/
│   │   ├── cards/              # Stored images for base cards
│   │   ├── comics/             # Stored images for comic covers (if downloaded)
│   │   └── variants/           # Stored images for variant cards
│   ├── script.js               # Client-side JavaScript logic
│   └── style.css               # CSS styles for the web interface
└── templates/
├── index.html              # HTML template for the main card list page
├── card_detail.html        # HTML template for individual card details and their variants
└── variant_detail.html     # HTML template for individual variant details, including comic info
└── README.md                   # This readme file

## Database Schema (`snap_data.db`)

cards
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

variants 
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

comics
    comic_link_id INTEGER PRIMARY KEY AUTOINCREMENT,
    variant_id INTEGER,
    marvel_link TEXT,
    marvel_unlimited_link TEXT,
    amazon_link TEXT,
    comic_cover_link TEXT,
    comic_cover_path TEXT DEFAULT '',
    is_original_commission TEXT,
    commission_image_url TEXT,
    commission_image_path TEXT,
    comic_title TEXT,
    comic_year INTEGER,
    issue_number TEXT,
    FOREIGN KEY (variant_id) REFERENCES variants (variant_id)                      |

## Website Overview

The Marvel Snap Comic Cover Art Variants website aims to educate and entertain Marvel Snap players by showcasing the comic book origins of in-game variants. Key features include:

* **Variant Showcase:**
    * Displays Marvel Snap variants alongside their corresponding comic book cover art.
* **Card and Variant Data:**
    * Fetches card and variant data from the Marvel Snap Zone API.
* **Comic Book Origins:**
    * Displays links and information related to the comic book origins of the variants.
* **Search and Filtering:**
    * Allows users to search and filter cards and variants.
* **Image Galleries:**
    * Provides image galleries to compare in-game variants with their comic cover art sources.
* **Educational Content:**
    * Includes information about the comic book origins of each variant.

## Getting Started

1.  **Clone the Repository:**
    * `git clone [repository URL]`
2.  **Install Dependencies:**
    * `pip install Flask requests Pillow tqdm`
3.  **Run the Application:**
    * `python app.py`
4.  **Open in Browser:**
    * Open your web browser and navigate to `http://127.0.0.1:5000/`.

## Future Improvements

* Enhance the display of comic book origin information.
* Improve the image galleries and comparison features.
* Enhance the UI/UX for a more engaging experience.
* Incorporate user feedback and suggestions.
* Add ability to view individual card and variant details.