"""Load restaurants from Atlas MongoDB and create a marker on a map for each
restaurant with latitude and longitude found. Save map as html
"""
from pymongo import MongoClient
import folium
from folium.plugins import MarkerCluster

client = MongoClient("mongodb://analytics:analytics-password@test-shard-00-00-"
                     "03ow6.mongodb.net:27017,test-shard-00-01-03ow6.mongodb"
                     ".net:27017,test-shard-00-02-03ow6.mongodb.net:27017/te"
                     "st?ssl=true&replicaSet=test-shard-0&authSource=admin&r"
                     "etryWrites=true&w=majority")


def main():
    db = client.get_database("dmdb_project")
    restaurants = db.restaurants

    restaurants_without_coordinates = 0

    m = folium.Map(location=[35, -100], zoom_start=5)  # default zoom into USA
    mc = MarkerCluster()  # create clusters for markers near eachother

    for restaurant in restaurants.find():
        if "latitude" not in restaurant:
            restaurants_without_coordinates += 1
            continue
        # add restaurant to a cluster
        mc.add_child(folium.Marker([restaurant["latitude"],
                                    restaurant["longitude"]],
                                   popup="<strong>" + restaurant["name"]
                                   + "</strong >\n " + restaurant["type"],
                                   icon=folium.Icon(icon="cutlery",
                                                    prefix='fa'),
                                   tooltip="<strong>" + restaurant["name"]
                                   + "</strong>"))
    mc.add_to(m)
    m.save("data/restaurants_map.html")  # save map
    print("Restaurants without coordinates: "
          + str(restaurants_without_coordinates))


if __name__ == "__main__":
    main()
