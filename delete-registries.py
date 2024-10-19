import json
import requests

def load_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def save_json(data, file_path):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

def delete_datasets(token, datasets):
    url_template = 'https://i2kOSDU.energy.azure.com/api/storage/v2/records/{}:delete'
    headers = {
        'Content-Type': 'application/json',
        'data-partition-id': 'i2kosdu',
        'Authorization': f'Bearer {token}'
    }
    results = []
    success_count = 0
    failure_count = 0

    for item in datasets:
        dataset_id = item['response_body']['datasetRegistries'][0]['id']
        url = url_template.format(dataset_id)

        try:
            response = requests.post(url, headers=headers)
            response_data = {
                'response_code': response.status_code,
                'response_body': response.text if response.content else None,
                'original_data': item
            }
            results.append(response_data)

            if response.status_code == 204:
                success_count += 1
                print(f"Dataset deleted successfully: {dataset_id}")
            else:
                failure_count += 1
                print(f"Failed to delete dataset: {dataset_id}, Response: {response_data['response_body']}")

        except Exception as e:
            print(f"An error occurred: {e}")
            failure_count += 1

    return results, success_count, failure_count

def main():
    token_file_path = './data/pdf/token.json'
    datasets_file_path = './data/pdf/register-datasets-result.json'
    output_file_path = './data/pdf/delete-datasets-result.json'

    # Load the token and datasets
    token_data = load_json(token_file_path)
    token = token_data['token']
    datasets = load_json(datasets_file_path)

    # Delete datasets
    results, success_count, failure_count = delete_datasets(token, datasets)

    # Add summary to results
    summary = {
        'total_datasets_processed': len(datasets),
        'total_successes': success_count,
        'total_failures': failure_count
    }
    results.append({'summary': summary})

    # Save the results
    save_json(results, output_file_path)
    print(f"Delete datasets results saved to {output_file_path}")

    # Print the report
    print(f"Total datasets processed: {summary['total_datasets_processed']}")
    print(f"Total successes: {summary['total_successes']}")
    print(f"Total failures: {summary['total_failures']}")

if __name__ == "__main__":
    main()