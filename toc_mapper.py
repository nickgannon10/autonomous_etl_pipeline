import fitz
import json
import os
from typing import Dict, List, Optional, Any

class PDFHyperlinkMapper:
    def __init__(self, pdf_dir: str, json_path: str, output_path: str) -> None:
        self.pdf_dir: str = pdf_dir
        self.json_path: str = json_path
        self.output_path: str = output_path
        self.data: Dict[str, Any] = self.load_json()
        self.updated_hyperlink_mapping: Dict[str, Dict[str, Dict[str, Dict[str, Any]]]] = {}

    def load_json(self) -> Dict[str, Any]:
        """Load the JSON data from the specified path."""
        try:
            with open(self.json_path, 'r') as file:
                data = json.load(file)
            return data
        except FileNotFoundError:
            print(f"JSON file at {self.json_path} not found.")
            return {}
        except json.JSONDecodeError:
            print(f"Error decoding JSON file at {self.json_path}.")
            return {}

    def process_pdfs(self) -> None:
        """Process each PDF to update the hyperlink mapping."""
        for pdf_key, pdf_info in self.data.items():
            pdf_name: str = pdf_info.get('pdf_name', '')
            pdf_path: str = os.path.join(self.pdf_dir, pdf_name)
            pages_with_links: Dict[str, Any] = pdf_info.get('pages_with_multiple_outgoing_links', {})
            page_list: List[int] = [int(page) for page in pages_with_links.keys()]
            
            try:
                doc = fitz.open(pdf_path)
            except Exception as e:
                print(f"Error opening {pdf_name}: {e}")
                continue

            self.updated_hyperlink_mapping[pdf_name] = {}
            for page_num in page_list:
                page_key: str = f"Page_{page_num}"
                
                # Check if is_toc is true before processing the page
                if pages_with_links.get(str(page_num), {}).get('is_toc', False):
                    page = doc.load_page(page_num - 1)
                    self.updated_hyperlink_mapping[pdf_name][page_key] = {}
                    links: List[Dict[str, Any]] = page.get_links()
                    for link in links:
                        if link['kind'] == 1:
                            rect: fitz.Rect = link['from']
                            text: str = page.get_text("text", clip=rect).strip()
                            destination_point: Optional[List[float]] = [link['to'].x, link['to'].y] if link['to'] else None
                            destination_page: int = (link['page'] + 1) if link['page'] is not None else None
                            hyperlink_info: Dict[str, Any] = {
                                'destination_page': destination_page,
                                'destination_point': destination_point,
                                'text': text
                            }
                            # Ensure no duplicate keys
                            if text not in self.updated_hyperlink_mapping[pdf_name][page_key]:
                                self.updated_hyperlink_mapping[pdf_name][page_key][text] = hyperlink_info
                                
            doc.close()



    def save_mapping(self) -> None:
        """Save the updated hyperlink mapping to the specified output path."""
        try:
            with open(self.output_path, 'w') as file:
                json.dump(self.updated_hyperlink_mapping, file, indent=4)
            print(f"Updated hyperlink mapping saved to {self.output_path}")
        except IOError as e:
            print(f"Error saving file to {self.output_path}: {e}")

    def execute(self) -> None:
        """Execute the full processing and saving workflow."""
        self.process_pdfs()
        self.save_mapping()

if __name__ == "__main__":
    import os
    import argparse

    current_directory = os.getcwd()
    default_pdf_dir = os.path.join(current_directory, "pdfs")
    default_json_path = os.path.join(current_directory, "outputs", "pdf_hyperlink_summary_classified.json")
    default_output_path = os.path.join(current_directory, "outputs", "hyperlink_mapping_all_pdfs.json")

    parser = argparse.ArgumentParser(description="Map PDF hyperlinks and classify them.")
    parser.add_argument("-p", "--pdf_dir", type=str, default=default_pdf_dir, help=f"Directory containing the PDF files (default: {default_pdf_dir}).")
    parser.add_argument("-j", "--json_path", type=str, default=default_json_path, help=f"Path to store the classified JSON file (default: {default_json_path}).")
    parser.add_argument("-o", "--output_path", type=str, default=default_output_path, help=f"Path to store the hyperlink mapping JSON file (default: {default_output_path}).")

    args = parser.parse_args()

    mapper = PDFHyperlinkMapper(args.pdf_dir, args.json_path, args.output_path)
    mapper.execute()

