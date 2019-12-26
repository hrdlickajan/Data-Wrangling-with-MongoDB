"""Loads restaurant collection from Atlas MongoDB and finds longitude and
latitude for each record"""
from pymongo import MongoClient
from geopy.geocoders import Nominatim
from tqdm import tqdm
import time

mongo_client = MongoClient("mongodb://analytics:analytics-password@test-shard"
                           "-00-00-03ow6.mongodb.net:27017,test-shard-00-01-0"
                           "3ow6.mongodb.net:27017,test-shard-00-02-03ow6.mong"
                           "odb.net:27017/test?ssl=true&replicaSet=test-shard"
                           "-0&authSource=admin&retryWrites=true&w=majority")


def main():
    mongo_db = mongo_client.get_database("dmdb_project")
    restaurants = mongo_db.restaurants
    geolocator = Nominatim(user_agent='restaurants', timeout=30,
                           country_bias="US")  # all restaurants are in the US

    # show progress bar in command prompt
    progress_loop = tqdm(total=restaurants.count({}), position=0, leave=False)

    for restaurant in restaurants.find():
        progress_loop.set_description("Getting latitudes and longitutes")
        # find the city directly in openstreetmaps to prevent dualities
        geocode_response = geolocator.geocode(restaurant["city"])
        time.sleep(1)  # delay between each request to avoid 429 response
        location = geolocator.geocode(restaurant["address"] + ", "
                                      + str(geocode_response))
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


if __name__ == "__main__":
    main()
