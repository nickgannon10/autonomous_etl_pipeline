import fitz
import json
import os
import csv
from utils.openai_client import OpenAIClient

class AnomalyPDFTableOfContentsExtractor:
    def __init__(self, pdf_path, output_dir):
        self.pdf_path = pdf_path
        self.output_dir = output_dir
        self.doc = None

    def read_pdf(self):
        try:
            self.doc = fitz.open(self.pdf_path)

            if self.doc.page_count >= 7:
                toc_dict = {"page_5": {}, "page_6": {}, "page_7": {}}

                for page_num in range(4, 7):
                    page = self.doc.load_page(page_num)
                    text = page.get_text().replace("TABLE OF CONTENTS", "").replace("Page", "").strip()

                    if page_num == 6:
                        annex_index = text.find("Annex A")
                        if annex_index != -1:
                            text = text[:annex_index].strip()

                    text = text.rstrip("i").strip()
                    lines = text.split("\n")
                    toc = {}
                    current_heading = ""
                    current_page_number = ""
                    skip_first_70 = True if page_num == 6 else False

                    for line in lines:
                        if line[0].isdigit():
                            if skip_first_70 and line.startswith("70"):
                                skip_first_70 = False
                                continue
                            if current_heading and current_page_number:
                                toc[current_heading.strip()] = current_page_number
                            current_page_number = line.split(None, 1)[0].strip()
                            current_heading = line.split(None, 1)[1].strip() if len(line.split(None, 1)) > 1 else ""
                        else:
                            current_heading += " " + line.strip()

                    if current_heading and current_page_number:
                        toc[current_heading.strip()] = current_page_number

                    toc_dict[f"page_{page_num + 1}"] = toc

                final_toc = self.transform_toc(toc_dict)
                self.write_json(final_toc)
                print(f"Table of contents saved to: {self.output_file}")

            else:
                print("The PDF document has less than 7 pages.")

        except Exception as e:
            print(f"An error occurred: {str(e)}")

    def transform_toc(self, toc_dict):
        final_toc = {}
        for page_key, contents in toc_dict.items():
            toc_with_pages = {}
            headings = list(contents.keys())
            for i, heading in enumerate(headings):
                start_page = int(contents[heading]) + 7
                if page_key == "page_5":
                    end_page = int(contents[headings[i + 1]]) + 7 if i + 1 < len(headings) else 31
                elif page_key == "page_6":
                    end_page = int(contents[headings[i + 1]]) + 7 if i + 1 < len(headings) else 75
                elif page_key == "page_7":
                    end_page = int(contents[headings[i + 1]]) + 7 if i + 1 < len(headings) else start_page

                page_content = self.extract_page_content(start_page, end_page)

                toc_with_pages[heading] = {
                    "start_page": contents[heading],
                    "end_page": end_page - 7,
                    "page_content": page_content.strip()
                }
            final_toc[page_key] = toc_with_pages
        return final_toc

    def extract_page_content(self, start_page, end_page):
        page_content = ""
        for pg_num in range(start_page, end_page + 1):
            page = self.doc.load_page(pg_num - 1)
            page_content += page.get_text()
        return page_content

    def write_json(self, data):
        os.makedirs(self.output_dir, exist_ok=True)
        self.output_file = os.path.join(self.output_dir, "table_of_contents.json")
        with open(self.output_file, "w") as json_file:
            json.dump(data, json_file, indent=4)

    def json_to_csv(self, json_file_path, output_csv_path, document_name):
        try:
            with open(json_file_path, "r") as json_file:
                data = json.load(json_file)
            
            with open(output_csv_path, "w", newline='') as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(["Document", "Section Header", "Section Text", "Start Page", "End Page"])

                for page_key, sections in data.items():
                    for header, details in sections.items():
                        writer.writerow([
                            document_name,
                            header,
                            details.get("page_content", "").replace("\n", " "),
                            details.get("start_page", ""),
                            details.get("end_page", "")
                        ])
            
            print(f"CSV file saved to: {output_csv_path}")

        except Exception as e:
            print(f"An error occurred: {str(e)}")


