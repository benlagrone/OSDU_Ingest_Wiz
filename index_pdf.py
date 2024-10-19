import os
import json

def get_files_in_directory(directory):
    file_list = []
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            file_info = {
                "filename": file,
                "path": file_path
            }
            file_list.append(file_info)
    return file_list

def write_to_json(file_list, output_file):
    with open(output_file, 'w') as json_file:
        json.dump(file_list, json_file, indent=4)
    print(f"Index written to {output_file}")

def filter_pdf_files(file_list):
    return [file_info for file_info in file_list if file_info['filename'].lower().endswith('.pdf')]

def main():
    directory = './data/pdf/'
    all_files_output = './data/pdf/index.json'
    pdf_files_output = './data/pdf/index-pdf.json'

    # Get all files
    file_list = get_files_in_directory(directory)
    write_to_json(file_list, all_files_output)

    # Filter and write only PDF files
    pdf_file_list = filter_pdf_files(file_list)
    write_to_json(pdf_file_list, pdf_files_output)

if __name__ == "__main__":
    main()