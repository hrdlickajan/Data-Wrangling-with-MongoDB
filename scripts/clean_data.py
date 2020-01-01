"""Download tsv file with restaurants, clean it, find duplicates in it
and upload it to Atlas MongoDB if it does not already exist
"""
import pandas as pd
import os
import bs4
import requests
import shutil
import re
from jellyfish import jaro_winkler
from pymongo import MongoClient
import argparse

parser = argparse.ArgumentParser(description='Downloads .tsv files from \
https://hpi.de/. Cleans restaurant dataset and saves it as .tsv file. \
Finds duplicate pairs and saves them to .tsv file. \
Uploads clean .tsv to Atlas MongoDB, argument is collection name.')

parser.add_argument('database_name', type=str,
                    help='Database name on Atlas MongoDB, create new if it \
                    does not exist.')
args = parser.parse_args()

dataset_path = "data/restaurants.tsv"
ndpl_path = "data/restaurants_NDPL.tsv"
gold_path = "data/restaurants_DPL.tsv"
clean_file_path = "data/restaurants_clean_dupl.tsv"
duplicates_path = "data/restaurants_duplicates.tsv"
special_chars_pattern = re.compile(r"[\./&\'()--]")

names_map = {"ave": "avenue",
             "aves": "avenues",
             "blv": "boulevard",
             "blvd": "boulevard",
             "dr": "drive",
             "e": "east",
             "fl": "floor",
             "hwy": "highway",
             "ln": "line",
             "n": "north",
             "ne": "north east",
             "nw": "north west",
             "pch": "pacific coast highway",
             "pkwy": "parkway",
             "pl": "place",
             "rd": "road",
             "s": "south",
             "se": "south east",
             "sq": "square",
             "st": "street",
             "sts": "streets",
             "w": "west"}

cities_map = {"new york": "new york city",
              "la": "los angeles"}

words_to_remove = ["traditional", "new", "wave", "classic", "bar", "shop",
                   "shops", "diner", "soul", "bistro", "nuova", "cucina",
                   "nan", "or", "and"]


def load_from_tsv():
    """Loads downloaded tsv with restaurants as pandas DataFrame"""
    df = pd.read_csv(dataset_path, sep='\t')
    return df.to_dict('restaurants')


def update_phone(phone_number):
    """Updates restaurant phone number to unified format
    update_phone("123 4 5 6  7890") returns "1 234 567 890"
    """
    numbers = phone_number.replace(" ", "")

    return "%s %s %s %s" % (numbers[0], numbers[1:4],  numbers[4:7],
                            numbers[7:10])


def update_address(adress):
    """Updates restaurant address. Replaces shortcuts with full words and
    gets rid of meaningless words"""
    new_address = []
    words = adress.split()
    if len(words) == 1:
        return ""
    for word in words:
        if word in names_map:
            word = names_map[word]  # replace shortcuts with full words
        if word in ["between", "near", "at", "off"]:
            # the information after these words is useless so do not append it
            break
        if word in ["in"]:  # "in" is meaningless word so do not append it
            continue
        new_address.append(word)
    return " ".join(new_address)


def update_city(city):
    """Maps old restaurant city name to a new, correct one"""
    if city.startswith("w ") or city.startswith("west "):
        # get rid of "w " or " west" at the start of the string
        new_city = " ".join(city.split()[1:])
    else:
        new_city = city
    if new_city in cities_map:
        new_city = cities_map[new_city]  # map old name to a new name
    return new_city


def update_type(restaurant_type):
    """Updates restaurant type by getting rid of useless words/numbers"""
    new_description = []  # new description to append words to
    words = restaurant_type.split()
    for word in words:
        if not (word in words_to_remove or is_number(word)):
            # skip append of useless word or number
            new_description.append(word)
    return " ".join(new_description)


def is_number(s):
    """Check if provided string is a number or not"""
    try:
        float(s)
        return True
    except ValueError:
        return False


def clean_tsv(restaurants):
    """Cleans provided tsv by updating phone, address, type and city"""
    print("Cleaning data")
    for record in restaurants:
        for key, value in record.items():
            # get rid of & ' - ( ) . in all fields - replace with a space
            value = re.sub(special_chars_pattern, " ", str(value))
            if key == "phone":
                value = update_phone(value)
            if key == "address":
                value = update_address(value)
            if key == "type":
                value = update_type(value)
            if key == "city":
                value = update_city(value)

            value = " ".join(value.split())  # remove multiple whitespaces
            record[key] = value
    return restaurants


