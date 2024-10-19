import asyncio
import json
from logger import main_logger
from query_blob_storage import inventory_blobs
from json_to_csv import process_inventory, generate_summary, visualize_dataset
from manifest_coverage_assessment import generate_coverage_report
from generate_manifests import generate_all_manifests
from adme_ingestion import ingest_to_adme
from generate_report import generate_report

async def run_pipeline(config, dry_run=False):
    try:
        main_logger.info("Starting blob inventory...")
        await inventory_blobs(config['connection_string'], config['container_name'])
        
        main_logger.info("Processing inventory...")
        df = process_inventory('blob_inventory.json')
        generate_summary(df)
        visualize_dataset(df)
        
        main_logger.info("Assessing manifest coverage...")
        coverage_report = generate_coverage_report(df, config['osdu_schemas'])
        
        main_logger.info("Generating manifests...")
        generate_all_manifests('categorized_inventory.csv')
        
        if not dry_run:
            main_logger.info("Starting ADME ingestion...")
            ingestion_results = await ingest_to_adme(config, 'generated_manifests.json')
        else:
            main_logger.info("Dry run mode: Skipping ADME ingestion")
            ingestion_results = ["Dry run: Ingestion simulated for all files"]
        
        main_logger.info("Generating final report...")
        generate_report('categorized_inventory.csv', 'coverage_report.json', ingestion_results)
        
        main_logger.info("Ingestion pipeline completed successfully.")
    except Exception as e:
        main_logger.error(f"Pipeline failed: {str(e)}")
        raise

if __name__ == "__main__":
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    dry_run = config.get('dry_run', False)
    asyncio.run(run_pipeline(config, dry_run))
