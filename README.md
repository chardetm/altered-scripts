# Altered scripts

**By:** Maverick Chardet

**License:** MIT

**Contact:** `maverick_fr` on Discord

## Files

- `README.md`: This file
- `get_cards_data.py`: Script to download the cards data using the official
Altered API
- `get_card_images.py`: Script to download the card images from the official
Altered wbesite using the results from `get_cards_data.py`
- `utils.py`: Utility functions used by the other scripts

## Getting cards data

To get the cards data, run the following command:

```bash
python get_cards_data.py
```

By default, the script will download the data to the `results` directory. The
data for all languages is aggregated in a single file.

### Parameters

It is possible to change some parameters at the beginning of the script. In
particular, you can list only the languages you are interested in by changing
the `LANGUAGES` variable.

## Getting card images

**Note:** This script requires the results from `get_cards_data.py`. Make sure
to run `get_cards_data.py` first.

To get the card images, run the following command:

```bash
python get_card_images.py
```

By default, the script will download the card images to the `card_images`
directory, in one subfolder for each language. By default, the name of the
files will be the card collector number (e.g. `BTG-036-C.jpg`). Additionally,
the script will download image assets related to the card to the `card_assets`
directory. By default, the images will not be redownloaded if they already
exist.

### Parameters

It is possible to change some parameters at the beginning of the script. In
particular, you can list only the languages you are interested in by changing
the `LANGUAGES` variable. You may also choose which format to use for the
card image names by changing the `USE_COLLECTOR_NUMBERS` variable. You may also
choose whether to download the card images and/or the card assets by changing
the `DOWNLOAD_CARD_IMAGES` and `DOWNLOAD_ASSETS` variables. You may also force
redownloading the images by changing the `FORCE_REDOWNLOAD` variable.

## Getting cards data as CSV

**Note:** This script requires the results from `get_cards_data.py`. Make sure
to run `get_cards_data.py` first.

To get the cards data as a CSV file, run the following command:

```bash
python get_csv_data.py
```

By default, the script will write the CSV file in the `results`
directory, with the name `cards_XX.csv` where `XX` is the main language code.

### Parameters

It is possible to change some parameters at the beginning of the script. In
particular, you can list only the languages you are interested in by changing
the `NAME_LANGUAGES` and `ABILITIES_LANGUAGES` variables. You may also choose
the language to use for the types, subtypes, and rarities by changing the
`MAIN_LANGUAGE` variable. It is also possible to choose whether to group the
subtypes in a single column or to have one column per subtype by changing the
`GROUP_SUBTYPES` variable (defaults to `False`).

Note that if the subtypes are not grouped, the subtypes will span over
multiple columns. The column for each subtype is decided so that any one
subtype may appear in only one column. 
