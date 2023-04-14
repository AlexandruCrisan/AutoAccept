import json


def save_json_to_file(filename: str, data):
  with open(filename, 'w') as outfile:
    json.dump(data, outfile, indent=4, sort_keys=True)

def read_json_from_file(filename: str):
  file = open(filename)
  return json.load(file)