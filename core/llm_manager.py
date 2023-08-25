"""
    LLM
"""
import os

from langchain.embeddings import OpenAIEmbeddings

class LlmManager():
    """LLM Manager"""

    _MODEL_NAME = "gpt-3.5-turbo" # gpt-3.5-turbo-16k

    def __get_api_key(self):
        return os.environ["OPENAI_API_KEY"]

    def get_model_name(self):
        """Return model name"""
        return self._MODEL_NAME

    def get_embeddings(self):
        """Embeddings based on model name"""
        # https://api.python.langchain.com/en/latest/embeddings/langchain.embeddings.openai.OpenAIEmbeddings.html
        return OpenAIEmbeddings(openai_api_key= self.__get_api_key())
