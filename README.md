# README.md Format

1. Solution Architecture
2. Codebase Architecture
3. Assumptions
4. Anomalies
5. Next Steps and Future Improvements
6. Potential Future Issues and Considerations
7. RAG Summarizer App
8. How to run

# Solution Architecture

1. Preprocessing (preprocessing.py):
   - Input: Raw PDF documents
   - Process: Extract hyperlinks and their associated pages from each PDF. Additionally it filter out the vast majority of the PDF pages from the is table of contents selection process
   - Output: pdf_hyperlink_summary.json containing hyperlink infrastructure for each PDF
2. Table of Contents Classification (toc_classifier.py):
   - Input: pdf_hyperlink_summary.json
   - Process: Classify each page as a potential table of contents using a predefined prompt and an OpenAI model
   - Output: pdf_hyperlink_summary_classified.json with an is_toc field indicating table of contents classification
3. Table of Contents Mapping (toc_mapper.py):
   - Input: pdf_hyperlink_summary_classified.json
   - Process: Map each header in the table of contents to its corresponding page and section in the PDF, using the PDF’s internal hyperlink infrastructure
   - Output: hyperlink_mapping_all_pdfs.json containing links associated with each header on each table of contents page
4. Chunk Extraction (chunk_extractor.py):
   - Input: hyperlink_mapping_all_pdfs.json
   - Process: Extract semantic chunks with corresponding page numbers using the table of contents mapping
   - Output: <pdf_extracted_sections>.json containing extracted sections and metadata for each PDF
5. CSV Generation (csv_builder.py):
   - Input: <pdf_extracted_sections>.json files
   - Process: Convert the extracted sections and metadata into a structured CSV format
   - Output: <pdf_output>.csv files containing the complete set of results as specified in the project instructions
6. Anomaly Handling (anomalies.py):
   - Input: PDFs without proper hyperlink infrastructure
   - Process: Handle anomalous files separately, extracting and processing them based on their unique structure
   - Output: classified_pages.json and table_of_contents.json for the anomalous files
7. RAG-based summarize (RAG_summarize/)
   - This directory holds a solution for generating the optional classification and summarization functionality to Termination, Indemnification, or Confidentiality.
   - More Detail is provided in the RAG Summarizer App section below

In summary this modular approach goes as follows: the preprocessing step establishes the hyperlink infrastructure, followed by table of contents classification and mapping. The chunk extraction step utilizes the mapped table of contents to extract semantic chunks, which are then converted into a structured CSV format. Anomalous files are handled separately to ensure comprehensive processing of all documents.

# Code Base Architecture

- Harvey
  - `anomalies.py`: Handles files without hyperlink infrastructure
  - `chunk_extractor.py`: Takes in hyperlink_mapping_all_pdfs.json and returns `<pdf_extracted_sections>.json`
  - `csv_builder.py`: Takes in `<pdf_extracted_sections>.json` files and returns `<pdf_output>.csv` files
  - `preprocessing.py`: Takes in PDFs and returns pdf_hyperlink_summary.json
  - `toc_classifier.py`: Takes in pdf_hyperlink_summary.json and returns pdf_hyperlink_summary_classified.json
  - `toc_mapper.py`: Takes in pdf_hyperlink_summary_classified.json and returns hyperlink_mapping_all_pdfs.json
  - `run_csvs.sh` : runs script sequence to output csv chunks
  - `run_summarizer.sh` : runs script sequence for RAG Summarizer
  - `.gitignore`
  - `requirements.txt`
  - `data_models/`
    - `toc_classification_model.py`: Houses the table of contents pydantic data model classified
  - `output/`
    - `anomalies/`
      - `classified_pages.json` and `table_of_contents.json`: Two of the attached files were determined to be anomalies (more details provided below); because of this, the PDFs were processed separately
    - `csv_files/`
      - `<pdf_output>.csv`: This houses the complete set of results as specified in the project instructions
    - `extraction/` This has been deleted to send over through gmail.
      - `<pdf_extracted_sections>.json`: Prior to generating the CSV files, the information for each PDF was formatted and handled as a JSON. This JSON holds additional metadata.
      - `hyperlink_mapping_all_pdfs.json`: This JSON holds the output of toc_mapper.py. Its outputs hold links associated with each header on each table of contents page for each PDF.
      - `pdf_hyperlink_summary_classified.json`: This JSON holds the output of toc_classifier.py. Its most notable distinction from pdf_hyperlink_summary.json is the inclusion of an is_toc field that verifies if one of the candidate pages for table of contents classification is of the table of contents class.
      - `pdf_hyperlink_summary.json`: This JSON holds the output of preprocessing.py. It establishes the hyperlink infrastructure associated with each table of contents page candidate and filters out all obvious non-ToC candidates.
  - `pdfs/`: This just holds all the PDFs it has been deleted to send over through gmail.
  - `prompts/`
    - `toc_classification_prompt.yaml`: This YAML holds the prompt used in toc_classifier.py.
  - `utils/`
    - `get_yaml_prompt.py`: Holds the functionality to read in YAML prompts
    - `openai_client.py`: Holds the OpenAI client used in toc_classifier.py and anomalies.py
    - `token_counter.py`: This file was used on this side so I could do some calculations to determine a price estimate for API calls (should be less than 50 dollars)

# Assumptions

1. Removal of non-header links:
   - Justification: The decision to remove non-header links is based on the assumption that the table of contents (ToC) follows a standard format where links directly point to section headers. This assumption is made to ensure consistency in processing the majority of the documents.
   - Potential issue: If the ToC format changes, such as in the case of page 85 in the Watermark document where no headers have links and links point from corresponding non-header elements like "A/n-25", this assumption may lead to the loss of relevant information. These cases appear extremely rare.
