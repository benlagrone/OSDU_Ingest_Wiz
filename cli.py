import click
import json
import pandas as pd
import asyncio
from query_blob_storage import inventory_blobs
from json_to_csv import process_inventory, generate_summary, visualize_dataset
from manifest_coverage_assessment import generate_coverage_report
from generate_manifests import generate_all_manifests
from adme_ingestion import ingest_to_adme

@click.group()
def cli():
    """OSDU Ingest Wiz CLI"""
    pass

@cli.command()
@click.option('--connection-string', required=True, help='Azure Storage connection string')
@click.option('--container-name', required=True, help='Azure Storage container name')
def inventory(connection_string, container_name):
    """Take inventory of files in Azure Blob Storage"""
    asyncio.run(inventory_blobs(connection_string, container_name))
    click.echo("Inventory completed. Output saved to blob_inventory.json")

@cli.command()
@click.option('--input-file', default='blob_inventory.json', help='Input JSON file')
@click.option('--output-file', default='categorized_inventory.csv', help='Output CSV file')
def process(input_file, output_file):
    """Process inventory and generate CSV"""
    df = process_inventory(input_file)
    df.to_csv(output_file, index=False)
    generate_summary(df)
    visualize_dataset(df)
    click.echo(f"Processing completed. Output saved to {output_file}")

@cli.command()
@click.option('--input-file', default='categorized_inventory.csv', help='Input CSV file')
@click.option('--schemas-file', required=True, help='OSDU schemas file')
def assess_coverage(input_file, schemas_file):
    """Assess manifest coverage"""
    df = pd.read_csv(input_file)
    with open(schemas_file, 'r') as f:
        schemas = json.load(f)
    generate_coverage_report(df, schemas)
    click.echo("Coverage assessment completed. Report saved to manifest_coverage_report.txt")

@cli.command()
@click.option('--input-file', default='categorized_inventory.csv', help='Input CSV file')
@click.option('--output-file', default='generated_manifests.json', help='Output JSON file')
def generate_manifests(input_file, output_file):
    """Generate OSDU manifests"""
    generate_all_manifests(input_file, output_file)
    click.echo(f"Manifests generated and saved to {output_file}")

@cli.command()
@click.option('--config', default='config.json', help='Configuration file')
@click.option('--manifests-file', default='generated_manifests.json', help='Manifests JSON file')
@click.option('--dry-run', is_flag=True, help='Perform a dry run without actual ingestion')
def ingest(config, manifests_file, dry_run):
    """Ingest data into ADME"""
    with open(config, 'r') as f:
        config_data = json.load(f)
    if dry_run:
        click.echo("Performing dry run...")
    else:
        asyncio.run(ingest_to_adme(config_data, manifests_file))
    click.echo("Ingestion process completed")

if __name__ == '__main__':
    cli()
