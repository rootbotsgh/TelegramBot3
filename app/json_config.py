"""
Index.json file is an index of documents stored in storage channel
Contains functions load_index() and 
save_index() to interact with the index.json file
"""
import json
from config import INDEX_FILE

def load_index():
    """
    loads the json data of all files stored on the storage channel
    """
    try:
        with open(INDEX_FILE, "r", encoding='UTF-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print('index.json file not found')
        return []

def save_index(data):
    """
    saves file data to index.json
    """
    try:
        with open(INDEX_FILE, "w", encoding='UTF-8') as f:
            json.dump(data, f, indent=2)
    except FileNotFoundError:
        #for now, i'll just notify the console
        print('index.json file not found')
