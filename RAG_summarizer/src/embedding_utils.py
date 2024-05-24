import tiktoken
from chromadb.utils import embedding_functions
from dotenv import load_dotenv
import os

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=openai_api_key,
    model_name="text-embedding-ada-002"
)

def clip_to_token_limit(text, limit, encoding_name):
    if not isinstance(text, str):
        text = str(text) if text is not None else ""
    encoding = tiktoken.get_encoding(encoding_name)
    tokens = encoding.encode(text)
    if len(tokens) > limit:
        tokens = tokens[:limit]
    return encoding.decode(tokens)