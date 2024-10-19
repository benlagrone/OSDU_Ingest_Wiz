import json
import os
import pandas as pd

data_dir = 'data'

def load_inventory():
    inventory_file = os.path.join(data_dir, 'blob_inventory_enhanced.csv')
    return pd.read_csv(inventory_file)

def create_manifest_entry(row):
    # Create a manifest entry based on the file's category and metadata
    entry = {
        "kind": "osdu:wks:Manifest:1.0.0",
        "ReferenceData": [],
        "MasterData": [],
        "Data": {
            "WorkProduct": {},
            "WorkProductComponents": [],
            "Datasets": []
        }
    }
    
    # Example: Add file metadata to the appropriate section
    if row['Category'] == 'Well Logs':
        entry['MasterData'].append({
            "WellID": row['WellID'],
            "FileName": row['FileName'],
            "FilePath": row['FilePath']
        })
    elif row['Category'] == 'Seismic Data':
        entry['Data']['Datasets'].append({
            "SurveyName": row['SurveyName'],
            "FileName": row['FileName'],
            "FilePath": row['FilePath']
        })
    # Add more conditions for other categories as needed

    return entry

def generate_manifests():
    df = load_inventory()
    manifests = []

    for _, row in df.iterrows():
        if row['ReadyForManifest']:
            manifest_entry = create_manifest_entry(row)
            manifests.append(manifest_entry)

    # Write the manifests to a JSON file
    manifest_file = os.path.join(data_dir, 'generated_manifests.json')
    with open(manifest_file, 'w') as f:
        json.dump(manifests, f, indent=2)

    print(f"Manifests have been written to {manifest_file}")

if __name__ == "__main__":
    generate_manifests()