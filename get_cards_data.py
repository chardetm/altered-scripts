# Script by Maverick CHARDET
# MIT License

# Parameters
LANGUAGES = ["en", "fr", "es", "it", "de"]
DUMP_TEMP_FILES = False
OUTPUT_FOLDER = "results"
TEMP_FOLDER = "temp"
INCLUDE_PROMO_CARDS = True
INCLUDE_UNIQUES = True
INCLUDE_KS = True
FORCE_INCLUDE_KS_UNIQUES = True # only relevant if INCLUDE_KS = False and INCLUDE_UNIQUES = True
INCLUDE_FOILERS = False

# Imports
import requests
from typing import Dict, List
from os.path import join
from utils import dump_json, create_folder_if_not_exists, LANGUAGE_HEADERS

# Constants
RARITY_PARAMS = "rarity[]=UNIQUE&rarity[]=COMMON&rarity[]=RARE"
if not INCLUDE_UNIQUES:
    RARITY_PARAMS = "rarity[]=COMMON&rarity[]=RARE"
CARDS_URL = f"https://api.altered.gg/cards?{RARITY_PARAMS}&itemsPerPage=10000"

def get_cards_data(language):
    response = requests.get(CARDS_URL, headers=LANGUAGE_HEADERS[language])
    if not response.ok:
        print(response)
    return response.json()

def treat_cards_data(data):
    cards = []
    types = {}
    subtypes = {}
    factions = {}
    rarities = {}
    for card in data["hydra:member"]:
        if not INCLUDE_FOILERS and "_FOILER_" in card["reference"]:
            continue
        if not INCLUDE_KS and "_COREKS_" in card["reference"]:
            if not INCLUDE_UNIQUES or not FORCE_INCLUDE_KS_UNIQUES or "_U_" not in card["reference"]:
                continue
        if not INCLUDE_PROMO_CARDS and card["reference"].startswith("ALT_CORE_P_"):
            # print(f"Skipping promo card {card['reference']}")
            continue # Promo card with missing stats
        cards.append({
            "id": card["reference"],
            "name": card["name"],
            "type": card["cardType"]["reference"],
            "subtypes": [subtype["reference"] for subtype in card["cardSubTypes"]],
            "imagePath": card["imagePath"],
            "assets": card["assets"],
            "mainFaction": card["mainFaction"]["reference"],
            "elements": card["elements"],
            "rarity": card["rarity"]["reference"],
            "collectorNumberFormatted": card["collectorNumberFormatted"]
        })
        types[card["cardType"]["reference"]] = card["cardType"]["name"]
        for subtype in card["cardSubTypes"]:
            subtypes[subtype["reference"]] = subtype["name"]
        factions[card["mainFaction"]["reference"]] = card["mainFaction"]["name"]
        rarities[card["rarity"]["reference"]] = card["rarity"]["name"]
    return cards, types, subtypes, factions, rarities

def merge_language_dicts(data: Dict[str, Dict[str, any]]):
    merged_dict = {}
    for language in data:
        for key in data[language]:
            if key not in merged_dict:
                merged_dict[key] = {}
            merged_dict[key][language] = data[language][key]
    return merged_dict

def merge_cards_data(data: Dict[str, List[Dict[str, any]]]):
    cards_lang_dict = {}
    all_cards_ids = set()
    for language in data:
        cards_lang_dict[language] = {}
        for card in data[language]:
            cards_lang_dict[language][card["id"]] = card
            all_cards_ids.add(card["id"])
    
    all_cards = {}
    for card_id in all_cards_ids:
        card = {}
        for language in data:
            if card_id not in cards_lang_dict[language]:
                print(f"Card {card_id} not found in {language}")
                continue
            current_card_lang = cards_lang_dict[language][card_id]
            for property in ["id", "type", "subtypes", "assets", "mainFaction", "rarity"]:
                add_property_or_ensure_identical(card, property, current_card_lang[property])
            for property in ["name", "imagePath", "collectorNumberFormatted"]:
                if property not in card:
                    card[property] = {}
                card[property][language] = current_card_lang[property]
            if "elements" not in card:
                card["elements"] = {}
            for property in current_card_lang["elements"]:
                if "EFFECT" in property:
                    if property not in card["elements"]:
                        card["elements"][property] = {}
                    card["elements"][property][language] = current_card_lang["elements"][property]
                else:
                    value = current_card_lang["elements"][property]
                    if "COST" in property or "POWER" in property or property in ["PERMANENT", "RESERVE"]:
                        value = int(value) if value != "" else None
                    add_property_or_ensure_identical(card["elements"], property, value)
        all_cards[card_id] = card
    return all_cards

def add_property_or_ensure_identical(card, property_name, property_value):
    if property_name in card:
        if card[property_name] != property_value:
            print(f"Property {property_name} is different for card {card['id']}: {card[property_name]} != {property_value}")
    else:
        card[property_name] = property_value

def main():
    create_folder_if_not_exists(OUTPUT_FOLDER)
    if DUMP_TEMP_FILES:
        create_folder_if_not_exists(TEMP_FOLDER)

    treated_cards = {}
    treated_types = {}
    treated_subtypes = {}
    treated_factions = {}
    treated_rarities = {}
    for language in LANGUAGES:
        print("Importing data for language " + language)
        raw_data = get_cards_data(language)
        if DUMP_TEMP_FILES:
            dump_json(raw_data, join(TEMP_FOLDER, 'raw_data_' + language + '.json'))
        tcards, ttypes, tsubtypes, tfactions, trarities = treat_cards_data(raw_data)
        if DUMP_TEMP_FILES:
            dump_json(tcards   , join(TEMP_FOLDER, 'cards_' + language + '.json'))
            dump_json(ttypes   , join(TEMP_FOLDER, 'types_' + language + '.json'))
            dump_json(tsubtypes, join(TEMP_FOLDER, 'subtypes_' + language + '.json'))
            dump_json(tfactions, join(TEMP_FOLDER, 'factions_' + language + '.json'))
            dump_json(trarities, join(TEMP_FOLDER, 'rarities_' + language + '.json'))
        treated_cards[language] = tcards
        treated_types[language] = ttypes
        treated_subtypes[language] = tsubtypes
        treated_factions[language] = tfactions
        treated_rarities[language] = trarities

    cards    = merge_cards_data(treated_cards)
    types    = merge_language_dicts(treated_types)
    subtypes = merge_language_dicts(treated_subtypes)
    factions = merge_language_dicts(treated_factions)
    rarities = merge_language_dicts(treated_rarities)
    dump_json(cards,    join(OUTPUT_FOLDER, 'cards.json'))
    dump_json(types,    join(OUTPUT_FOLDER, 'types.json'))
    dump_json(subtypes, join(OUTPUT_FOLDER, 'subtypes.json'))
    dump_json(factions, join(OUTPUT_FOLDER, 'factions.json'))
    dump_json(rarities, join(OUTPUT_FOLDER, 'rarities.json'))

if __name__ == "__main__":
    main()
