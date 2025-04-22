# Marvel Snap Comic Cover Art Variants

This project is a web application designed to highlight the connection between Marvel Snap in-game variants and classic Marvel comic book cover art. It fetches card data and variant information from the Marvel Snap Zone API, emphasizing the comic origins of these variants.

## File Structure

marvel-snap-project/
├── app.py              # Flask application logic (routes, data retrieval)
├── config.py           # Configuration settings (API URLs, database path)
├── database_manager.py # Database interaction (SQLite - single database file)
├── marvel_snap_zone_api.py # API interaction (card data and variant retrieval, image downloads)
├── static/
│   ├── images/
│   │   ├── cards/       # Card images
│   │   └── variants/    # Variant images (comic cover art)
│   ├── script.js        # Client-side JavaScript logic
│   └── style.css         # CSS styles
├── templates/
│   └── index.html      # HTML template for the main page
├── snap_data.db        # SQLite database for cards, variants, and comics data
└── README.md

## File Descriptions

* **`app.py`:**
    * Main Flask application file; handles routes, data retrieval, and rendering.
* **`config.py`:**
    * Stores configuration settings like API URLs and the path to the single database file (`snap_data.db`).
* **`database_manager.py`:**
    * Manages database interactions (SQLite), including card, variant, and comic data storage and retrieval within the single database file.
* **`marvel_snap_zone_api.py`:**
    * Interacts with the Marvel Snap Zone API to fetch card and variant data and download images.
* **`static/images/cards/`:**
    * Stores standard card images.
* **`static/images/variants/`:**
    * Stores variant images, focusing on comic cover art.
* **`static/script.js`:**
    * Client-side JavaScript for search, filtering, and dynamic content updates.
* **`static/style.css`:**
    * CSS stylesheets for website design.
* **`templates/index.html`:**
    * HTML template for the main page, using Jinja2 for dynamic content.
* **`snap_data.db`:**
    * SQLite database containing tables for card data, variant data, and comic link information.
* **`README.md`:**
    * Documentation for the project.

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