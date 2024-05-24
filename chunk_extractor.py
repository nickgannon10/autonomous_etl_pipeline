import json
import os
import re
from typing import List, Tuple, Dict, Any
import fitz  # PyMuPDF

class PDFChunkExtractor:
    def __init__(self, json_path: str, pdf_dir: str, output_dir: str) -> None:
        self.json_path: str = json_path
        self.pdf_dir: str = pdf_dir
        self.output_dir: str = os.path.join(output_dir, 'extractions')
        os.makedirs(self.output_dir, exist_ok=True)

    @staticmethod
    def is_filtered_out(key: str) -> bool:
        numeric_pattern = re.compile(r'^\d+$')
        alphanumeric_pattern = re.compile(r'^[A-Z]-\d+$')
        section_pattern = re.compile(r'^\d+(\.\d+)+$')
        section_label_pattern = re.compile(r'^Section\s\d+(\.\d+)*$')
        section_trailing_period_pattern = re.compile(r'^Section\s\d+(\.\d+)*\.$')
        trailing_period_pattern = re.compile(r'^\d+(\.\d+)*\s\.\s*$')
        roman_numeral_pattern = re.compile(r'^[ivxlcdm]+$', re.IGNORECASE)
        alphanumeric_newline_pattern = re.compile(r'^[A-Z]-\n\d+$')
        repeated_number_pattern = re.compile(r'^\d+\n\d+$')
        decimal_trailing_period_pattern = re.compile(r'^\d+(\.\d+)*\.$')
        numbered_parenthesis_pattern = re.compile(r'^\d+\)$')
        single_letter_pattern = re.compile(r'^[pvfgy]$', re.IGNORECASE)
        section_decimal_pattern = re.compile(r'^SECTION\s\d+(\.\d+)*\.$')

        return key == "" or \
               key in ["Table of Contents", "TABLE OF CONTENTS", "TABLE OF CONTENTS\u200b"] or \
               numeric_pattern.match(key) is not None or \
               alphanumeric_pattern.match(key) is not None or \
               section_pattern.match(key) is not None or \
               section_label_pattern.match(key) is not None or \
               section_trailing_period_pattern.match(key) is not None or \
               trailing_period_pattern.match(key) is not None or \
               roman_numeral_pattern.match(key) is not None or \
               alphanumeric_newline_pattern.match(key) is not None or \
               repeated_number_pattern.match(key) is not None or \
               decimal_trailing_period_pattern.match(key) is not None or \
               numbered_parenthesis_pattern.match(key) is not None or \
               single_letter_pattern.match(key) is not None or \
               section_decimal_pattern.match(key) is not None

    def gather_sections(self, pdf_data: Dict[str, Any]) -> List[Tuple[str, str, Dict[str, Any]]]:
        sections: List[Tuple[str, str, Dict[str, Any]]] = []
        for page, elements in pdf_data.items():
            page_number = int(page.split('_')[1])
            if 25 <= page_number <= 40:
                continue
            page_sections = {
                f"{k}_{v['destination_page']}_{v['destination_point'][1]}": v
                for k, v in elements.items() if not self.is_filtered_out(k)
            }
            sections.extend((page, k, v) for k, v in page_sections.items())
        return sections

    @staticmethod
    def sort_sections(sections: List[Tuple[str, str, Dict[str, Any]]]) -> List[Tuple[str, str, Dict[str, Any]]]:
        return sorted(sections, key=lambda item: (item[2]["destination_page"], item[2]["destination_point"][1]))

    def extract_chunks(self) -> None:
        with open(self.json_path, 'r') as file:
            data: Dict[str, Dict[str, Dict[str, Any]]] = json.load(file)

        for pdf_name, pdf_data in data.items():
            pdf_path: str = os.path.join(self.pdf_dir, pdf_name)
            output_path: str = os.path.join(self.output_dir, f"extracted_sections_{pdf_name}.json")

            if not os.path.exists(pdf_path):
                print(f"PDF file {pdf_path} not found, skipping.")
                continue

            sections: List[Tuple[str, str, Dict[str, Any]]] = self.gather_sections(pdf_data)
            sorted_sections: List[Tuple[str, str, Dict[str, Any]]] = self.sort_sections(sections)

            pdf_document: fitz.Document = fitz.open(pdf_path)
            extracted_data: Dict[str, Dict[str, Dict[str, Any]]] = {page: {} for page in pdf_data.keys()}

            for i in range(len(sorted_sections)):
                source_page, current_section, current_details = sorted_sections[i]

                if i < len(sorted_sections) - 1:
                    next_section, next_details = sorted_sections[i + 1][1], sorted_sections[i + 1][2]
                    end_page: int = next_details["destination_page"]
                    end_point: Tuple[float, float] = next_details["destination_point"]
                else:
                    end_page = current_details["destination_page"]
                    end_point = (current_details["destination_point"][0], pdf_document.load_page(end_page - 1).rect.height)

                start_page: int = current_details["destination_page"]
                start_point: Tuple[float, float] = current_details["destination_point"]

                text: str = ""

                if start_point == end_point and start_page == end_page:
                    page = pdf_document.load_page(start_page - 1)
                    text = page.get_text()
                elif start_point == end_point and start_page != end_page:
                    for page_num in range(start_page, end_page + 1):
                        page = pdf_document.load_page(page_num - 1)
                        if page_num == start_page:
                            text += page.get_textbox((0, start_point[1], page.rect.width, page.rect.height))
                        elif page_num == end_page:
                            text += page.get_textbox((0, 0, page.rect.width, page.rect.height))
                        else:
                            text += page.get_text()
                else:
                    for page_num in range(start_page, end_page + 1):
                        page = pdf_document.load_page(page_num - 1)
                        if page_num == start_page:
                            if page_num == end_page:
                                text += page.get_textbox((0, start_point[1], page.rect.width, end_point[1]))
                            else:
                                text += page.get_textbox((0, start_point[1], page.rect.width, page.rect.height))
                        elif page_num == end_page:
                            text += page.get_textbox((0, 0, page.rect.width, end_point[1]))
                        else:
                            text += page.get_text()

                section_title: str = current_section.rsplit('_', 2)[0]
                title_index: int = text.find(section_title)
                if title_index != -1:
                    text = text[title_index:].strip()

                next_section_name: str = next_section.rsplit('_', 2)[0] if i < len(sorted_sections) - 1 else ""
                if start_point == end_point and start_page != end_page and next_section_name:
                    next_title_index: int = text.find(next_section_name)
                    if next_title_index != -1:
                        text = text[:next_title_index].strip()

                if start_point == end_point and start_page == end_page and next_section_name:
                    next_title_index: int = text.find(next_section_name)
                    if next_title_index != -1:
                        text = text[:next_title_index].strip()

                section_identifier: str = current_section.rsplit('_', 2)[0]
                extracted_data[source_page][section_identifier] = {
                    "text": text,
                    "start_page": start_page,
                    "start_point": start_point,
                    "end_page": end_page,
                    "end_point": end_point
                }

            with open(output_path, 'w') as out_file:
                json.dump(extracted_data, out_file, indent=4)

if __name__ == "__main__":
    import os
    import argparse

    current_directory = os.getcwd()
    default_json_path = os.path.join(current_directory, "outputs", "hyperlink_mapping_all_pdfs.json")
    default_pdf_dir = os.path.join(current_directory, "pdfs")
    default_output_dir = os.path.join(current_directory, "outputs")

    parser = argparse.ArgumentParser(description="Extract chunks from PDFs based on hyperlink mapping.")
    parser.add_argument("-j", "--json_path", type=str, default=default_json_path, help=f"Path to the JSON file with hyperlink mappings (default: {default_json_path}).")
    parser.add_argument("-p", "--pdf_dir", type=str, default=default_pdf_dir, help=f"Directory containing the PDF files (default: {default_pdf_dir}).")
    parser.add_argument("-o", "--output_dir", type=str, default=default_output_dir, help=f"Directory to store the extracted chunks (default: {default_output_dir}).")

    args = parser.parse_args()

    extractor = PDFChunkExtractor(args.json_path, args.pdf_dir, args.output_dir)
    extractor.extract_chunks()
    
