import os
import json

def saveJSON(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def readJSON(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def fileExists(filename):
    return os.path.exists(filename)