class AnomalyPDFClassifier:
    def __init__(self, pdf_path: str, output_json_dir: str, output_csv_dir: str):
        self.pdf_path = pdf_path
        self.output_json_dir = output_json_dir
        self.output_csv_dir = output_csv_dir
        self.openai_client = OpenAIClient(response_format=None)
        self.results = []

    def extract_text_from_page(self, page):
        return page.get_text()

    def classify_page(self, page_text: str) -> str:
        prompt = f"Below you are given a page of text. Please read the text and return a single phrase to classify the contents of that page, avoiding the use of quotation marks around the phrase. If there is an obvious header, please return that:\n\n{page_text}"
        response = self.openai_client.generate_completion(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=10,
            temperature=0.5
        )
        classification = response.choices[0].message.content.strip()
        if classification.startswith('"') and classification.endswith('"'):
            classification = classification[1:-1]
        return classification

    def process_pdf(self):
        doc = fitz.open(self.pdf_path)
        for page_num in range(len(doc)):
            page_text = self.extract_text_from_page(doc.load_page(page_num))
            classification = self.classify_page(page_text)
            page_result = {
                "page": str(page_num + 1),
                "header": classification,
                "page_content": page_text
            }
            self.results.append(page_result)
        self.save_results_as_json()
        self.convert_json_to_csv()

    def save_results_as_json(self):
        os.makedirs(self.output_json_dir, exist_ok=True)
        final_output = {"results": self.results}
        output_json_file_path = os.path.join(self.output_json_dir, 'classified_pages.json')
        with open(output_json_file_path, 'w') as json_file:
            json.dump(final_output, json_file, indent=4)
        print(f"JSON file created at: {output_json_file_path}")

    def convert_json_to_csv(self):
        os.makedirs(self.output_csv_dir, exist_ok=True)
        csv_data = [
            [
                os.path.basename(self.pdf_path),  # Document
                result['header'],                # Section Header
                result['page_content'],          # Section Text
                result['page'],                  # Start Page
                result['page']                   # End Page
            ]
            for result in self.results
        ]
        csv_header = ['Document', 'Section Header', 'Section Text', 'Start Page', 'End Page']
        output_csv_file_path = os.path.join(self.output_csv_dir, f'{os.path.basename(self.pdf_path)}.csv')
        with open(output_csv_file_path, 'w', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(csv_header)
            writer.writerows(csv_data)
        print(f"CSV file created at: {output_csv_file_path}")

if __name__ == "__main__":
    import os
    import argparse

    # Get the current working directory
    current_directory = os.getcwd()
    default_pdf_file_1 = os.path.join(current_directory, "pdfs", "PREFERRED APARTMENT COMMUNITIES INC_20220414_DEFM14A_20015574_4442255.Pdf")
    default_output_directory = os.path.join(current_directory, "outputs", "anomalies")
    default_csv_output_path_1 = os.path.join(current_directory, "outputs", "csv_files", "PREFERRED APARTMENT COMMUNITIES INC_20220414_DEFM14A_20015574_4442255.Pdf.csv")
    default_pdf_file_2 = os.path.join(current_directory, "pdfs", "CITRIX SYSTEMS INC_20220316_DEFM14A_19951567_4414270.Pdf")
    default_output_csv_dir = os.path.join(current_directory, "outputs", "csv_files")

    # Set up argument parser
    parser = argparse.ArgumentParser(description="Extract and classify anomalies from PDF Table of Contents.")
    parser.add_argument("-p1", "--pdf_path_1", type=str, default=default_pdf_file_1, help=f"Path to the first PDF file (default: {default_pdf_file_1}).")
    parser.add_argument("-o", "--output_directory", type=str, default=default_output_directory, help=f"Directory to store anomaly outputs (default: {default_output_directory}).")
    parser.add_argument("-c1", "--csv_output_path_1", type=str, default=default_csv_output_path_1, help=f"CSV output path for the first PDF file (default: {default_csv_output_path_1}).")
    parser.add_argument("-p2", "--pdf_path_2", type=str, default=default_pdf_file_2, help=f"Path to the second PDF file (default: {default_pdf_file_2}).")
    parser.add_argument("-j", "--output_json_dir", type=str, default=default_output_directory, help=f"Directory to store JSON outputs for classification (default: {default_output_directory}).")
    parser.add_argument("-c2", "--output_csv_dir", type=str, default=default_output_csv_dir, help=f"Directory to store CSV outputs for classification (default: {default_output_csv_dir}).")

    # Parse arguments
    args = parser.parse_args()

    # Initialize and run the PDF chunk extractor for the first PDF
    extractor = AnomalyPDFTableOfContentsExtractor(args.pdf_path_1, args.output_directory)
    extractor.read_pdf()
    extractor.json_to_csv(extractor.output_file, args.csv_output_path_1, os.path.basename(args.pdf_path_1))

    # Initialize and run the PDF classifier for the second PDF
    classifier = AnomalyPDFClassifier(args.pdf_path_2, args.output_json_dir, args.output_csv_dir)
    classifier.process_pdf()

