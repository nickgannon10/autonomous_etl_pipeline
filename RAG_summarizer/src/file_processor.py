import os
import json
from src.embedding_utils import clip_to_token_limit, openai_ef
from src.chroma_utils import initialize_chroma_client, sanitize_collection_name
from src.config import JSON_DIRECTORY, QUERY_OUTPUT_DIRECTORY

def process_files():
    chroma_client = initialize_chroma_client()
    token_limit = 4000
    encoding_scheme = "cl100k_base"

    for filename in os.listdir(JSON_DIRECTORY):
        if filename.endswith('.json'):
            json_path = os.path.join(JSON_DIRECTORY, filename)

            with open(json_path, 'r') as file:
                classified_sections = json.load(file)

            documents = []
            metadatas = []
            ids = []

            for index, section in enumerate(classified_sections):
                section_text = section.get('Section Text', "")
                if not isinstance(section_text, str):
                    section_text = str(section_text) if section_text is not None else ""

                clipped_text = clip_to_token_limit(section_text, token_limit, encoding_scheme)
                documents.append(clipped_text)
                metadata = {
                    "Document": section['Document'],
                    "Section Header": section['Section Header'],
                    "Start Page": section['Start Page'],
                    "End Page": section['End Page'],
                    "Keyword": section['keyword']
                }
                metadatas.append(metadata)
                
                # Ensure unique IDs by appending the row index
                unique_id = f"{section['Document']}-{section['Section Header']}-{index}"
                ids.append(unique_id)

            try:
                embeddings = openai_ef(documents)
            except Exception as e:
                print(f"Error creating embeddings for file {filename}: {e}")
                continue

            collection_name = sanitize_collection_name(os.path.splitext(filename)[0].replace(".Pdf_classified", ""))
            collection = chroma_client.create_collection(name=collection_name)

            collection.upsert(
                documents=documents,
                metadatas=metadatas,
                ids=ids,
                embeddings=embeddings
            )

            print(f"Documents from {filename} upserted into the '{collection_name}' collection in Chroma DB.")
