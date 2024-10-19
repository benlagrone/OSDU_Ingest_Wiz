import json
import requests

def load_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def save_json(data, file_path):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

def register_datasets(token, upload_results, legal_tag):
    url = 'https://i2kOSDU.energy.azure.com/api/dataset/v1/registerDataset'
    headers = {
        'data-partition-id': 'i2kosdu',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    results = []
    success_count = 0
    failure_count = 0

    for item in upload_results:
        file_source = item['original_data']['response']['storageLocation']['fileSource']
        payload = {
            "datasetRegistries": [
                {
                    "kind": "osdu:wks:dataset--File.Generic:1.0.0",
                    "acl": {
                        "viewers": [
                            "data.default.viewers@i2kosdu.dataservices.energy"
                        ],
                        "owners": [
                            "data.default.owners@i2kosdu.dataservices.energy"
                        ]
                    },
                    "legal": {
                        "legaltags": [
                            legal_tag['name']
                        ],
                        "otherRelevantDataCountries": [
                            "US"
                        ],
                        "status": "compliant"
                    },
                    "data": {
                        "DatasetProperties": {
                            "FileSourceInfo": {
                                "FileSource": file_source
                            }
                        },
                        "ResourceSecurityClassification": "osdu:reference-data--ResourceSecurityClassification:RESTRICTED:",
                        "SchemaFormatTypeID": "osdu:reference-data--SchemaFormatType:TabSeparatedColumnarText:"
                    },
                    "meta": [],
                    "tags": {}
                }
            ]
        }

        try:
            response = requests.put(url, headers=headers, json=payload)
            response_body = response.json() if response.status_code == 201 else response.text
            response_data = {
                'response_code': response.status_code,
                'response_body': response_body,
                'original_data': item
            }
            results.append(response_data)

            if response.status_code == 201:
                success_count += 1
                print(f"Dataset registered successfully: {response_body['datasetRegistries'][0]['id']}")
            else:
                failure_count += 1
                print(f"Failed to register dataset: {response_body}")

        except Exception as e:
            print(f"An error occurred: {e}")
            failure_count += 1

    return results, success_count, failure_count

def main():
    token_file_path = './data/pdf/token.json'
    upload_results_file_path = './data/pdf/upload-file-results.json'
    legal_tag_file_path = './data/pdf/legaltag.json'
    output_file_path = './data/pdf/register-datasets-result.json'

    # Load the token, upload results, and legal tag
    token_data = load_json(token_file_path)
    token = token_data['token']
    upload_results = load_json(upload_results_file_path)
    legal_tag = load_json(legal_tag_file_path)

    # Register datasets
    results, success_count, failure_count = register_datasets(token, upload_results, legal_tag)

    # Save the results
    save_json(results, output_file_path)
    print(f"Register datasets results saved to {output_file_path}")

    # Print the report
    total_files = len(upload_results)
    print(f"Total files processed: {total_files}")
    print(f"Total successes: {success_count}")
    print(f"Total failures: {failure_count}")

if __name__ == "__main__":
    main()