def download_tsv_files():
    """Download three .tsv files from hpi.de and save them into folder "data"
    first file - dirty tsv file with restaurants
    second file - list of restaurant duplicates
    third file - list of non duplicates pairs
    """
    base_url = "https://hpi.de/"
    os.makedirs('data', exist_ok=True)  # store .tsv in folder 'data'
    url = base_url + "naumann/projects/repeatability/datasets/" \
        "restaurants-dataset.html"  # url containing TSV file
    print('Downloading TSV files from ' + url)
    res = requests.get(url)
    res.raise_for_status()
    soup = bs4.BeautifulSoup(res.text, features="html.parser")
    tsv_urls = soup.find_all("a", href=True, class_="download")

    dataset_url = tsv_urls[0]["href"]
    dpl_url = tsv_urls[2]["href"]
    ndpl_url = tsv_urls[4]["href"]

    download_url(base_url + dataset_url, dataset_path)
    download_url(base_url + dpl_url, gold_path)
    download_url(base_url + ndpl_url, ndpl_path)
    return os.path.exists(dataset_path) and os.path.exists(gold_path) and \
        os.path.exists(ndpl_path)


def download_url(url, path):
    """Download url to a specified path"""
    response = requests.get(url, stream=True)
    with open(path, 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)
    del response


def upload_to_mongo(restaurants, database_name):
    """Upload dictionary with restaurant records to Atlas, create a new database
    "dmdb_project" and a collection named "restaurants". Skip the upload if
    the database already exists.
    """
    print("Uploading to Atlas MongoDB")
    mongo_client = MongoClient("mongodb://analytics:analytics-password@test-"
                               "shard-00-00-03ow6.mongodb.net:27017,test-sh"
                               "ard-00-01-03ow6.mongodb.net:27017,test-shar"
                               "d-00-02-03ow6.mongodb.net:27017/test?ssl=tr"
                               "ue&replicaSet=test-shard-0&authSource=admin"
                               "&retryWrites=true&w=majority")
    database = mongo_client[database_name]
    restaurants_collection = database.restaurants
    if restaurants_collection.count_documents({}) == 0:
        restaurants_collection.insert(restaurants)
        print("Created a new database \"" + database_name + "\" and collection"
              + " \"restaurants\". Uploaded "
              + str(restaurants_collection.count_documents({})) + " records")
    else:
        print("Database \"" + database_name + "\" and collection "
              + "\"restaurants\" already exists, no record inserted")


def save_locally(restaurants):
    """Save restaurant tsv file to hard drive"""
    print("Saving clean TSV locally to " + clean_file_path)
    df = pd.DataFrame(restaurants)
    df.to_csv(clean_file_path, sep='\t', encoding="utf-8", index=False)


def find_duplicates(restaurants_clean):
    """Find duplicate records and save them to tsv file"""
    print("Finding duplicates")
    duplicate_list_id1 = []
    duplicate_list_id2 = []
    for restaurant in restaurants_clean:
        phone_number = restaurant["phone"]
        name = restaurant["name"]
        id = restaurant["id"]
        # mark as duplicate when same phone numbers and similar name
        duplicate = list(filter(lambda duplicate_restaurant:
                                duplicate_restaurant['phone'] == phone_number
                                and jaro_winkler(duplicate_restaurant["name"],
                                                 name) > 0.7
                                and duplicate_restaurant['id'] != id,
                                restaurants_clean))
        # add to list if both records do not already have a duplicate
        if (len(duplicate) > 0 and id not in duplicate_list_id1 and
                id not in duplicate_list_id2):
            duplicate_list_id1.append(id)
            duplicate_list_id2.append(duplicate[0]["id"])

    df = pd.DataFrame(list(zip(duplicate_list_id1, duplicate_list_id2)),
                      columns=["id1", "id2"])
    df.to_csv(duplicates_path, sep='\t', index=False)  # save as tsv
    return os.path.exists(duplicates_path)


def main(database_name):
    if not download_tsv_files():
        print("TSV file not downloaded correctly")
        return
    restaurants = load_from_tsv()
    restaurants_clean = clean_tsv(restaurants)
    save_locally(restaurants_clean)
    if not find_duplicates(restaurants_clean):
        print("File with duplicates was not created")
    else:
        print("File with duplicates saved to " + duplicates_path)
    upload_to_mongo(restaurants_clean, database_name)


if __name__ == "__main__":
    main(args.database_name)