2. Handling of links pointing to the same page without a specific location:
   - Justification: When multiple elements in the ToC point to the same page without specifying a particular location on that page, the page in its entirety is returned for each header. This assumption is made to handle cases where the granularity of the links is at the page level rather than the section level.
   - Example: In the UserTesting document, ToC page 114 —> 166 have links pointing to the same page without specifying a specific location, resulting in the start and end points being the same, and so I’m just returning the entire page for each header on this page.
3. Anomalous structure in SPX FLOW document:
   - Justification: The SPX FLOW document has an anomalous structure where the links in the second ToC are only numbers, deviating from the standard format observed in other documents. To maintain consistency in processing the majority of the documents, a decision was made not to include a specific conditional clause to handle this anomaly.
   - Consideration: While adding a conditional clause to handle the SPX FLOW document's structure is possible, it may introduce complexities and potential issues when processing other documents. Additionally, the SPX FLOW document's structure does not technically qualify as a ToC since the links point to defined terms in an annex rather than section headers.

# Anomalies

During the processing of the PDF documents, two anomalies were identified:

1. PDF_67: PREFERRED APARTMENT COMMUNITIES INC_20220414_DEFM14A_20015574_4442255.pdf
   - Issue: No hyperlink infra.
   - Resolution: To handle this anomaly, a separate processing pipeline was created specifically for this document. While this approach may not be the most elegant solution, it demonstrates the importance of pragmatic engineering decisions to ensure the successful processing of all documents, even those with unique structures.
2. PDF_20: CITRIX SYSTEMS INC_20220316_DEFM14A_19951567_4414270.pdf
   - Observation: Despite the presence of a single hyperlink, it was determined that this document does not contain a valid table of contents structure.

By identifying and addressing these anomalies, the solution ensures that all documents are processed successfully, even if some require special handling.

# Next Steps and Future Improvements

1. Enhance table extraction process:
   - Investigate and implement more advanced techniques for extracting tables from PDF documents to improve the accuracy and completeness of the extracted information.
2. Introduce similarity-based linking and filtering:
   - Utilize Levenshtein similarity score or other similarity metrics to establish links between sections and filter out irrelevant content, enhancing the precision of the extracted chunks.
3. Establish robust testing infrastructure:
   - Develop a comprehensive testing framework to ensure the reliability and correctness of the solution, covering various scenarios and edge cases.
4. Improve environment robustness:
   - Create a Dockerfile to encapsulate the solution and its dependencies, ensuring a consistent and reproducible environment across different systems. Additionally, move away from hard typing files paths in scripts.
5. Develop a mini frontend:
   - Design and implement a simple frontend interface to facilitate user interaction with the solution, allowing users to upload documents, view results, and perform basic analytics.

# Potential Future Issues and Considerations

1. Hyperlinks pointing to incorrect locations:
   - In some documents, such as AEROJET ROCKETDYNE HOLDINGS, INC.\_20210205_DEFM14A_19007640_4113036.pdf, hyperlinks in the table of contents may point to incorrect locations, like Annex B linking to Annex C and vice versa.
2. Handling unclassified content:
   - Some documents may contain a significant amount of unclassified content, such as definitions and miscellaneous information, towards the end of the document.
   - Develop strategies to identify and filter out this unclassified content to improve the focus and relevance of the extracted chunks.

# RAG Summarizer App

The RAG (Retrieval-Augmented Generation) Summarizer App is an extension to the main solution that focuses on summarizing the similarities and differences among each document's Termination, Confidentiality, or Indemnification provisions.

## Solution Architecture

1. Section Builder (section_builder.py):

   - Input: CSV files generated by the main solution
   - Process: Converts each input CSV file into a corresponding JSON file
   - Output: JSON files stored in the classified_outputs directory

2. Upsert and Query (upsert_and_query.py):

   - Input: Classified outputs from section_builder.py
   - Process:
     - Upserts all the chunks from the JSON files into a newly created vector database
     - Queries the vector database to retrieve the top 10 most information-rich chunks related to Termination, Indemnification, or Confidentiality
   - Output: Query results stored in the query_results directory

3. Summarizer (summarizer.py):
   - Input: Query results from upsert_and_query.py
   - Process:
     - Filters the retrieved chunks
     - Makes one LLM (Language Model) API call per PDF to generate a summary
   - Output: Summaries stored in the summaries directory

## Codebase Architecture

- `section_builder.py`: Responsible for converting CSV files to JSON files
- `src/`: Contains utility modules and helper functions
  - `chroma_utils.py`: Utilities for interacting with the Chroma vector database
  - `config.py`: Configuration settings for the app
  - `embedding_utils.py`: Utilities for generating embeddings
  - `file_processor.py`: Functions for processing files
  - `openai_client.py`: Client for interacting with the OpenAI API
  - `query_executor.py`: Executes queries against the vector database
- `summarizer.py`: Generates summaries using the retrieved chunks and LLM
- `upsert_and_query.py`: Upserts chunks into the vector database and performs queries against each vector container

- `outputs/`: One directory up
  - `classified_outputs/`: json files
  - `query_results/` : json files
  - `summaries`: markdown files

# How to Run:

Create a venv and install requirements into it

1. Create a pdfs directory `pdfs/` and load the pdfs into it

   - This can be used to load a single file into

2. `chmod +x run_csvs.sh`
3. `./run_csvs.sh`
   - anomalies.py will error if there is one of the anomalous files was not loaded into the pdfs directory, just ignore it
4. `chmod +x run_summarizer.sh`
5. `./run_summarizer.sh` : This file start from the checkpoint of the csv files, so for every csv file is will do upsert_query and summarize
