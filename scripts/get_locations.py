"""Loads restaurant collection from Atlas MongoDB and finds longitude and
latitude for each record"""
from pymongo import MongoClient
from geopy.geocoders import Nominatim
from tqdm import tqdm
import time
from geopy.exc import GeocoderServiceError
import argparse

mongo_client = MongoClient("mongodb://analytics:analytics-password@test-shard"
                           "-00-00-03ow6.mongodb.net:27017,test-shard-00-01-0"
                           "3ow6.mongodb.net:27017,test-shard-00-02-03ow6.mong"
                           "odb.net:27017/test?ssl=true&replicaSet=test-shard"
                           "-0&authSource=admin&retryWrites=true&w=majority")

parser = argparse.ArgumentParser(description="Gets latitudes and longitudes "
                                 + " from OpenStreetMap and saves them to "
                                 + "selected database")

parser.add_argument('database_name', type=str,
                    help="Database name on Atlas MongoDB to update records in")
args = parser.parse_args()


# prevent time out - call this function until it returns location
def get_osm_response(address, geolocator):
    try:
        return geolocator.geocode(address)
    except GeocoderServiceError:
        time.sleep(1)
        return get_osm_response(address, geolocator)


def main(database_name):
    mongo_db = mongo_client.get_database(database_name)
    restaurants = mongo_db.restaurants
    if restaurants.count_documents({}) == 0:
        print("Collection \"restaurants\" does not exist in database \""
              + database_name + "\"")
        return
    geolocator = Nominatim(user_agent='restaurants', timeout=50,
                           country_bias="US")  # all restaurants are in the US

    # show progress bar in command prompt
    progress_loop = tqdm(total=restaurants.count({}), position=0, leave=False)

    for restaurant in restaurants.find():
        progress_loop.set_description("Getting latitudes and longitutes")
        # try to find the city directly in openstreetmap to prevent dualities
        geocode_response = get_osm_response(restaurant["city"], geolocator)
        time.sleep(1)  # delay between each request to avoid 429 response
        location = get_osm_response(restaurant["address"] + ", "
                                    + str(geocode_response), geolocator)
        time.sleep(1)
        progress_loop.update(1)
        if location is None:
            restaurants.update_one(restaurant, {"$set": {
                                                "geocode_city_response": str(
                                                    geocode_response)}})
            continue

        restaurants.update_one(restaurant, {"$set": {
                                            "latitude": location.latitude,
                                            "longitude": location.longitude,
                                            "geocode_city_response": str(
                                                geocode_response)}})
    progress_loop.close()

    print("Restaurants without coordinates: "
          + str(restaurants.count({"latitude": {"$exists": False}})))


if __name__ == "__main__":
    main(args.database_name)
