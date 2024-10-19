import json
import os
from dotenv import load_dotenv
import openai

# question = "Given the OSDU (Open Subsurface Data Universe) standards and the comprehensive coverage of the Volve dataset, including geophysical interpretation, reservoir modeling, production data, and well logs, I need to create an expanded schema for schema category: {schema_cat} and schema name: {schema_name}. This schema should align with industry standards for data interoperability and analysis, and be suitable for ingestion into Azure Data Manager for Energy. Please format the expanded schema in JSON format with comments and descriptions for each attribute.",
#import json

# Load environment variables
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

# Define the path to the input JSON file and the output directory
input_file_path = './data/flat_schemas.json'
output_dir_path = './data/schemas/'

# Ensure the output directory exists
os.makedirs(output_dir_path, exist_ok=True)

# Function to call OpenAI API using the Python SDK
def ask_openai(schema_name):
    schema_cat = item['category']
    schema_name = item['schema']
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant."
                },
                {
                    "role": "user",
                    "content": f"Given the OSDU (Open Subsurface Data Universe) standards and the comprehensive coverage of the Volve dataset, including geophysical interpretation, reservoir modeling, production data, and well logs, I need to create an expanded schema for schema category: {schema_cat} and schema name: {schema_name}. This schema should align with industry standards for data interoperability and analysis, and be suitable for ingestion into Azure Data Manager for Energy. Please format the expanded schema in JSON format with comments and descriptions for each attribute."
                }
            ]
        )
        # Assuming the first response is the one we want
        return response['choices'][0]['message']['content']
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return None

# Read the JSON data from the file
with open(input_file_path, 'r') as file:
    data = json.load(file)

# Iterate through each object in the JSON data
for item in data:
    schema_name = item['schema']
    # Define the output file path using the schema name
    output_file_path = os.path.join(output_dir_path, f"{schema_name}.json")
    
    # Ask OpenAI API for expanded schema
    expanded_schema = ask_openai(item)
    
    # Check if expanded_schema contains data before writing
    if expanded_schema:
        # Write the expanded schema to a new JSON file named after the schema attribute
        with open(output_file_path, 'w') as outfile:
            outfile.write(expanded_schema)
        print(f"Schema for {schema_name} written successfully.")
    else:
        print(f"Failed to retrieve expanded schema for {schema_name}.")

print("Operation completed.")