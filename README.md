# Data Wrangling with MongoDB

This repository is a semester project for a class IM_DMDB, all scripts are coded in Python 3. Download .tsv files from https://hpi.de/naumann/projects/repeatability/datasets/restaurants-dataset.html,
clean the dataset, upload it to Atlas MongoDB, find out geographical coordinates using geopy and visualize them on a map with Folio. 
![alt text](https://raw.githubusercontent.com/hrdlickajan/dmdb_restaurants/master/img/map.png)

### Install
File with requirements is included in this repository
```
pip install -r requirements.txt
```

### Architecture
Right now, for demonstrational purpose, database on Atlas does not exist. The script clean_data.py creates this database
![alt text](https://raw.githubusercontent.com/hrdlickajan/dmdb_restaurants/master/img/architecture.png)

### How to run
1. download .tsv files from page, clean it and upload to MongoDB
```
python clean_data.py
```
or 
```
python3 clean_data.py
```
2. find the location


## Built With

* [Dropwizard](http://www.dropwizard.io/1.0.2/docs/) - The web framework used
* [Maven](https://maven.apache.org/) - Dependency Management
* [ROME](https://rometools.github.io/rome/) - Used to generate RSS Feeds
