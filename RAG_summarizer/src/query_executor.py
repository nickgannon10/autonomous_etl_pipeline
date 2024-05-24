import os
import json
from src.embedding_utils import openai_ef
from src.chroma_utils import initialize_chroma_client, sanitize_collection_name
from src.config import JSON_DIRECTORY, QUERY_OUTPUT_DIRECTORY

def query_collections():
    chroma_client = initialize_chroma_client()

    query_data = [
        {"terms": ["Termination, terminate, termination, end of agreement"], "keyword": "Termination"},
        {"terms": ["Indemnification, indemnify, indemnification, hold harmless"], "keyword": "Indemnification"},
        {"terms": ["Confidentiality, confidential, non-disclosure, confidentiality"], "keyword": "Confidentiality"}
    ]

    def query_collection(collection_name, terms, keyword):
        try:
            query_embeddings = openai_ef(terms)
            collection = chroma_client.get_collection(name=collection_name)
            results = collection.query(
                query_embeddings=query_embeddings,
                n_results=10,
                where={"Keyword": {"$in": [keyword]}}
            )
            return results
        except ValueError as e:
            print(f"Collection {collection_name} does not exist or could not be queried. Error: {e}")
            return None

    os.makedirs(QUERY_OUTPUT_DIRECTORY, exist_ok=True)

    for filename in os.listdir(JSON_DIRECTORY):
        if filename.endswith('.json'):
            collection_name = os.path.splitext(filename)[0].replace(".Pdf_classified", "")
            sanitized_collection_name = sanitize_collection_name(collection_name)

            all_results = {"ids": [], "distances": [], "metadatas": [], "documents": []}

            for query in query_data:
                results = query_collection(sanitized_collection_name, query["terms"], query["keyword"])
                if results:
                    all_results["ids"].extend(results.get("ids", []))
                    all_results["distances"].extend(results.get("distances", []))
                    all_results["metadatas"].extend(results.get("metadatas", []))
                    all_results["documents"].extend(results.get("documents", []))

            output_file_path = os.path.join(QUERY_OUTPUT_DIRECTORY, f"{sanitized_collection_name}_query_results.json")
            with open(output_file_path, 'w') as output_file:
                json.dump(all_results, output_file, indent=4)
            print(f"Results for collection '{sanitized_collection_name}' written to '{output_file_path}'.")

