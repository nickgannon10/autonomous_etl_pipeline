import os
import pandas as pd
import json

def classify_and_extract_sections(csv_path):
    # Keywords for each category
    keywords = {
        'Termination': ['terminate', 'termination', 'end of agreement'],
        'Indemnification': ['indemnify', 'indemnification', 'hold harmless'],
        'Confidentiality': ['confidential', 'non-disclosure', 'confidentiality']
    }

    # Read the CSV file
    df = pd.read_csv(csv_path)

    # Function to check if a section contains any keyword
    def contains_keywords(text, category_keywords):
        if isinstance(text, str):
            return any(word in text.lower() for word in category_keywords)
        return False

    # Filter sections that contain any of the keywords
    classified_sections = []
    for index, row in df.iterrows():
        section_data = {
            'Document': row['Document'],
            'Section Header': row['Section Header'],
            'Section Text': row['Section Text'],
            'Start Page': row['Start Page'],
            'End Page': row['End Page']
        }
        for cat in keywords:
            if contains_keywords(row['Section Header'], keywords[cat]) or contains_keywords(row['Section Text'], keywords[cat]):
                section_data['keyword'] = cat
                classified_sections.append(section_data)
                break  # Stop checking once a keyword is found

    return classified_sections

def process_all_csv_files(base_dir):
    csv_dir = os.path.join(base_dir, 'csv_files')
    output_dir = os.path.join(base_dir, 'classified_outputs')
    os.makedirs(output_dir, exist_ok=True)

    for file_name in os.listdir(csv_dir):
        if file_name.endswith('.csv'):
            csv_path = os.path.join(csv_dir, file_name)
            classified_sections = classify_and_extract_sections(csv_path)

            # Output the classified sections to a JSON file in the new directory
            output_filename = file_name.replace('.csv', '_classified.json')
            output_path = os.path.join(output_dir, output_filename)
            with open(output_path, 'w') as outfile:
                json.dump(classified_sections, outfile, indent=4)

            print(f"Classified sections saved to {output_path}")

if __name__ == "__main__":
    import os
    import argparse

    # Get the current working directory
    current_directory = os.getcwd()
    default_base_dir = os.path.join(current_directory, "outputs")

    # Set up argument parser
    parser = argparse.ArgumentParser(description="Process all CSV files in the specified directory.")
    parser.add_argument("-b", "--base_dir", type=str, default=default_base_dir, help=f"Base directory containing CSV files (default: {default_base_dir}).")

    # Parse arguments
    args = parser.parse_args()

    # Process all CSV files
    process_all_csv_files(args.base_dir)

