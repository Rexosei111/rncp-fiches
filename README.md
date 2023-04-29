# ETL Pipeline

This scripts are for populating and updating the database with data coming from an xml file.

## Basic Requirements

- Python (version 3.8+)
- MySQL Database

## Project Setup

- Create and activate your virtual environment
- In the root folder, run `pip install -r requirements.txt` to install the required libraries.
- Create a ".env" file in the root fold.
- The sample content of the ".env" file can be found in the ".env.sample" file also in the root folder.

## Folder structure

- [.env.sample](./final/.env.sample) # Contains sample environement variables you need to set.
- [.gitignore](./final/.gitignore)
- [README.md](./final/README.md)
- [config.py](./final/config.py) # Contains the entire project configurations. It is mainly responsible for reading and parsing environment variables and generating a settings instance base on the environment variables.
- [create_db_tables.py](./final/create_db_tables.py) # This is a script for recreating tables in the database. Only run this script when you want to delete and recreate the database tables.
- [data_model.py](./final/data_model.py) # Contains classes that represent the tables in the database
- [get_files.py](./final/get_files.py) # contains functions for downloading the latest version of the data from the website and extracting it.
- [main.py](./final/main.py) # This is the script which runs daily and update the database with latest version of the xml data.
- [populate_db.py](./final/populate_db.py) # After recreating your database tables, this is the script you run to populate it with the latest xml file.
- [requirements.txt](./final/requirements.txt)
- [save_data.py](./final/save_data.py) # Contains functions for saving a fresh data into the database. The functions in this file are used when inserting a new fiche into the database.
- [update_data.py](./final/update_data.py) # Contains functions for updating already existing fiche.
