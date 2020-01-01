from pymongo import MongoClient
import folium

client = MongoClient("mongodb://analytics:analytics-password@test-shard-00-00-"
                     "03ow6.mongodb.net:27017,test-shard-00-01-03ow6.mongodb"
                     ".net:27017,test-shard-00-02-03ow6.mongodb.net:27017/te"
                     "st?ssl=true&replicaSet=test-shard-0&authSource=admin&r"
                     "etryWrites=true&w=majority")

db = client.get_database("dmdb_project")
restaurants = db.restaurants

m = folium.Map(location=[38.023213, -71.0589], zoom_start=12)
for restaurant in restaurants.find():
    if "latitude" not in restaurant:
        continue
    print(restaurant)
    folium.Marker([restaurant["latitude"], restaurant["longitude"]],
                  popup=restaurant["name"],
                  tooltip=restaurant["type"]).add_to(m)


m.save("data/restaurants_map.html")
