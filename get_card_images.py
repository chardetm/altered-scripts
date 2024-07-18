# Script by Maverick CHARDET
# MIT License

# Parameters
LANGUAGES = ["en", "fr", "es", "it", "de"]
FORCE_REDOWNLOAD = False
DOWNLOAD_CARD_IMAGES = True
DOWNLOAD_ASSETS = False
USE_COLLECTOR_NUMBERS = False
CARDS_DATA_PATH = "results/cards.json"
CARD_IMAGES_FOLDER = "card_images"
CARD_ASSETS_FOLDER = "card_assets"

# Imports
import os
from utils import create_folder_if_not_exists, download_file, load_json

def main():
    if not DOWNLOAD_CARD_IMAGES and not DOWNLOAD_ASSETS:
        print("Nothing to do.")
        return
    
    if not os.path.exists(CARDS_DATA_PATH):
        print(f"File {CARDS_DATA_PATH} not found. Have you run get_cards_data.py?")
        return
    
    data = load_json(CARDS_DATA_PATH)

    if DOWNLOAD_CARD_IMAGES:
        create_folder_if_not_exists(CARD_IMAGES_FOLDER)
    if DOWNLOAD_ASSETS:
        create_folder_if_not_exists(CARD_ASSETS_FOLDER)
    
    for card in data.values():
        card_id = card["id"]
        i = 0

        if "imagePath" in card and DOWNLOAD_CARD_IMAGES:
            for language in card["imagePath"]:
                if language not in LANGUAGES:
                    continue
                create_folder_if_not_exists(f"{CARD_IMAGES_FOLDER}/{language}")
                path = f"{CARD_IMAGES_FOLDER}/{language}/{card_id}.jpg"
                if USE_COLLECTOR_NUMBERS:
                    number = card["collectorNumberFormatted"][language]
                    if "_COREKS_" in card["id"]:
                        number = number.replace("BTG", "BTGKS")
                    path = f"{CARD_IMAGES_FOLDER}/{language}/{number}.jpg"
                if FORCE_REDOWNLOAD or not os.path.exists(path):
                    result = download_file(card["imagePath"][language], path)
                    if not result:
                        print(f"Error downloading {card_id} ({language})")

        if "assets" in card and DOWNLOAD_ASSETS:
            for asset_type in card["assets"]:
                for asset_url in card["assets"][asset_type]:
                    split_url = asset_url.split('/')
                    file_name = split_url[-1]
                    if not file_name.endswith(".jpg") and not file_name.endswith(".png"):
                        print(f"Warning {asset_type}/{file_name} is related to card {card_id} but has a non-standard ending.")
                        if asset_type == "WEB":
                            file_name = f"{card_id}_XXX{i}_WEB.jpg"
                            i += 1
                            print(f"Renaming to {file_name}")
                    create_folder_if_not_exists(f"{CARD_ASSETS_FOLDER}/{asset_type}")
                    path = f"{CARD_ASSETS_FOLDER}/{asset_type}/{file_name}"

                    if FORCE_REDOWNLOAD or not os.path.exists(path):
                        download_file(asset_url, path)

if __name__ == "__main__":
    main()
