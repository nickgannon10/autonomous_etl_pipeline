import os
import json
import csv

def create_csv_from_json(json_file_path, output_dir):
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Load JSON data
    with open(json_file_path, 'r') as file:
        data = json.load(file)
    
    # Extract document name from file path
    document_name = os.path.basename(json_file_path).replace('extracted_sections_', '').replace('.json', '')
    
    # Prepare CSV file path
    csv_file_path = os.path.join(output_dir, f'{document_name}.csv')
    
    with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        # Write header
        writer.writerow(['Document', 'Section Header', 'Section Text', 'Start Page', 'End Page'])
        
        # Iterate through pages and sections
        for page_key, sections in data.items():
            for section_header, section_details in sections.items():
                # Write section details to CSV
                writer.writerow([
                    document_name, 
                    section_header, 
                    section_details.get('text', ''),
                    section_details.get('start_page', ''),
                    section_details.get('end_page', '')
                ])
    
    print(f'CSV file created: {csv_file_path}')

def process_all_json_files(json_dir, output_dir):
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # List all JSON files in the specified directory
    json_files = [f for f in os.listdir(json_dir) if f.endswith('.json')]
    
    # Process each JSON file
    for json_file in json_files:
        json_file_path = os.path.join(json_dir, json_file)
        create_csv_from_json(json_file_path, output_dir)

if __name__ == "__main__":
    import os
    import argparse

    # Get the current working directory
    current_directory = os.getcwd()
    default_json_dir = os.path.join(current_directory, "outputs", "extractions")
    default_output_dir = os.path.join(current_directory, "outputs", "csv_files")

    # Set up argument parser
    parser = argparse.ArgumentParser(description="Process all JSON files and convert them to CSV.")
    parser.add_argument("-j", "--json_dir", type=str, default=default_json_dir, help=f"Directory containing JSON files (default: {default_json_dir}).")
    parser.add_argument("-o", "--output_dir", type=str, default=default_output_dir, help=f"Directory to store the CSV files (default: {default_output_dir}).")

    # Parse arguments
    args = parser.parse_args()

    # Process all JSON files
    process_all_json_files(args.json_dir, args.output_dir)

