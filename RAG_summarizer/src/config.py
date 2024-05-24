import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Get the current working directory
current_directory = os.getcwd()

# Retrieve the OpenAI API key from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Define dynamic paths based on the current working directory
JSON_DIRECTORY = os.getenv("JSON_DIRECTORY", os.path.join(current_directory, "outputs", "classified_outputs"))
QUERY_OUTPUT_DIRECTORY = os.getenv("QUERY_OUTPUT_DIRECTORY", os.path.join(current_directory, "outputs", "query_results"))

print(JSON_DIRECTORY)
