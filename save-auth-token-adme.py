import json
import os

def create_token_file():
    # Define the directory and file path
    directory = './data/pdf/'
    file_path = os.path.join(directory, 'token.json')

    # Ensure the directory exists
    os.makedirs(directory, exist_ok=True)

    # Define the token data
    token_data = {
        "token": "XXX"
    }

    # Write the token data to the JSON file
    with open(file_path, 'w') as json_file:
        json.dump(token_data, json_file, indent=4)
    print(f"Token written to {file_path}")

if __name__ == "__main__":
    create_token_file()