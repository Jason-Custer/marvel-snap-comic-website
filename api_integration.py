import os
import requests
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
from tqdm import tqdm

CARDS_API_URL = 'https://marvelsnapzone.com/getinfo/?searchtype=cards&searchcardstype=true'
LOCATIONS_API_URL = 'https://marvelsnapzone.com/getinfo/?searchtype=locations&searchcardstype=true'
ROOT_DIR = 'marvel-snap'
CARDS_DIR = 'cards'
VARIANTS_DIR = 'variants'
LOCATIONS_DIR = 'locations'

def get_cards(url: str = CARDS_API_URL):
    """
    Retrieves a list of card data from the Marvel SNAP Zone API.

    Returns:
        A list of dictionaries, where each dictionary represents a card's data.
    """
    try:
        response = requests.get(url) # Make a GET request to the API URL.
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx).

        json_data = response.json() # Parse the JSON response.
        success = json_data.get("success", {}) # Get the "success" part of the JSON.
        cards = success.get("cards", []) # Get the "cards" list from the "success" part.

        # Extract only the necessary data from each card.
        card_data = []
        for card in cards:
            card_data.append({
                'name': card.get('name'),
                'energy': card.get('cost'),
                'power': card.get('power'),
                'image': card.get('art')
            })
        return card_data
    except requests.exceptions.RequestException as e:
        print(f"Error: API request failed: {e}")
        return [] # Return an empty list in case of an error.

def download_images(urls, dir: str = ROOT_DIR):
    """
    Downloads images from the given URLs and stores them in the given directory.

    Args:
        urls: A list of URLs to download images from.
        dir: The directory to store the images in.
    """

    overall_progress = tqdm(total=len(urls), unit=' URL') # progress bar

    def download_image(url, dir: str = ROOT_DIR):
        try:
            file_name = url.rsplit('/', 1)[-1].rsplit('?', 1)[0] # get filename from url
            file_path = os.path.join(dir, file_name) # construct file path
            png_file_path = os.path.splitext(file_path)[0] + ".png" # construct png file path

            if os.path.exists(png_file_path): # if file exists, skip
                overall_progress.update(1)
                return

            temp_file_path = file_path + ".webp" # construct temp webp file path
            with open(temp_file_path, 'wb') as file: # open file for writing
                response = requests.get(url, stream=True) # get image data
                response.raise_for_status() # raise exception for bad status codes

                for data in response.iter_content(1024): # write image data to file
                    file.write(data)

            image = Image.open(temp_file_path) # open image
            image.save(png_file_path, "PNG") # save image as png
            overall_progress.update(1)

        except requests.exceptions.RequestException: # if error, skip
            overall_progress.update(1)

        finally:
            if os.path.exists(temp_file_path): # delete temp file
                os.remove(temp_file_path)

    with ThreadPoolExecutor(max_workers=5) as executor: # download images in parallel
        for url in urls:
            executor.submit(download_image, url, dir)

    overall_progress.close() # close progress bar

def create_directories():
    """
    Creates the directories for the card images.

    ROOT_DIR
    ├── CARDS_DIR
    ├── LOCATIONS_DIR
    └── VARIANTS_DIR

    """
    if not os.path.exists(ROOT_DIR): # create root directory if it doesn't exist
        os.mkdir(ROOT_DIR)

    directories = [CARDS_DIR, VARIANTS_DIR, LOCATIONS_DIR] # list of directories to create

    for directory in directories: # create directories
        path = os.path.join(ROOT_DIR, directory)
        if not os.path.exists(path):
            os.mkdir(path)

def download_card_images(card_data):
    """
    Downloads card images from the given card data.
    """
    create_directories() # create directories

    card_image_urls = [card['image'] for card in card_data] # get card image urls

    download_images(card_image_urls, os.path.join(ROOT_DIR, CARDS_DIR)) # download card images

if __name__ == '__main__':
    print("[%s] %s" % (datetime.now(), "Start downloading..."))
    cards = get_cards() # get card data from api

    download_card_images(cards)

    print("[%s] %s" % (datetime.now(), f"Finished downloading. Check '{ROOT_DIR}' directory."))
