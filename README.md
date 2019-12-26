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
Right now, for demonstrational purposes, the database on Atlas does not exist.
Run the scripts in following order:
#### 1. clean_data.py
- downloads .tsv files from https://hpi.de/naumann/projects/repeatability/datasets/restaurants-dataset.html
- cleans the restaurant dataset and save it locally
- finds duplicate pairs and save them into a .tsv file
- uploads clean dataset to Atlas MongoDB

```
python clean_data.py
```
or 
```
python3 clean_data.py
```
#### 2. get_locations.py
- loads restaurants collection from Atlas
- gets geopy's response to city
- finds lattitude and longitude for each restaurant

The OpenStreetMap server sometimes returned Error 429: Too many requests. So to prevent this error I added a sleep timer between every request set to one second. The timer could be deleted/lowered to speed up the process with a possibility that the server would return an error.

```
python get_locations.py
```
or 
```
python3 get_locations.py
```
#### 3. visualize_restaurants.py
- Loads every record from Atlas
- If the record has coordinates, visualize it in a map using Folio
- Clusters map markers that are near eachother

```
python visualize_restaurants.py
```
or 
```
python3 visualize_restaurants.py
```
#### Evaluating duplicates - TODO.py
- This script computes precision, recall, accuracy and F-measure between gold standard file
and .tsv file created in clean_data.py.

```
python TODO.py data/restaurants_DPL.tsv data/restaurants_duplicates.tsv data/restaurants_ndpl.tsv
```
or
```
python3 TODO.py data/restaurants_DPL.tsv data/restaurants_duplicates.tsv data/restaurants_ndpl.tsv
```
### Used libraries
* [Beautiful Soup](https://pypi.org/project/beautifulsoup4/) - Web scraping
* [folium](https://pypi.org/project/folium/) - Visualize records in a map
* [geopy](https://pypi.org/project/geopy/) - Get real world coordinates of an addresss
* [Jellyfish](https://pypi.org/project/jellyfish/) - Duplicate detection, compute similarity distance between strings
* [pandas](https://pypi.org/project/pandas/) - Simplified data structures
* [PyMongo](https://pypi.org/project/pymongo/) - MongoDB in Python
* [tqdm](https://pypi.org/project/tqdm/) - Progress bar in command prompt
