import chromadb
import re

def initialize_chroma_client():
    return chromadb.Client()

def sanitize_collection_name(name):
    sanitized_name = re.sub(r'[^a-zA-Z0-9_-]', '_', name)
    if len(sanitized_name) < 3:
        sanitized_name = sanitized_name + ("_" * (3 - len(sanitized_name)))
    elif len(sanitized_name) > 63:
        sanitized_name = sanitized_name[:63]
    if not sanitized_name[0].isalnum():
        sanitized_name = 'A' + sanitized_name[1:]
    if not sanitized_name[-1].isalnum():
        sanitized_name = sanitized_name[:-1] + 'Z'
    return sanitized_name
