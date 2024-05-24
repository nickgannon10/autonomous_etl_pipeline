from src.file_processor import process_files
from src.query_executor import query_collections

def main():
    process_files()
    query_collections()
    
if __name__ == "__main__":
    main()
