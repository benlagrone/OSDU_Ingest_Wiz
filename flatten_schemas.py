import json

# Specify the path to the schemas.json file
file_path = './data/schemas.json'

# Open the JSON file and load its content
with open(file_path, 'r') as file:
    original_json = json.load(file)

flattened_list = []

# Iterate through the loaded JSON data and flatten it
for category in original_json:
    for schema in category["schemas"]:
        flattened_list.append({"schema": schema, "category": category["category"]})

# Optionally, convert the flattened list back to JSON if needed
flattened_json = json.dumps(flattened_list, indent=4)
print(flattened_json)

# Optionally, convert the flattened list back to JSON and output it to a specific file
output_file_path = './data/flat_schemas.json'
with open(output_file_path, 'w') as file:
    json.dump(flattened_list, file, indent=4)