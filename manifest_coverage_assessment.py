import pandas as pd
import json
import os
from collections import defaultdict
import matplotlib.pyplot as plt

def load_enhanced_inventory(file_path):
    return pd.read_csv(file_path)

def load_osdu_manifests(manifests_dir):
    manifests = {}
    for filename in os.listdir(manifests_dir):
        if filename.endswith('.json'):
            with open(os.path.join(manifests_dir, filename), 'r') as f:
                manifest = json.load(f)
                kind = manifest.get('kind')
                if kind:
                    manifests[kind] = manifest
                else:
                    print(f"Warning: Manifest in {filename} does not have a 'kind' field.")
    return manifests

def assess_manifest_coverage(inventory_df, manifests):
    coverage = defaultdict(lambda: {'covered': 0, 'total': 0, 'missing': [], 'file_types': set()})
    
    for _, row in inventory_df.iterrows():
        category = row['Category']
        osdu_schema = row['OSDUSchema']
        file_extension = os.path.splitext(row['FileName'])[1].lower()
        coverage[category]['total'] += 1
        coverage[category]['file_types'].add(file_extension)
        
        if osdu_schema in manifests:
            coverage[category]['covered'] += 1
        else:
            coverage[category]['missing'].append(row['FileName'])
    
    return coverage

def generate_coverage_report(coverage):
    report = []
    for category, data in coverage.items():
        covered = data['covered']
        total = data['total']
        percentage = (covered / total) * 100 if total > 0 else 0
        file_types = ', '.join(sorted(data['file_types']))
        report.append(f"{category}:\n"
                      f"  Total files: {total}\n"
                      f"  Covered by manifests: {covered}\n"
                      f"  Coverage percentage: {percentage:.2f}%\n"
                      f"  File types: {file_types}\n"
                      f"  Missing manifests for: {', '.join(data['missing'][:5])}"
                      f"{' ...' if len(data['missing']) > 5 else ''}\n")
    return '\n'.join(report)

def main():
    inventory_file = './data/blob_inventory_enhanced.csv'
    manifests_dir = './data/osdu_manifests'
    output_file = './data/manifest_coverage_report.txt'
    
    inventory_df = load_enhanced_inventory(inventory_file)
    manifests = load_osdu_manifests(manifests_dir)
    coverage = assess_manifest_coverage(inventory_df, manifests)
    report = generate_coverage_report(coverage)
    
    with open(output_file, 'w') as f:
        f.write(report)
    
    print(f"Manifest coverage report has been written to {output_file}")
    
    # Generate visualization
    categories = list(coverage.keys())
    percentages = [(data['covered'] / data['total']) * 100 if data['total'] > 0 else 0 for data in coverage.values()]
    
    plt.figure(figsize=(12, 6))
    plt.bar(categories, percentages)
    plt.title('Manifest Coverage by Category')
    plt.xlabel('Category')
    plt.ylabel('Coverage Percentage')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig('./data/manifest_coverage_visualization.png')
    print("Manifest coverage visualization has been saved to ./data/manifest_coverage_visualization.png")

if __name__ == '__main__':
    main()
