from openai import OpenAI
from typing import List, Dict, Optional, Union
import os
import logging
from dotenv import load_dotenv
import numpy as np
from tenacity import retry, wait_random_exponential, stop_after_attempt, RetryError

class OpenAIClient:
    def __init__(self, response_format: Optional[Dict] = None):
        load_dotenv()
        self.oai_client = OpenAI(
            api_key=os.getenv("XAI_API_KEY"),
            base_url="https://api.x.ai/v1/chat/completions",
        )
        self.response_format = response_format

    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(3))
    def generate_completion(
        self,
        messages: List[Dict],
        model: str = "grok-beta",
    ):
        completions_params = {
            "messages": messages,
            "model": model,
            "response_format": self.response_format,
        }

        response_message = None

        try:
            response_message = self.oai_client.chat.completions.create(
                **completions_params
            )
        except Exception as e:
            logging.error(f"Error: {e}")
            raise

        if logprobs and response_message:
            logprobs = [
                np.round(np.exp(token.logprob) * 100, 2)
                for token in response_message.choices[0].logprobs.content
            ]
            confidence_score = np.mean(logprobs)

            return response_message, confidence_score

        return response_message

    def get_embeddings(self, content: str):
        return (
            self.oai_client.embeddings.create(
                input=content, model="https://api.x.ai/v1/embeddings"
            )
            .data[0]
            .embedding
        )
