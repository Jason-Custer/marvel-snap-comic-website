"""
This module handles interactions with the Marvel Snap Zone API, including fetching
card data and downloading card images.
"""

import os
import requests
import logging
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
from tqdm import tqdm
from config import CARDS_API_URL, CARDS_IMAGE_DIR, VARIANTS_IMAGE_DIR

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_cards(url: str = CARDS_API_URL):
    """Retrieves a list of card data from the Marvel Snap Zone API."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        if response.text:
            try:
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
                    'url': card.get('url'), #keep url, if you have a use for it.
                    'status': card.get('status'),
                    'carddefid': card.get('carddefid'),
                    'variants': card.get('variants')
                } for card in cards]
            except requests.exceptions.JSONDecodeError as e:
                logging.error(f"Error: Could not decode JSON response: {e}")
                return []
        else:
            logging.error("Error: Empty response from API.")
            return []

    except requests.exceptions.RequestException as e:
        logging.error(f"Error: API request failed: {e}")
        return []

def download_images(card_data):
    """Downloads card images to CARDS_IMAGE_DIR."""
    # ... (Your download_images() function remains the same)
    if not card_data:
        print("No card data to download images for.")
        return

    image_dir = CARDS_IMAGE_DIR
    if not os.path.exists(image_dir):
        os.makedirs(image_dir)
        print(f"Created {image_dir} directory.")
    else:
        print(f"{image_dir} directory already exists.")

    urls = [card['art'] for card in card_data if card.get('art')]

    print(f"Downloading {len(urls)} images to {image_dir}.")

    overall_progress = tqdm(total=len(urls), unit=' URL')

    def download_image(url):
        """Downloads a single image from a URL."""
        temp_file_path = None

        try:
            file_name = url.rsplit('/', 1)[-1].rsplit('?', 1)[0]
            file_path = os.path.join(image_dir, file_name)
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

            print(f"Downloaded: {url}")

        except requests.exceptions.RequestException:
            overall_progress.update(1)

        finally:
            if temp_file_path and os.path.exists(temp_file_path):
                os.remove(temp_file_path)

    with ThreadPoolExecutor(max_workers=5) as executor:
        for url in urls:
            executor.submit(download_image, url)

    overall_progress.close()

def download_variants(cards):
    """Downloads variant images from Marvel Snap Zone and converts them to PNG."""
    os.makedirs(VARIANTS_IMAGE_DIR, exist_ok=True)
    for card in cards:
        if card['variants']:
            for variant in card['variants']:
                image_url = variant.get('art')
                image_filename = variant.get('art_filename')
                if image_url and image_filename:
                    webp_path = os.path.join(VARIANTS_IMAGE_DIR, image_filename.rsplit('?', 1)[0]) #download the webp.
                    png_path = os.path.splitext(webp_path)[0] + ".png" #set the png filename.

                    if not os.path.exists(png_path):
                        try:
                            response = requests.get(image_url, stream=True)
                            response.raise_for_status()
                            with open(webp_path, 'wb') as f:
                                for chunk in response.iter_content(chunk_size=8192):
                                    f.write(chunk)

                            # Convert WebP to PNG
                            try:
                                img = Image.open(webp_path)
                                img.save(png_path, "PNG")
                                os.remove(webp_path) #remove the webp file.
                                print(f"Downloaded and converted variant image: {png_path}")
                            except Exception as e:
                                print(f"Error converting {webp_path} to PNG: {e}")

                        except requests.exceptions.RequestException as e:
                            print(f"Error downloading variant image {image_url}: {e}")
                    else:
                        print(f"Variant image already exists: {png_path}")
                else:
                    print(f"Warning: Missing art or art_filename for variant of card CID: {card['cid']}")