import json
import requests

def load_token(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data['token']

def create_legal_tag(token):
    url = 'https://i2kOSDU.energy.azure.com/api/legal/v1/legaltags'
    headers = {
        'Content-Type': 'application/json',
        'data-partition-id': 'i2kosdu',
        'Authorization': f'Bearer {token}'
    }
    payload = {
        "name": "i2kosdu-Test-Legal-Tag-9029857",
        "description": "Legal Tag added for Well",
        "properties": {
            "contractId": "123456",
            "countryOfOrigin": ["US", "CA"],
            "dataType": "Third Party Data",
            "exportClassification": "EAR99",
            "originator": "Schlumberger",
            "personalData": "No Personal Data",
            "securityClassification": "Private",
            "expirationDate": "2025-12-25"
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    response_data = response.json()

    # Save the response to a JSON file
    with open('./data/pdf/legaltag.json', 'w') as file:
        json.dump(response_data, file, indent=4)

    # Print the response body
    if response.status_code == 201:  # Assuming 201 is the success status code
        print(f"Legal tag created: {response_data['name']} = {response_data['name']} > 1")
    else:
        print(f"Failed to create legal tag: {response_data}")

if __name__ == "__main__":
    token_file_path = './data/pdf/token.json'
    token = load_token(token_file_path)
    create_legal_tag(token)