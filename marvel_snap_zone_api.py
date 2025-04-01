"""
This module handles interactions with the Marvel Snap Zone API, including fetching
card data and downloading card images.
"""

import os
import requests
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
from tqdm import tqdm
from config import CARDS_API_URL

def get_cards(url: str = CARDS_API_URL):
    """Retrieves a list of card data from the Marvel Snap Zone API."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        cards = response.json().get("success", {}).get("cards", [])
        return [{
            'cid': card.get('cid'),
            'name': card.get('name'),
            'type': card.get('type'),
            'cost': card.get('cost'),
            'power': card.get('power'),
            'ability': card.get('ability'),
            'flavor': card.get('flavor'),
            'art': card.get('art'),
            'alternate_art': card.get('alternate_art'),
            'url': card.get('url'),
            'status': card.get('status'),
            'carddefid': card.get('carddefid'),
            'variants': card.get('variants')
        } for card in cards]
    except requests.exceptions.RequestException as e:
        print(f"Error: API request failed: {e}")
        return []

def create_directories():
    """Creates the static/images directory for the card images."""
    image_dir = os.path.join("static", "images")
    if not os.path.exists(image_dir):
        os.makedirs(image_dir)
        print("Created static/images directory.")
    else:
        print("static/images directory already exists")

def download_images(card_data):
    """Downloads card images from the Marvel Snap Zone API."""
    if not card_data:
        print("No card data to download images for.")
        return

    create_directories()  # Ensure the directory exists

    urls = [card['art'] for card in card_data if card.get('art')]  # Extract image URLs

    print(f"Downloading {len(urls)} images.") # added print statement

    overall_progress = tqdm(total=len(urls), unit=' URL')

    def download_image(url):
        """Downloads a single image from a URL."""
        temp_file_path = None  # Initialize temp_file_path

        try:
            file_name = url.rsplit('/', 1)[-1].rsplit('?', 1)[0]
            file_path = os.path.join("static", "images", file_name)
            png_file_path = os.path.splitext(file_path)[0] + ".png"

            if os.path.exists(png_file_path):
                overall_progress.update(1)
                return

            temp_file_path = file_path + ".webp"
            with open(temp_file_path, 'wb') as file:
                response = requests.get(url, stream=True)
                response.raise_for_status()
                for data in response.iter_content(1024):
                    file.write(data)

            image = Image.open(temp_file_path)
            image.save(png_file_path, "PNG")
            overall_progress.update(1)

            print(f"Downloaded: {url}") # added print statement

        except requests.exceptions.RequestException:
            overall_progress.update(1)

        finally:
            if temp_file_path and os.path.exists(temp_file_path):  # Check if defined and exists
                os.remove(temp_file_path)

    with ThreadPoolExecutor(max_workers=5) as executor:
        for url in urls:
            executor.submit(download_image, url)

    overall_progress.close()