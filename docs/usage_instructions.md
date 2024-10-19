# OSDU Ingest Wiz: Usage Instructions

This guide provides instructions on how to use the enhanced and new scripts in the OSDU Ingest Wiz project for processing the Volve dataset and preparing it for ingestion into Azure Data Manager for Energy (ADME).

## Prerequisites

- Python 3.7 or higher
- Azure Storage account with access to the Volve dataset
- OSDU manifests stored in a local directory

## Setup

1. Clone the OSDU Ingest Wiz repository to your local machine.
2. Install the required Python packages:
   ```
   pip install -r requirements.txt
   ```
3. Set up your Azure credentials in a `.env` file in the project root:
   ```
   AZURE_STORAGE_ACCOUNT_URL=your_account_url
   AZURE_STORAGE_SAS_TOKEN=your_sas_token
   ```

## 1. Query Blob Storage (query_blob_storage.py)

This script retrieves blob information from Azure Blob Storage for the Volve dataset.

Usage:
```
python projects/OSDU_Ingest_Wiz/query_blob_storage.py
```

Output:
- Generates `blob_inventory_volve.json` in the `data` directory.

Key Features:
- Asynchronous processing for improved performance
- Pagination for handling large datasets
- Progress bar for visual feedback
- Enhanced error handling and logging

## 2. Process Blob Inventory (json_to_csv.py)

This script processes the blob inventory data and generates an enhanced CSV file with categorized data.

Usage:
```
python projects/OSDU_Ingest_Wiz/json_to_csv.py
```

Input:
- Reads `blob_inventory_volve.json` from the `data` directory.

Output:
- Generates `blob_inventory_enhanced.csv` in the `data` directory.
- Creates `kinds_summary.json` with detailed statistics in the `data` directory.
- Produces visualizations:
  - `file_type_distribution.png`
  - `avg_file_size_by_category.png`

Key Features:
- Detailed file type and size statistics
- Parallel processing for improved performance
- Sophisticated metadata extraction
- Data visualizations for analysis

## 3. Assess Manifest Coverage (manifest_coverage_assessment.py)

This new script assesses the coverage of existing OSDU manifests for the categorized Volve dataset.

Usage:
```
python projects/OSDU_Ingest_Wiz/manifest_coverage_assessment.py
```

Input:
- Reads `blob_inventory_enhanced.csv` from the `data` directory.
- Loads OSDU manifests from the `data/osdu_manifests` directory.

Output:
- Generates `manifest_coverage_report.txt` in the `data` directory.
- Creates `manifest_coverage_visualization.png` in the `data` directory.

Key Features:
- Compares categorized data against existing OSDU manifests
- Generates a detailed report on manifest coverage
- Identifies gaps in manifest coverage
- Provides visualizations of coverage statistics

## Workflow

1. Run `query_blob_storage.py` to retrieve the latest blob inventory from Azure.
2. Execute `json_to_csv.py` to process and categorize the blob inventory data.
3. Run `manifest_coverage_assessment.py` to assess the coverage of existing OSDU manifests.
4. Review the generated reports and visualizations in the `data` directory.
5. Use the insights from the manifest coverage assessment to guide the next steps in preparing for ADME ingestion.

## Next Steps

- Develop missing manifests identified by the coverage assessment.
- Enhance metadata extraction based on the categorized data.
- Prepare for ADME ingestion using the insights gained from these analyses.

For any issues or questions, please refer to the project documentation or contact the project maintainers.