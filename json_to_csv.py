import json
import csv
import os
import re
from datetime import datetime
from collections import Counter, defaultdict
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from concurrent.futures import ProcessPoolExecutor, as_completed
import lasio
from azure.storage.blob import BlobServiceClient
import io   
from dotenv import load_dotenv
import os
import logging
from tqdm import tqdm
import signal

load_dotenv()  # This loads the variables from .env

   # Then use os.getenv to get the variables
account_url = os.getenv('AZURE_STORAGE_ACCOUNT_URL')
sas_token = os.getenv('AZURE_STORAGE_SAS_TOKEN')
data_dir = 'data'

def signal_handler(signum, frame):
    print("\nInterrupted. Saving progress...")
    raise KeyboardInterrupt

signal.signal(signal.SIGINT, signal_handler)


def make_serializable(obj):
    if isinstance(obj, set):
        return list(obj)
    elif isinstance(obj, (datetime, pd.Timestamp)):
        return obj.isoformat()
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    # Add more conversions as needed
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")


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

def process_blob(blob):
    file_name = os.path.basename(blob['name'])
    file_extension = os.path.splitext(file_name)[1].lower()
    category, osdu_schema = get_file_category_and_schema(file_name, blob['name'])
    metadata = extract_metadata(file_name, blob['name'], category)
    file_size = blob['properties']['contentLength']
    
    return {
        'FileName': file_name,
        'FilePath': blob['name'],
        'FileExtension': file_extension,
        'FileSize': file_size,
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


import os
import lasio
import logging
from azure.storage.blob import BlobServiceClient

def extract_las_data(container_name, blob_name):
    connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
    if not account_url or not sas_token:
        raise ValueError("Azure Storage account URL or SAS token not found. Make sure AZURE_STORAGE_ACCOUNT_URL and AZURE_STORAGE_SAS_TOKEN are set in your .env file.")

    # Create the BlobServiceClient
    blob_service_client = BlobServiceClient(account_url=account_url, credential=sas_token)
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
    
    try:
        # Create a local directory to store downloaded files
        os.makedirs('data/temp', exist_ok=True)
        
        # Define the local file path
        local_file_path = os.path.join('data/temp', os.path.basename(blob_name))
        
        # Download the blob to a local file
        with open(local_file_path, "wb") as local_file:
            download_stream = blob_client.download_blob()
            local_file.write(download_stream.readall())
        
        # Read the LAS file from the local directory
        try:
            las = lasio.read(local_file_path)
        except Exception as e:
            logging.error(f"Error reading LAS file {blob_name}: {str(e)}")
            return None
        
        well_data = {
            'filename': blob_name,
            'well': las.well.get('WELL', {}).value or 'NA',
            'company': las.well.get('COMP', {}).value or 'NA',
            'field': las.well.get('FLD', {}).value or 'NA',
            'country': las.well.get('CTRY', {}).value or 'NA',
            'start_depth': las.well.get('STRT', {}).value,
            'stop_depth': las.well.get('STOP', {}).value,
            'step': las.well.get('STEP', {}).value,
            'null_value': las.well.get('NULL', {}).value,
            'curve_names': [curve.mnemonic for curve in las.curves],
            'curve_units': [curve.unit for curve in las.curves],
            'curve_descriptions': [curve.descr for curve in las.curves],
            'curve_data': []
        }

        for curve in las.curves:
            try:
                data = curve.data.tolist()
            except AttributeError:
                data = [str(value) for value in curve.data]  # Convert to strings if not numeric
            well_data['curve_data'].append(data)
        
        # Create the manifests directory if it doesn't exist
        os.makedirs('./data/manifests', exist_ok=True)
        
        base_name = os.path.splitext(os.path.basename(blob_name))[0]
        json_filename = f"well-log-{well_data['well']}-{well_data['company']}"
        json_filename = re.sub(r'[^\w\-_\.]', '_', json_filename)  # Replace invalid characters with underscore
        json_filename = f"{json_filename}.json"
        json_filepath = os.path.join('./data/manifests', json_filename)
        
        # Write the well data to a JSON file
        with open(json_filepath, 'w') as json_file:
            json.dump(well_data, json_file, indent=2)
        
        logging.info(f"Well data written to {json_filepath}")
        
        # Remove the local file after processing
        os.remove(local_file_path)
        
        return well_data
    except Exception as e:
        logging.error(f"Error processing {blob_name}: {str(e)}")
        return None
          
def main():
    input_file = os.path.join(data_dir, 'blob_inventory_volve.json')
    with open(input_file, 'r') as json_file:
        blobs = json.load(json_file)

    # Azure Blob Storage connection string
    # connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
    # if not account_url or not sas_token:
    #     raise ValueError("Azure Storage account URL or SAS token not found. Make sure AZURE_STORAGE_ACCOUNT_URL and AZURE_STORAGE_SAS_TOKEN are set in your .env file.")

    #     # Create the BlobServiceClient
    # blob_service_client = BlobServiceClient(account_url=account_url, credential=sas_token)


    wells_data = []

    total_files = len([blob for blob in blobs if blob['name'].lower().endswith('.las')])
    
    with tqdm(total=len(blobs), desc="Processing LAS files") as pbar:
        for blob in blobs:
            file_name = blob['name']
            print(file_name)
            if file_name.lower().endswith('.las'):
                try:
                    well_data = extract_las_data(blob['container'], file_name)
                    if well_data:
                        wells_data.append(well_data)
                except Exception as e:
                    logging.error(f"Error processing {file_name}: {str(e)}")
                finally:
                    pbar.update(1)

    # for blob in blobs:
    #     file_name = blob['name']
    #     if file_name.lower().endswith('.las'):
    #         logging.info(f"Processing LAS file: {file_name}")
    #         try:
    #             well_data = extract_las_data(blob['container'], file_name)
    #             wells_data.append(well_data)
    #         except Exception as e:
    #             logging.error(f"Error processing {file_name}: {str(e)}")
    #             continue  # Skip to the next file on error

    # Save the extracted data to a JSON file
    output_file = os.path.join(data_dir, 'wells-from-las.json')
    with open(output_file, 'w') as json_file:
        json.dump(wells_data, json_file, indent=2)

    print(f"Extracted well data has been written to {output_file}")

    with ProcessPoolExecutor() as executor:
        results = list(executor.map(process_blob, blobs))

    df = pd.DataFrame(results)
    
    output_file = os.path.join(data_dir, 'blob_inventory_enhanced.csv')
    df.to_csv(output_file, index=False)

    kinds_summary = generate_summary(df)

    summary_file = os.path.join(data_dir, 'kinds_summary.json')
    with open(summary_file, 'w') as json_file:
        json.dump(kinds_summary, json_file, indent=2, default=make_serializable)


    generate_visualizations(df, kinds_summary)

    print(f"Enhanced blob inventory has been written to {output_file}")
    print(f"Kinds summary has been written to {summary_file}")
    print("Visualizations have been generated.")

def generate_summary(df):
    # Load OSDU file types
    with open(os.path.join('data', 'osdu-types.json'), 'r') as f:
        osdu_types = json.load(f)
    
    # Create a set of OSDU extensions for quick lookup
    osdu_extensions = {filetype['extension'].lower() for filetype in osdu_types['filetypes']}

    # Convert FileSize to numeric, coercing errors to NaN
    df['FileSize'] = pd.to_numeric(df['FileSize'], errors='coerce')

    # Print out any rows where FileSize is NaN to debug
    if df['FileSize'].isnull().any():
        print("Non-numeric FileSize entries found:")
        print(df[df['FileSize'].isnull()])

    unknown_count = df['Category'].value_counts().get('Unknown', 0)
    total_files = len(df)

    # Count total occurrences of each file extension
    extension_counts = df['FileExtension'].value_counts().to_dict()

    kinds_summary = {
        'kinds': {},
        'unknown_count': unknown_count,
        'total_files': total_files,
        'total_size': df['FileSize'].sum()
    }

    for category in df['Category'].unique():
        if category != 'Unknown':
            category_df = df[df['Category'] == category]
            kinds_summary['kinds'][category] = {
                'count': len(category_df),
                'folders': category_df['FilePath'].apply(os.path.dirname).unique().tolist(),
                'filetypes': [],
                'size_stats': {
                    'total': category_df['FileSize'].sum(),
                    'avg': category_df['FileSize'].mean(),
                    'min': category_df['FileSize'].min(),
                    'max': category_df['FileSize'].max()
                }
            }
            
            for ext in category_df['FileExtension'].unique():
                filetype_info = {
                    'extension': ext,
                    'count': extension_counts.get(ext, 0),
                    'in_osdu': ext.lower() in osdu_extensions
                }
                kinds_summary['kinds'][category]['filetypes'].append(filetype_info)

    return kinds_summary
    # Load OSDU file types
    with open(os.path.join('data', 'osdu-types.json'), 'r') as f:
        osdu_types = json.load(f)
    
    # Create a set of OSDU extensions for quick lookup
    osdu_extensions = {ext.lower() for filetype in osdu_types['filetypes'] for ext in filetype.get('extension', [])}

    # Convert FileSize to numeric, coercing errors to NaN
    df['FileSize'] = pd.to_numeric(df['FileSize'], errors='coerce')

    # Print out any rows where FileSize is NaN to debug
    if df['FileSize'].isnull().any():
        print("Non-numeric FileSize entries found:")
        print(df[df['FileSize'].isnull()])

    unknown_count = df['Category'].value_counts().get('Unknown', 0)
    total_files = len(df)

    # Count total occurrences of each file extension
    extension_counts = df['FileExtension'].value_counts().to_dict()

    kinds_summary = {
        'kinds': {},
        'unknown_count': unknown_count,
        'total_files': total_files,
        'total_size': df['FileSize'].sum()
    }

    for category in df['Category'].unique():
        if category != 'Unknown':
            category_df = df[df['Category'] == category]
            kinds_summary['kinds'][category] = {
                'count': len(category_df),
                'folders': category_df['FilePath'].apply(os.path.dirname).unique().tolist(),
                'filetypes': [],
                'size_stats': {
                    'total': category_df['FileSize'].sum(),
                    'avg': category_df['FileSize'].mean(),
                    'min': category_df['FileSize'].min(),
                    'max': category_df['FileSize'].max()
                }
            }
            
            for ext in category_df['FileExtension'].unique():
                filetype_info = {
                    'extension': ext,
                    'count': extension_counts.get(ext, 0),
                    'in_osdu': ext.lower() in osdu_extensions
                }
                kinds_summary['kinds'][category]['filetypes'].append(filetype_info)

    return kinds_summary

def generate_visualizations(df, kinds_summary):
    print("Generating visualizations...")

    # Check if DataFrame is empty
    if df.empty:
        print("DataFrame is empty. No visualizations will be generated.")
        return

    # File type distribution
    plt.figure(figsize=(12, 6))
    df['Category'].value_counts().plot(kind='bar')
    plt.title('File Type Distribution')
    plt.xlabel('Category')
    plt.ylabel('Count')
    plt.tight_layout()
    plt.savefig(os.path.join(data_dir, 'file_type_distribution.png'))
    plt.close()
    print("File type distribution saved.")

    # File size statistics
    plt.figure(figsize=(12, 6))
    size_stats = pd.DataFrame({k: v['size_stats'] for k, v in kinds_summary['kinds'].items()}).T
    size_stats['avg'] = size_stats['avg'] / 1024 / 1024  # Convert to MB
    size_stats['avg'].plot(kind='bar')
    plt.title('Average File Size by Category')
    plt.xlabel('Category')
    plt.ylabel('Average Size (MB)')
    plt.tight_layout()
    plt.savefig(os.path.join(data_dir, 'avg_file_size_by_category.png'))
    plt.close()
    print("Average file size by category saved.")

def calculate_size_stats(sizes):
    if not sizes:
        return {'total': 0, 'avg': 0, 'min': 0, 'max': 0}
    return {
        'total': sum(sizes),
        'avg': sum(sizes) / len(sizes),
        'min': min(sizes),
        'max': max(sizes)
    }

if __name__ == "__main__":
    main()
