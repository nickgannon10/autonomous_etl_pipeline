import os
import fitz
import tiktoken

def get_text_from_pdf(file_path):
    """
    Extract text content from a PDF file.

    Args:
    file_path (str): Path to the PDF file.

    Returns:
    str: Text content extracted from the PDF.
    """
    doc = fitz.open(file_path)
    text_string = ""
    
    for page in doc:
        text_string += page.get_text()

    doc.close()
    return text_string

def num_tokens_from_string(string: str, encoding_name: str) -> int:
    """
    Calculate the number of tokens in a string.

    Args:
    string (str): Input string.
    encoding_name (str): Name of the encoding scheme.

    Returns:
    int: Number of tokens.
    """
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens

def compute_token_counts_in_directory(directory_path: str, encoding_name: str) -> (int, dict):
    """
    Compute token counts for all PDFs in a directory.

    Args:
    directory_path (str): Path to the directory containing PDF files.
    encoding_name (str): Name of the encoding scheme.

    Returns:
    tuple: Total token count and dictionary containing token counts for each PDF.
    """
    total_token_count = 0
    pdf_token_counts = {}

    for filename in os.listdir(directory_path):
        if filename.endswith(".Pdf"):
            file_path = os.path.join(directory_path, filename)
            text = get_text_from_pdf(file_path)
            num_tokens = num_tokens_from_string(text, encoding_name)
            total_token_count += num_tokens
            pdf_token_counts[filename] = num_tokens

    return total_token_count, pdf_token_counts

# Directory containing PDF files
pdf_directory = '/Users/nicholasgannon/sources/repos/Harvey/pdfs'

# Encoding scheme name
encoding_scheme = "cl100k_base"

# Compute token counts
total_tokens, pdf_tokens = compute_token_counts_in_directory(pdf_directory, encoding_scheme)

# Print token counts for each PDF
for pdf, tokens in pdf_tokens.items():
    print(f"PDF: {pdf}, Token Count: {tokens}")

# Print total token count
print(f"Total Token Count for All PDFs: {total_tokens}")
