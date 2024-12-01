import tiktoken
from chromadb.utils import embedding_functions
from dotenv import load_dotenv
import os

load_dotenv()
xai_api_key = os.getenv("XAI_API_KEY")

openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=xai_api_key,
    model_name="https://api.x.ai/v1/embeddings"
)

def clip_to_token_limit(text, limit, encoding_name):
    if not isinstance(text, str):
        text = str(text) if text is not None else ""
    encoding = tiktoken.get_encoding(encoding_name)
    tokens = encoding.encode(text)
    if len(tokens) > limit:
        tokens = tokens[:limit]
    return encoding.decode(tokens)