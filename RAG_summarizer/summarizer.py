import os
import json
from src.openai_client import OpenAIClient
import tiktoken

openai_client = OpenAIClient()

def num_tokens_from_string(string: str, encoding_name: str) -> int:
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens

def generate_summary(documents):
    openai_client = OpenAIClient()
    
    # Filter out documents with token count less than 30
    filtered_documents = []
    for sublist in documents:
        filtered_sublist = [doc for doc in sublist if num_tokens_from_string(doc, "cl100k_base") >= 30]
        filtered_documents.append(filtered_sublist)
    
    # Calculate the minimum length among the filtered sublists
    min_length = min(len(sublist) for sublist in filtered_documents if sublist)  # Ensure non-empty sublists
    
    # Clip each sublist to the minimum length
    clipped_documents = [sublist[:min_length] for sublist in filtered_documents if sublist]
    
    # Flatten the filtered and clipped documents list
    flattened_documents = [doc for sublist in clipped_documents for doc in sublist]
    
    prompt = f"Please be sure to touch on Termination, Confidentiality, and Indemnification provisions in your answer: Documents: {flattened_documents}"
    
    response = openai_client.generate_completion(
        messages=[
            {"role": "system", "content": "Below you will be provided with a set of documents. Please summarize the similarities or differences among the Termination, Confidentiality, and Indemnification provisions."},
            {"role": "user", "content": prompt}
            ],
        max_tokens=350,
        temperature=0.5
    )
    
    summary = response.choices[0].message.content.strip()
    return summary

def write_summary_to_markdown(summary, output_file_path):
    """
    Write the summary to a markdown file.
    Args:
        summary (str): The generated summary.
        output_file_path (str): The path to the output markdown file.
    """
    with open(output_file_path, 'w') as file:
        file.write(f"# Summary of Documents\n\n{summary}")

def summarize_all_query_results(query_results_directory, summaries_directory):
    """
    Process all JSON files in the query results directory and generate summaries.
    Args:
        query_results_directory (str): Path to the directory containing query results JSON files.
        summaries_directory (str): Path to the directory to save the summaries.
    """
    os.makedirs(summaries_directory, exist_ok=True)

    for filename in os.listdir(query_results_directory):
        if filename.endswith('.json'):
            query_results_file = os.path.join(query_results_directory, filename)
            
            # Read the query results from the JSON file
            with open(query_results_file, 'r') as file:
                query_results = json.load(file)
            
            # Extract the documents from the query results
            documents = query_results.get("documents", [])
            
            if documents:
                # Generate a summary using the OpenAI client
                summary = generate_summary(documents)
                
                # Define the output markdown file path
                output_file_name = filename.replace('_query_results.json', '_summary.md')
                output_file_path = os.path.join(summaries_directory, output_file_name)
                
                # Write the summary to the markdown file
                write_summary_to_markdown(summary, output_file_path)
                print(f"Summary for '{filename}' written to '{output_file_path}'.")

if __name__ == "__main__":
    import os
    import argparse

    # Get the current working directory
    current_directory = os.getcwd()
    default_query_results_directory = os.path.join(current_directory, "outputs", "query_results")
    default_summaries_directory = os.path.join(current_directory, "outputs", "summaries")

    # Set up argument parser
    parser = argparse.ArgumentParser(description="Summarize all query results and store the summaries.")
    parser.add_argument("-q", "--query_results_directory", type=str, default=default_query_results_directory, help=f"Directory containing query results (default: {default_query_results_directory}).")
    parser.add_argument("-s", "--summaries_directory", type=str, default=default_summaries_directory, help=f"Directory to store summaries (default: {default_summaries_directory}).")

    # Parse arguments
    args = parser.parse_args()

    # Summarize all query results
    summarize_all_query_results(args.query_results_directory, args.summaries_directory)

