"""Load restaurants from Atlas MongoDB and create a marker on a map for each
restaurant with latitude and longitude found. Save map as html
"""
from pymongo import MongoClient
import folium
from folium.plugins import MarkerCluster
import argparse

client = MongoClient("mongodb://analytics:analytics-password@test-shard-00-00-"
                     "03ow6.mongodb.net:27017,test-shard-00-01-03ow6.mongodb"
                     ".net:27017,test-shard-00-02-03ow6.mongodb.net:27017/te"
                     "st?ssl=true&replicaSet=test-shard-0&authSource=admin&r"
                     "etryWrites=true&w=majority")
map_path = "data/restaurants_map.html"

parser = argparse.ArgumentParser(description="Loads latitudes and longitudes "
                                 + " from selected database and puts a marker "
                                 + "on a .html map")

parser.add_argument('database_name', type=str,
                    help="Database name on Atlas MongoDB to load records from")
args = parser.parse_args()


def main(database_name):
    db = client.get_database(database_name)
    restaurants = db.restaurants
    if restaurants.count_documents({}) == 0:
        print("Collection \"restaurants\" does not exist in database \""
              + database_name + "\"")
        return
    map = folium.Map(location=[35, -100], zoom_start=5)  # default zoom into US
    marker_cluster = MarkerCluster()  # create clusters for markers near

    visualized_restaurants = []
    for restaurant in restaurants.find({"latitude": {"$exists": True}}):

        latitude = restaurant["latitude"]
        longitude = restaurant["longitude"]
        name = restaurant["name"]
        type = restaurant["type"]
        # do not show the same restaurant twice
        if (latitude, longitude, name) in visualized_restaurants:
            continue

        # add restaurant to a cluster
        marker_cluster.add_child(folium.Marker([latitude, longitude],
                                               popup="<strong>" + name
                                               + "</strong >\n " + type,
                                               icon=folium.Icon(icon="cutlery",
                                                                prefix='fa'),
                                               tooltip="<strong>" + name
                                               + "</strong>"))

        visualized_restaurants.append((latitude, longitude, name))

    marker_cluster.add_to(map)
    map.save(map_path)  # save map


if __name__ == "__main__":
    main(args.database_name)
