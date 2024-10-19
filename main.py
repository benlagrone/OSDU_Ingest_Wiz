import argparse
import json
import asyncio
from ingestion_pipeline import run_pipeline

def main():
    parser = argparse.ArgumentParser(description="ADME Ingestion Pipeline")
    parser.add_argument('--dry-run', action='store_true', help='Run in dry run mode (no actual ingestion)')
    parser.add_argument('--config', default='config.json', help='Path to configuration file')
    args = parser.parse_args()

    with open(args.config, 'r') as f:
        config = json.load(f)

    config['dry_run'] = args.dry_run

    asyncio.run(run_pipeline(config, args.dry_run))

if __name__ == "__main__":
    main()
