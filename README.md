# Data Wrangling with MongoDB

This repository is a semester project for a class IM_DMDB, all scripts are coded in Python 3. The goal of this project is to visualize restaurants on a map from a dirty .tsv file.

<p align="center"> 
<img src="https://raw.githubusercontent.com/hrdlickajan/dmdb_restaurants/master/img/map.png">
</p>

### Install
File with requirements is included in this repository

```
pip install -r requirements.txt
```

### Architecture
<p align="center"> 
<img src="https://raw.githubusercontent.com/hrdlickajan/dmdb_restaurants/master/img/architecture.png">
</p>

### How to run

#### 1. clean_data.py
- downloads .tsv files from https://hpi.de/naumann/projects/repeatability/datasets/restaurants-dataset.html
- cleans the restaurant dataset and saves it locally
- finds duplicate pairs and saves them into a .tsv file
- uploads clean dataset to Atlas MongoDB to a selected database

There is already a database on Atlas named "dmdb_project" with everything prepared. You can create your own database by writing your database name as script argument.
```
python clean_data.py [database_name]
```

#### 2. get_locations.py
- loads restaurants collection from selected Atlas database
- gets geopy's Nominatim response to city
- finds lattitude and longitude for each restaurant

The OpenStreetMap server sometimes returned Error 429: Too many requests. So to prevent this error I added a sleep timer between every request set to one second. The timer could be deleted/lowered to speed up the process with a possibility that the server would return an error - see [Nominatim usage policy](https://operations.osmfoundation.org/policies/nominatim/).

```
python get_locations.py [database_name]
```

#### 3. visualize_restaurants.py
- Load record from selected database, if it has coordinates, visualize it in a map using folium
- Clusters map markers that are near eachother

```
python visualize_restaurants.py [database_name]
```

#### Evaluating duplicates - gold_standard_evaluation.py
- This script computes precision, recall, accuracy and F-measure between gold standard file
and .tsv file created in clean_data.py.

```
python gold_standard_evaluation.py [path to gold standard duplicates] [path to clean dataset] [path to non-duplicates]
```
The files are downloaded or created in script clean_data.py
```
python gold_standard_evaluation.py data/restaurants_DPL.tsv data/restaurants_duplicates.tsv data/restaurants_ndpl.tsv
```

### Used libraries
* [Beautiful Soup](https://pypi.org/project/beautifulsoup4/) - Web scraping
* [folium](https://pypi.org/project/folium/) - Visualize records in a map
* [geopy](https://pypi.org/project/geopy/) - Get real world coordinates of an addresss
* [Jellyfish](https://pypi.org/project/jellyfish/) - Duplicate detection, compute similarity distance between strings
* [pandas](https://pypi.org/project/pandas/) - Simplified data structures
* [PyMongo](https://pypi.org/project/pymongo/) - MongoDB in Python
* [tqdm](https://pypi.org/project/tqdm/) - Progress bar in command prompt
