import os
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient, ContainerClient, BlobPrefix
import json
import csv
from azure.core.exceptions import ResourceNotFoundError
import base64
import datetime

data_dir = 'data'

# Load environment variables from .env file
load_dotenv()

# Get the storage account URL and SAS token from environment variables
account_url = os.getenv('AZURE_STORAGE_ACCOUNT_URL')
sas_token = os.getenv('AZURE_STORAGE_SAS_TOKEN')

# Create the BlobServiceClient object
blob_service_client = BlobServiceClient(account_url=account_url, credential=sas_token)

# Specify the container name
container_name = "corpus"

# Get a reference to the container
container_client = blob_service_client.get_container_client(container_name)

def get_subfolders(prefix):
    return [blob.name for blob in container_client.walk_blobs(name_starts_with=prefix, delimiter='/') if isinstance(blob, BlobPrefix)]

def json_serializable(obj):
    if isinstance(obj, (bytes, bytearray)):
        return base64.b64encode(obj).decode('utf-8')
    elif isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    return str(obj)

def get_blob_info(prefix):
    blob_info_list = []
    blobs = container_client.list_blobs(name_starts_with=prefix)
    for blob in blobs:
        if not blob.name.endswith('/'):  # Exclude folder names
            blob_info = {
                "container": container_name,
                "content": "",
                "deleted": json_serializable(blob.deleted),
                "encryptedMetadata": json_serializable(blob.encrypted_metadata),
                "encryptionKeySha256": json_serializable(blob.encryption_key_sha256),
                "encryptionScope": json_serializable(blob.encryption_scope),
                "hasLegalHold": json_serializable(blob.has_legal_hold),
                "hasVersionsOnly": json_serializable(blob.has_versions_only),
                "immutabilityPolicy": {
                    "expiryTime": json_serializable(blob.immutability_policy.expiry_time) if blob.immutability_policy else None,
                    "policyMode": json_serializable(blob.immutability_policy.policy_mode) if blob.immutability_policy else None
                },
                "isCurrentVersion": json_serializable(blob.is_current_version),
                "lastAccessedOn": json_serializable(blob.last_accessed_on),
                "leaseDuration": json_serializable(blob.lease.duration) if blob.lease else None,
                "leaseState": json_serializable(blob.lease.state) if blob.lease else None,
                "leaseStatus": json_serializable(blob.lease.status) if blob.lease else None,
                "metadata": json_serializable(blob.metadata),
                "name": json_serializable(blob.name),
                "properties": {
                    "appendBlobCommittedBlockCount": json_serializable(blob.append_blob_committed_block_count),
                    "blobTier": json_serializable(blob.blob_tier),
                    "blobTierChangeTime": json_serializable(blob.blob_tier_change_time),
                    "blobTierInferred": json_serializable(blob.blob_tier_inferred),
                    "blobType": json_serializable(blob.blob_type),
                    "contentLength": json_serializable(blob.size),
                    "contentRange": json_serializable(blob.content_range),
                    "contentSettings": {
                        "cacheControl": json_serializable(blob.content_settings.cache_control),
                        "contentDisposition": json_serializable(blob.content_settings.content_disposition),
                        "contentEncoding": json_serializable(blob.content_settings.content_encoding),
                        "contentLanguage": json_serializable(blob.content_settings.content_language),
                        "contentMd5": json_serializable(blob.content_settings.content_md5),
                        "contentType": json_serializable(blob.content_settings.content_type)
                    },
                    "copyCompletionTime": json_serializable(blob.copy.completion_time) if blob.copy else None,
                    "copyId": json_serializable(blob.copy.id) if blob.copy else None,
                    "copyProgress": json_serializable(blob.copy.progress) if blob.copy else None,
                    "copySource": json_serializable(blob.copy.source) if blob.copy else None,
                    "copyStatus": json_serializable(blob.copy.status) if blob.copy else None,
                    "copyStatusDescription": json_serializable(blob.copy.status_description) if blob.copy else None,
                    "creationTime": json_serializable(blob.creation_time),
                    "deletedTime": json_serializable(blob.deleted_time),
                    "etag": json_serializable(blob.etag),
                    # "expiresOn": json_serializable(blob.expires_on),
                    "lastModified": json_serializable(blob.last_modified),
                    "leaseDuration": json_serializable(blob.lease.duration) if blob.lease else None,
                    "leaseState": json_serializable(blob.lease.state) if blob.lease else None,
                    "leaseStatus": json_serializable(blob.lease.status) if blob.lease else None,
                    "pageBlobSequenceNumber": json_serializable(blob.page_blob_sequence_number),
                    # "pageRanges": json_serializable(blob.page_ranges),
                    # "rehydrationStatus": json_serializable(blob.rehydration_status),
                    "remainingRetentionDays": json_serializable(blob.remaining_retention_days),
                    "serverEncrypted": json_serializable(blob.server_encrypted)
                },
                "rehydratePriority": json_serializable(blob.rehydrate_priority),
                "requestServerEncrypted": json_serializable(blob.request_server_encrypted),
                "snapshot": json_serializable(blob.snapshot),
                "tagCount": json_serializable(blob.tag_count),
                "tags": json_serializable(blob.tags),
                "versionId": json_serializable(blob.version_id)
            }
            blob_info_list.append(blob_info)
    return blob_info_list
    blob_info_list = []
    blobs = container_client.list_blobs(name_starts_with=prefix)
    for blob in blobs:
        if not blob.name.endswith('/'):  # Exclude folder names
            blob_info = {
                "container": container_name,
                "content": "",
                "deleted": json_serializable(blob.deleted),
                "encryptedMetadata": json_serializable(blob.encrypted_metadata),
                "encryptionKeySha256": json_serializable(blob.encryption_key_sha256),
                "encryptionScope": json_serializable(blob.encryption_scope),
                "hasLegalHold": json_serializable(blob.has_legal_hold),
                "hasVersionsOnly": json_serializable(blob.has_versions_only),
                "immutabilityPolicy": {
                    "expiryTime": json_serializable(blob.immutability_policy.expiry_time) if blob.immutability_policy else None,
                    "policyMode": json_serializable(blob.immutability_policy.policy_mode) if blob.immutability_policy else None
                },
                "isCurrentVersion": json_serializable(blob.is_current_version),
                "lastAccessedOn": json_serializable(blob.last_accessed_on),
                "leaseDuration": json_serializable(blob.lease.duration) if blob.lease else None,
                "leaseState": json_serializable(blob.lease.state) if blob.lease else None,
                "leaseStatus": json_serializable(blob.lease.status) if blob.lease else None,
                "metadata": json_serializable(blob.metadata),
                "name": json_serializable(blob.name),
                "properties": {
                    "appendBlobCommittedBlockCount": json_serializable(blob.properties.append_blob_committed_block_count),
                    "blobTier": json_serializable(blob.properties.blob_tier),
                    "blobTierChangeTime": json_serializable(blob.properties.blob_tier_change_time),
                    "blobTierInferred": json_serializable(blob.properties.blob_tier_inferred),
                    "blobType": json_serializable(blob.properties.blob_type),
                    "contentLength": json_serializable(blob.properties.content_length),
                    "contentRange": json_serializable(blob.properties.content_range),
                    "contentSettings": {
                        "cacheControl": json_serializable(blob.properties.content_settings.cache_control),
                        "contentDisposition": json_serializable(blob.properties.content_settings.content_disposition),
                        "contentEncoding": json_serializable(blob.properties.content_settings.content_encoding),
                        "contentLanguage": json_serializable(blob.properties.content_settings.content_language),
                        "contentMd5": json_serializable(blob.properties.content_settings.content_md5),
                        "contentType": json_serializable(blob.properties.content_settings.content_type)
                    },
                    "copyCompletionTime": json_serializable(blob.properties.copy.completion_time),
                    "copyId": json_serializable(blob.properties.copy.id),
                    "copyProgress": json_serializable(blob.properties.copy.progress),
                    "copySource": json_serializable(blob.properties.copy.source),
                    "copyStatus": json_serializable(blob.properties.copy.status),
                    "copyStatusDescription": json_serializable(blob.properties.copy.status_description),
                    "creationTime": json_serializable(blob.properties.creation_time),
                    "deletedTime": json_serializable(blob.properties.deleted_time),
                    "etag": json_serializable(blob.properties.etag),
                    # "expiresOn": json_serializable(blob.properties.expires_on),
                    "lastModified": json_serializable(blob.properties.last_modified),
                    "leaseDuration": json_serializable(blob.properties.lease.duration),
                    "leaseState": json_serializable(blob.properties.lease.state),
                    "leaseStatus": json_serializable(blob.properties.lease.status),
                    "pageBlobSequenceNumber": json_serializable(blob.properties.page_blob_sequence_number),
                    # "pageRanges": json_serializable(blob.properties.page_ranges),
                    # "rehydrationStatus": json_serializable(blob.properties.rehydration_status),
                    "remainingRetentionDays": json_serializable(blob.properties.remaining_retention_days),
                    "serverEncrypted": json_serializable(blob.properties.server_encrypted)
                },
                "rehydratePriority": json_serializable(blob.rehydrate_priority),
                "requestServerEncrypted": json_serializable(blob.request_server_encrypted),
                "snapshot": json_serializable(blob.snapshot),
                "tagCount": json_serializable(blob.tag_count),
                "tags": json_serializable(blob.tags),
                "versionId": json_serializable(blob.version_id)
            }
            blob_info_list.append(blob_info)
    return blob_info_list

# Start with the Volve folder
root_prefix = "files/Volve/"
all_blob_info = []

try:
    # Get subfolders
    subfolders = get_subfolders(root_prefix)
    print(f"Subfolders found: {subfolders}")

    # Process root folder
    print(f"Processing root folder: {root_prefix}")
    all_blob_info.extend(get_blob_info(root_prefix))

    # Process each subfolder
    for subfolder in subfolders:
        print(f"Processing subfolder: {subfolder}")
        all_blob_info.extend(get_blob_info(subfolder))


    # Write the blob information to a JSON file in the 'data' directory
    output_file = os.path.join(data_dir, 'blob_inventory_volve.json')
    with open(output_file, 'w') as json_file:
        json.dump(all_blob_info, json_file, indent=2, default=json_serializable)

    print("Blob inventory has been written to blob_inventory_volve.json")

except ResourceNotFoundError:
    print(f"Error: The container '{container_name}' or the prefix '{root_prefix}' was not found.")
except Exception as e:
    print(f"An error occurred: {str(e)}")