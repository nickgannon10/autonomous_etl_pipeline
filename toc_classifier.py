import json
import logging
from typing import Dict, List
import os

from data_models.toc_classification_model import TableOfContentsClassifier
from utils.get_prompt import get_yaml_prompt
from utils.openai_client import OpenAIClient

class TOCClassifier:
    def __init__(self, pdf_hyperlink_summary_path: str, toc_classification_prompt_path: str):
        self.openai_client = OpenAIClient()
        self.pdf_hyperlink_summary_path = pdf_hyperlink_summary_path
        self.toc_classification_prompt_path = toc_classification_prompt_path
        self.system_prompt = self.load_prompt(key="system_prompt")
        self.user_prompt_template = self.load_prompt(key="user_prompt")

    def load_prompt(self, key: str) -> str:
        try:
            return get_yaml_prompt(self.toc_classification_prompt_path, key)
        except FileNotFoundError:
            logging.error(f"Prompt file not found: {self.toc_classification_prompt_path}")
        except KeyError:
            logging.error(f"Key '{key}' not found in prompt file: {self.toc_classification_prompt_path}")
        except Exception as e:
            logging.error(f"An error occurred while loading the prompt: {e}")
        return None

    def load_pdf_hyperlink_summary(self) -> Dict:
        try:
            with open(self.pdf_hyperlink_summary_path, "r") as f:
                pdf_hyperlink_summary = json.load(f)
            return pdf_hyperlink_summary
        except FileNotFoundError:
            logging.error(f"PDF hyperlink summary file not found: {self.pdf_hyperlink_summary_path}")
        except json.JSONDecodeError as e:
            logging.error(f"Error parsing JSON file: {e}")
        except Exception as e:
            logging.error(f"An error occurred: {e}")
        return {}

    def _get_toc_classification_tool(self):
        return [
            {
                "type": "function",
                "function": {
                    "name": "classify_table_of_content",
                    "description": "Classify the page content depending on if it is a part of a table of content",
                    "parameters": TableOfContentsClassifier.model_json_schema()
                },
            }
        ]

    def classify_table_of_contents(self, pdf_identifier: str, page_number: int, page_content: str) -> bool:
        if not self.user_prompt_template:
            logging.error(f"User prompt template is not loaded properly.")
            return False

        user_prompt = self.user_prompt_template.format(page_content=page_content)
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        try:
            response_message = self.openai_client.generate_completion(
                messages=messages,
                tools=self._get_toc_classification_tool(),
                tool_choice={
                    "type": "function",
                    "function": {"name": "classify_table_of_content"},
                },
                temperature=0,
                max_tokens=None,
                model="gpt-4"
            )

            response_args_dict = json.loads(response_message.choices[0].message.tool_calls[0].function.arguments)
            table_of_contents_classifier = TableOfContentsClassifier(**response_args_dict)

            return table_of_contents_classifier.is_table_of_contents

        except Exception as e:
            logging.error(f"Failed to classify table of contents for PDF {pdf_identifier}, page {page_number}: {e}")
            return False

    def classify_pdf_pages(self) -> Dict:
        pdf_hyperlink_summary = self.load_pdf_hyperlink_summary()
        classified_pages: Dict[str, Dict[int, bool]] = {}

        for pdf_identifier, pdf_data in pdf_hyperlink_summary.items():
            classified_pages[pdf_identifier] = {}
            for page_number, page_data in pdf_data["pages_with_multiple_outgoing_links"].items():
                page_content = page_data["page_content"]
                is_table_of_contents = self.classify_table_of_contents(pdf_identifier, int(page_number), page_content)
                page_data["is_toc"] = is_table_of_contents
                classified_pages[pdf_identifier][int(page_number)] = is_table_of_contents

        print("\nClassification Results:")
        for pdf_identifier, classified_page_numbers in classified_pages.items():
            print(f"{pdf_identifier}: {classified_page_numbers}")

        return pdf_hyperlink_summary

    def write_classified_summary_to_json(self, classified_summary: Dict) -> None:
        output_file = os.path.join(os.path.dirname(self.pdf_hyperlink_summary_path), "pdf_hyperlink_summary_classified.json")
        with open(output_file, "w") as file:
            json.dump(classified_summary, file, indent=4)
        print(f"\nClassified PDF hyperlink summary has been written to: {output_file}")


if __name__ == "__main__":
    import os
    import argparse
    import logging

    logging.basicConfig(level=logging.INFO)

    # Get the current working directory
    current_directory = os.getcwd()
    default_pdf_hyperlink_summary_path = os.path.join(current_directory, "outputs", "pdf_hyperlink_summary.json")
    default_toc_classification_prompt_path = os.path.join(current_directory, "prompts", "toc_classification_prompt.yaml")

    # Set up argument parser
    parser = argparse.ArgumentParser(description="Classify PDF pages based on Table of Contents.")
    parser.add_argument("-s", "--summary_path", type=str, default=default_pdf_hyperlink_summary_path, help=f"Path to the PDF hyperlink summary JSON file (default: {default_pdf_hyperlink_summary_path}).")
    parser.add_argument("-t", "--toc_prompt_path", type=str, default=default_toc_classification_prompt_path, help=f"Path to the Table of Contents classification prompt YAML file (default: {default_toc_classification_prompt_path}).")

    # Parse arguments
    args = parser.parse_args()

    # Initialize and run the TOC classifier
    toc_classifier = TOCClassifier(args.summary_path, args.toc_prompt_path)
    classified_summary = toc_classifier.classify_pdf_pages()
    toc_classifier.write_classified_summary_to_json(classified_summary)

