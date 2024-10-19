import json
import requests
import os

def load_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def save_json(data, file_path):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

def upload_files(storage_instructions, project_home):
    results = []

    for item in storage_instructions:
        signed_url = item['response']['storageLocation']['signedUrl']
        original_path = item['original']['path']
        full_path = os.path.join(project_home, original_path)

        headers = {
            'x-ms-blob-type': 'BlockBlob'
        }

        with open(full_path, 'rb') as file_data:
            response = requests.put(signed_url, headers=headers, data=file_data)

        response_data = {
            'response_code': response.status_code,
            'original_data': item
        }
        results.append(response_data)

    return results

def main():
    input_file_path = './data/pdf/get-storage-instructions.json'
    output_file_path = './data/pdf/upload-file-results.json'
    project_home = '/Users/benjaminlagrone/Documents/projects/OSDU/claude-engineer/projects/OSDU_Ingest_Wiz'

    # Load storage instructions
    storage_instructions = load_json(input_file_path)

    # Upload files and get results
    results = upload_files(storage_instructions, project_home)

    # Save the results
    save_json(results, output_file_path)
    print(f"Upload results saved to {output_file_path}")

if __name__ == "__main__":
    main()