# preprocessing.py
import fitz
import os
import json
import argparse
from typing import Dict, List, Optional, Union

class PDFHyperlinkAnalyzer:
    def __init__(self, pdf_directory: str, output_directory: str):
        self.pdf_directory = pdf_directory
        self.output_directory = output_directory

    def _process_pdf(self, file_path: str) -> Dict[int, Dict[str, Union[int, List[int]]]]:
        doc = fitz.open(file_path)
        num_pages = len(doc)
        link_count_dict: Dict[int, Dict[str, Union[int, List[int], str]]] = {}

        for page_num in range(num_pages):
            page = doc[page_num]
            links = page.get_links()
            outgoing_links: List[int] = []
            page_content = page.get_text("text")
    
            link_count_dict[page_num + 1] = {
                "incoming_count": 0,
                "incoming_links": [],
                "outgoing_count": 0,
                "outgoing_links": [],
                "page_content": page_content
            }

            for link in links:
                if isinstance(link, dict):
                    if link.get("page"):
                        target_page = link["page"] + 1
                        if 0 <= target_page < num_pages:
                            outgoing_links.append(target_page)
                            link_count_dict.setdefault(target_page, {
                                "incoming_count": 0,
                                "incoming_links": [],
                                "outgoing_count": 0,
                                "outgoing_links": []
                            })
                            link_count_dict[target_page]["incoming_count"] += 1
                            link_count_dict[target_page]["incoming_links"].append(page_num + 1)
                else:
                    if link.page is not None:
                        target_page = link.page + 1
                        if 0 <= target_page < num_pages:
                            outgoing_links.append(target_page)
                            link_count_dict.setdefault(target_page, {
                                "incoming_count": 0,
                                "incoming_links": [],
                                "outgoing_count": 0,
                                "outgoing_links": []
                            })
                            link_count_dict[target_page]["incoming_count"] += 1
                            link_count_dict[target_page]["incoming_links"].append(page_num + 1)

            link_count_dict.setdefault(page_num + 1, {
                "incoming_count": 0,
                "incoming_links": [],
                "outgoing_count": 0,
                "outgoing_links": [],
                "page_content": page_content
            })
            link_count_dict[page_num + 1]["outgoing_count"] = len(outgoing_links)
            link_count_dict[page_num + 1]["outgoing_links"] = outgoing_links


        return link_count_dict

    def _get_pages_with_multiple_outgoing_links(self, link_count_dict: Dict[int, Dict[str, Union[int, List[int], str]]]) -> Dict[int, Dict[str, Union[int, List[int], str]]]:
        filtered_pages = {page: info for page, info in link_count_dict.items() if info['outgoing_count'] > 1}
        return filtered_pages

    def analyze_pdfs(self, num_files: Optional[int] = None) -> None:
        pdf_files = [os.path.join(self.pdf_directory, f) for f in os.listdir(self.pdf_directory) if f.lower().endswith('.pdf')]
        pdf_files.sort()
        if num_files is not None:
            pdf_files = pdf_files[:num_files]

        pdf_hyperlink_summary: Dict[str, Dict[str, Union[str, int, Dict[int, Dict[str, Union[int, List[int], str]]]]]] = {}

        for index, file_path in enumerate(pdf_files, start=1):
            file_name = os.path.basename(file_path)
            pdf_identifier = f"PDF_{index}"
            print(f"Processing {pdf_identifier} - {file_name}...")
            link_count_dict = self._process_pdf(file_path)
            pages_with_multiple_outgoing_links = self._get_pages_with_multiple_outgoing_links(link_count_dict)

            pdf_hyperlink_summary[pdf_identifier] = {
                "pdf_name": file_name,
                "total_pages": len(link_count_dict),
                "pages_with_multiple_outgoing_links_count": len(pages_with_multiple_outgoing_links),
                "pages_with_multiple_outgoing_links": pages_with_multiple_outgoing_links
            }

        self._write_summary_to_json(pdf_hyperlink_summary)
        self._print_summary(pdf_hyperlink_summary)

    def _write_summary_to_json(self, pdf_hyperlink_summary: Dict[str, Dict[str, Union[str, int, Dict[int, Dict[str, Union[int, List[int], str]]]]]]) -> None:
        output_file = os.path.join(self.output_directory, "pdf_hyperlink_summary.json")
        with open(output_file, "w") as file:
            json.dump(pdf_hyperlink_summary, file, indent=4)
        print(f"\nPDF hyperlink summary has been written to: {output_file}")

    def _print_summary(self, pdf_hyperlink_summary: Dict[str, Dict[str, Union[str, int, Dict[int, Dict[str, Union[int, List[int], str]]]]]]) -> None:    
        for pdf, info in pdf_hyperlink_summary.items():
            print(f"\n{pdf}: {info['pdf_name']}")
            print(f"Total Pages: {info['total_pages']}")
            print(f"Pages with Multiple Outgoing Links: {info['pages_with_multiple_outgoing_links_count']}")
            for page, page_info in info['pages_with_multiple_outgoing_links'].items():
                print(f" Page {page}:")
                print(f"  Incoming links: {page_info['incoming_count']}")
                print(f"   From pages: {', '.join(map(str, page_info['incoming_links']))}")
                print(f"  Outgoing links: {page_info['outgoing_count']}")
                print(f"   To pages: {', '.join(map(str, page_info['outgoing_links']))}")


if __name__ == "__main__":
    current_directory = os.getcwd()
    default_pdf_directory = os.path.join(current_directory, "pdfs")
    default_output_directory = os.path.join(current_directory, "outputs")

    parser = argparse.ArgumentParser(description="Analyze PDF hyperlinks.")
    parser.add_argument("-p", "--pdf_directory", type=str, default=default_pdf_directory, help=f"Directory containing the PDF files (default: {default_pdf_directory}).")
    parser.add_argument("-o", "--output_directory", type=str, default=default_output_directory, help=f"Directory to store the output JSON file (default: {default_output_directory}).")
    parser.add_argument("-n", "--num_files", type=int, default=None, help="Number of PDF files to process (default: all).")

    args = parser.parse_args()

    analyzer = PDFHyperlinkAnalyzer(args.pdf_directory, args.output_directory)
    analyzer.analyze_pdfs(num_files=args.num_files)
