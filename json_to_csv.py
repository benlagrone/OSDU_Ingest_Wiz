import json
import csv
import os
import re
from datetime import datetime
from collections import Counter, defaultdict

data_dir = 'data'

def get_file_category_and_schema(file_name, file_path):
    extension = os.path.splitext(file_name)[1].lower()
    folder_name = os.path.dirname(file_path).lower()
    
    categories = {
        '.las': ('Well Logs', 'Well Log'),
        '.dlis': ('Well Logs', 'Well Log'),
        '.segy': ('Seismic Data', 'Seismic'),
        '.sgy': ('Seismic Data', 'Seismic'),
        '.xml': ('Real-Time Drilling Data', 'Wellbore Trajectory'),
        '.witsml': ('Real-Time Drilling Data', 'Wellbore Trajectory'),
        '.csv': ('Production Data', 'Production Data'),
        '.json': ('Production Data', 'Production Data'),
        '.grdecl': ('Reservoir Models', 'Reservoir'),
        '.rms': ('Reservoir Models', 'Reservoir'),
        '.pdf': ('Documents', 'Work Product'),
        '.docx': ('Documents', 'Work Product'),
        '.xlsx': ('Documents', 'Work Product'),
        '.p1': ('Seismic Data', 'SeismicLineGeometry'),
        '.p11': ('Seismic Data', 'SeismicLineGeometry'),
        '.p6': ('Seismic Data', 'SeismicBinGrid'),
        '.resqml': ('Geophysical Interpretation', 'SeismicHorizon')
    }
    
    category, schema = categories.get(extension, ('Unknown', 'Unknown'))
    
    if category == 'Unknown':
        if 'well_logs' in folder_name:
            return 'Well Logs', 'Well Log'
        elif 'seismic' in folder_name:
            return 'Seismic Data', 'Seismic'
        elif 'production' in folder_name:
            return 'Production Data', 'Production Data'
        elif 'reservoir' in folder_name:
            return 'Reservoir Models', 'Reservoir'
        elif 'witsml' in folder_name or 'drilling' in folder_name:
            return 'Real-Time Drilling Data', 'Wellbore Trajectory'
        elif 'wellbore' in folder_name:
            return 'Wellbore Data', 'Wellbore'
        elif 'marker' in folder_name or 'horizon' in folder_name:
            return 'Markers and Horizons', 'Markers and Horizons'
    
    return category, schema

def extract_metadata(file_name, file_path, category):
    metadata = {}
    
    if category == 'Well Logs':
        well_id_match = re.search(r'([A-Z0-9-]+)', file_name)
        if well_id_match:
            metadata['WellID'] = well_id_match.group(1)
    
    elif category == 'Seismic Data':
        survey_name_match = re.search(r'([A-Z0-9-]+)_survey', file_name, re.IGNORECASE)
        if survey_name_match:
            metadata['SurveyName'] = survey_name_match.group(1)
    
    date_match = re.search(r'(\d{4}-\d{2}-\d{2})', file_name)
    if date_match:
        metadata['Date'] = date_match.group(1)
    
    return metadata

def all_required_metadata_present(category, osdu_schema, metadata):
    required_fields = {
        'Well Logs': ['WellID'],
        'Seismic Data': ['SurveyName'],
        'Production Data': ['Date']
    }
    
    if category in required_fields:
        return all(field in metadata and metadata[field] for field in required_fields[category])
    return True

def main():
    input_file = os.path.join(data_dir, 'blob_inventory_volve.json')
    with open(input_file, 'r') as json_file:
        blobs = json.load(json_file)

    total_files = len(blobs)
    unknown_count = 0
    kinds = Counter()
    kind_folders = defaultdict(set)
    kind_filetypes = defaultdict(set)

    output_file = os.path.join(data_dir, 'blob_inventory_enhanced.csv')
    with open(output_file, 'w', newline='') as csv_file:
        fieldnames = [
            'FileName', 'FilePath', 'FileExtension', 'FileSize', 'LastModified', 
            'FileType', 'BlobType', 'BlobTier', 'CreationTime', 'ETag', 'Container', 
            'Category', 'OSDUSchema', 'WellID', 'SurveyName', 'Date',
            'ReadyForManifest'
        ]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        for blob in blobs:
            file_name = os.path.basename(blob['name'])
            file_extension = os.path.splitext(file_name)[1].lower()
            category, osdu_schema = get_file_category_and_schema(file_name, blob['name'])
            
            if category == 'Unknown':
                unknown_count += 1
            else:
                kinds[category] += 1
                folder = os.path.dirname(blob['name'])
                kind_folders[category].add(folder)
                kind_filetypes[category].add(file_extension)
            
            metadata = extract_metadata(file_name, blob['name'], category)
            
            row = {
                'FileName': file_name,
                'FilePath': blob['name'],
                'FileExtension': file_extension,
                'FileSize': blob['properties']['contentLength'],
                'LastModified': blob['properties']['lastModified'],
                'FileType': blob['properties']['contentSettings']['contentType'],
                'BlobType': blob['properties']['blobType'],
                'BlobTier': blob['properties'].get('blobTier', ''),
                'CreationTime': blob['properties']['creationTime'],
                'ETag': blob['properties']['etag'],
                'Container': blob['container'],
                'Category': category,
                'OSDUSchema': osdu_schema,
                'WellID': metadata.get('WellID', ''),
                'SurveyName': metadata.get('SurveyName', ''),
                'Date': metadata.get('Date', ''),
                'ReadyForManifest': all_required_metadata_present(category, osdu_schema, metadata)
            }
            
            writer.writerow(row)

    kinds_summary = {
        'kinds': {
            kind: {
                'count': count,
                'folders': list(kind_folders[kind]),
                'filetypes': list(kind_filetypes[kind])
            } for kind, count in kinds.items()
        },
        'unknown_count': unknown_count,
        'total_files': total_files
    }

    summary_file = os.path.join(data_dir, 'kinds_summary.json')
    with open(summary_file, 'w') as json_file:
        json.dump(kinds_summary, json_file, indent=2)

    print(f"Enhanced blob inventory has been written to {output_file}")
    print(f"Kinds summary has been written to {summary_file}")

if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()