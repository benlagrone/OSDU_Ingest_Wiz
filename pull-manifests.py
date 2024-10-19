import json
import os
import requests
from concurrent.futures import ThreadPoolExecutor

# Load the manifest URLs from the JSON file
with open('./data/manifests.json', 'r') as f:
    manifests = json.load(f)

# Create a directory to store the downloaded files
os.makedirs("data/osdu_manifests", exist_ok=True)

def download_file(manifest):
    url = manifest['url']
    filename = manifest['name']
    file_path = os.path.join("data/osdu_manifests", filename)
    
    response = requests.get(url)
    if response.status_code == 200:
        with open(file_path, 'wb') as file:
            file.write(response.content)
        print(f"Downloaded: {filename}")
    else:
        print(f"Failed to download: {filename}")

# Use ThreadPoolExecutor for parallel downloads
with ThreadPoolExecutor(max_workers=5) as executor:
    executor.map(download_file, manifests)

print("All manifest files have been downloaded.")