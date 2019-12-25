# Data Wrangling with MongoDB

This repository is a semester project for a class IM_DMDB, all scripts are coded in Python 3. Goal of this project is to visualize restaurants on a map from a dirty .tsv file.

<p align="center"> 
<img src="https://raw.githubusercontent.com/hrdlickajan/dmdb_restaurants/master/img/map.png">
</p>

### Install
File with requirements is included in this repository

```
pip install -r requirements.txt
```

### Architecture
![alt text](https://raw.githubusercontent.com/hrdlickajan/dmdb_restaurants/master/img/architecture.png)

### How to run
Right now, for demonstrational purposes, the database on Atlas does not exist.
1. clean_data.py
- downloads .tsv files from https://hpi.de/naumann/projects/repeatability/datasets/restaurants-dataset.html
- clean the restaurant dataset and save it locally
- find duplicate pairs and save them into a .tsv file
- upload clean dataset to Atlas MongoDB

```
python clean_data.py
```
or 
```
python3 clean_data.py
```
2. find the location
- get geopy's response to city
- find lattitude and longitude for each restaurant
The OpenStreetMap server sometimes returned Error 429: Too many requests. So to prevent this error I added a sleep timer between every request set to one second. The timer could be deleted/lowered to speed up the process with a possibility, that the server would return an error.

```
python get_locations.py
```
or 
```
python3 get_locations.py
```
## Built With

* [Dropwizard](http://www.dropwizard.io/1.0.2/docs/) - The web framework used
* [Maven](https://maven.apache.org/) - Dependency Management
* [ROME](https://rometools.github.io/rome/) - Used to generate RSS Feeds
