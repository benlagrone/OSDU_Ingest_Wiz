import json
import requests

def load_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def save_json(data, file_path):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

def get_storage_instructions(token, index_data):
    url = 'https://i2kOSDU.energy.azure.com/api/dataset/v1/storageInstructions?kindSubType=dataset--File.Generic'
    headers = {
        'data-partition-id': 'i2kosdu',
        'Authorization': f'Bearer {token}'
    }
    results = []

    for item in index_data:
        response = requests.post(url, headers=headers, data='')
        response_data = response.json()
        # Combine the original item with the response data
        combined_data = {
            "original": item,
            "response": response_data
        }
        results.append(combined_data)

    return results

def main():
    token_file_path = './data/pdf/token.json'
    index_file_path = './data/pdf/index-pdf.json'
    output_file_path = './data/pdf/get-storage-instructions.json'

    # Load the token and index data
    token_data = load_json(token_file_path)
    token = token_data['token']
    index_data = load_json(index_file_path)

    # Get storage instructions
    results = get_storage_instructions(token, index_data)

    # Save the results
    save_json(results, output_file_path)
    print(f"Storage instructions saved to {output_file_path}")

if __name__ == "__main__":
    main()