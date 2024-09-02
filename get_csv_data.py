# Script by Maverick CHARDET
# MIT License

# Parameters
NAME_LANGUAGES = ["en", "fr"]
ABILITIES_LANGUAGES = ["en", "fr"]
MAIN_LANGUAGE = "en"
GROUP_SUBTYPES = False
INCLUDE_WEB_ASSETS = False

CARDS_DATA_PATH = "results/cards.json"
FACTIONS_DATA_PATH = "results/factions.json"
TYPES_DATA_PATH = "results/types.json"
SUBTYPES_DATA_PATH = "results/subtypes.json"
RARITIES_DATA_PATH = "results/rarities.json"
CSV_OUTPUT_PATH = "results/cards_" + MAIN_LANGUAGE + ".csv"

# Imports
import os
import csv
import itertools
from utils import load_json

def main():
    if not os.path.exists(CARDS_DATA_PATH):
        print(f"File {CARDS_DATA_PATH} not found. Have you run get_cards_data.py?")
        return
    if not os.path.exists(FACTIONS_DATA_PATH):
        print(f"File {FACTIONS_DATA_PATH} not found. Have you run get_cards_data.py?")
        return
    if not os.path.exists(TYPES_DATA_PATH):
        print(f"File {TYPES_DATA_PATH} not found. Have you run get_cards_data.py?")
        return
    if not os.path.exists(SUBTYPES_DATA_PATH):
        print(f"File {SUBTYPES_DATA_PATH} not found. Have you run get_cards_data.py?")
        return
    if not os.path.exists(RARITIES_DATA_PATH):
        print(f"File {RARITIES_DATA_PATH} not found. Have you run get_cards_data.py?")
        return
    
    data = load_json(CARDS_DATA_PATH)
    factions = load_json(FACTIONS_DATA_PATH)
    types = load_json(TYPES_DATA_PATH)
    subtypes = load_json(SUBTYPES_DATA_PATH)
    rarities = load_json(RARITIES_DATA_PATH)

    cards_dicts = []
    subtypes_cols = {}
    if not GROUP_SUBTYPES:
        subtypes_cols = get_subtypes_cols(data)
    
    for card in data.values():
        card_id = card["id"]
        card_dict = {
            "collectorNumber": card["collectorNumberFormatted"][MAIN_LANGUAGE],
            "id": card_id,
            "type": types[card["type"]][MAIN_LANGUAGE],
            "faction": factions[card["mainFaction"]][MAIN_LANGUAGE],
            "rarity": rarities[card["rarity"]][MAIN_LANGUAGE],
            "imagePath": card["imagePath"][MAIN_LANGUAGE],
        }
        if GROUP_SUBTYPES:
            card_dict["subtypes"] = ", ".join(sorted([subtypes[subtype][MAIN_LANGUAGE] for subtype in card["subtypes"]]))
        else:
            for subtype in card["subtypes"]:
                card_dict["subtype_" + str(subtypes_cols[subtype]+1)] = subtypes[subtype][MAIN_LANGUAGE]
        if "elements" in card:
            if "MAIN_COST" in card["elements"]:
                card_dict["handCost"] = card["elements"]["MAIN_COST"]
            if "RECALL_COST" in card["elements"]:
                card_dict["reserveCost"] = card["elements"]["RECALL_COST"]
            if "FOREST_POWER" in card["elements"]:
                card_dict["forestPower"] = card["elements"]["FOREST_POWER"]
            if "MOUNTAIN_POWER" in card["elements"]:
                card_dict["mountainPower"] = card["elements"]["MOUNTAIN_POWER"]
            if "OCEAN_POWER" in card["elements"]:
                card_dict["waterPower"] = card["elements"]["OCEAN_POWER"]
            if "PERMANENT" in card["elements"]:
                card_dict["landmarksSize"] = card["elements"]["PERMANENT"]
            if "RESERVE" in card["elements"]:
                card_dict["reserveSize"] = card["elements"]["RESERVE"]
            if "MAIN_EFFECT" in card["elements"]:
                for language in ABILITIES_LANGUAGES:
                    card_dict["abilities" + "_" + language] = card["elements"]["MAIN_EFFECT"][language]
            if "ECHO_EFFECT" in card["elements"]:
                for language in ABILITIES_LANGUAGES:
                    card_dict["supportAbility" + "_" + language] = card["elements"]["ECHO_EFFECT"][language]
        for language in NAME_LANGUAGES:
            card_dict["name" + "_" + language] = card["name"][language]
        if INCLUDE_WEB_ASSETS:
            card_dict["webAsset0"] = None
            card_dict["webAsset1"] = None
            card_dict["webAsset2"] = None
            if "WEB" in card["assets"]:
                if len(card["assets"]["WEB"]) > 0:
                    card_dict["webAsset0"] = card["assets"]["WEB"][0]
                if len(card["assets"]["WEB"]) > 1:
                    card_dict["webAsset1"] = card["assets"]["WEB"][1]
                if len(card["assets"]["WEB"]) > 2:
                    card_dict["webAsset2"] = card["assets"]["WEB"][2]
        cards_dicts.append(card_dict)
    
    fieldnames = ["collectorNumber"]
    for language in NAME_LANGUAGES:
        fieldnames.append("name_" + language)
    fieldnames += ["faction", "rarity", "type"]
    if GROUP_SUBTYPES:
        fieldnames.append("subtypes")
    else:
        try:
            for i in range(max(subtypes_cols.values()) + 1):
                fieldnames.append("subtype_" + str(i+1))
        except:
            pass
    fieldnames += ["handCost", "reserveCost", "forestPower", "mountainPower", "waterPower", "landmarksSize", "reserveSize"]
    for language in ABILITIES_LANGUAGES:
        fieldnames += ["abilities_" + language, "supportAbility_" + language]
    fieldnames += ["id", "imagePath"]
    if INCLUDE_WEB_ASSETS:
        fieldnames += ["webAsset0", "webAsset1", "webAsset2"]
    
    with open(CSV_OUTPUT_PATH, 'w', newline='', encoding="utf8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for card_dict in sorted(cards_dicts, key=custom_sort):
            writer.writerow(card_dict)

def custom_sort(card):
    beforeRarity = card["collectorNumber"][:-4]
    afterRarity = card["collectorNumber"][-3:]
    rarity = card["collectorNumber"][-4]
    fixedRarity = rarity if rarity != "R" else "D"
    return beforeRarity + fixedRarity + afterRarity

def get_subtypes_cols(data):
    subtypes_counts = {}
    subtypes_incompatibilities = set()
    for card in data.values():
        for subtype in card["subtypes"]:
            if subtype not in subtypes_counts:
                subtypes_counts[subtype] = 0
            subtypes_counts[subtype] += 1
        for comb in itertools.combinations(card["subtypes"], 2):
            subtypes_incompatibilities.add(comb)
    ordered_subtypes = sorted(subtypes_counts, key=lambda x: subtypes_counts[x], reverse=True)
    subtypes_cols = {}
    for subtype in ordered_subtypes:
        col = 0
        while col in [subtypes_cols[other] for other in subtypes_cols if tuple(sorted((subtype, other))) in subtypes_incompatibilities]:
            col += 1
        subtypes_cols[subtype] = col
    return subtypes_cols

if __name__ == "__main__":
    main()
