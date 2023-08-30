"""
    LLM
"""

from enum import Enum
import os

from langchain.embeddings import OpenAIEmbeddings
from langchain.embeddings import SentenceTransformerEmbeddings

class EmbeddingType(Enum):
    """Types of embeddings"""
    OPENAI = "Open AI Embeddings"
    SBERT = "SBERT (https://www.sbert.net/)"

class LmmError(Exception):
    """Lmm related exception"""

class LlmManager():
    """LLM Manager"""

    _MODEL_NAME = "gpt-3.5-turbo" # gpt-3.5-turbo-16k

    def __get_api_key(self):
        return os.environ["OPENAI_API_KEY"]

    def get_model_name(self):
        """Return model name"""
        return self._MODEL_NAME

    def get_embeddings(self, embedding_name : str):
        """Embeddings"""
        if embedding_name == EmbeddingType.OPENAI.value:
            # https://api.python.langchain.com/en/latest/embeddings/langchain.embeddings.openai.OpenAIEmbeddings.html
            return OpenAIEmbeddings(openai_api_key= self.__get_api_key())
        
        if embedding_name == EmbeddingType.SBERT.value:
            # https://www.sbert.net/
            return SentenceTransformerEmbeddings(
                model_name= 'sentence-transformers/all-MiniLM-L6-v2',
                model_kwargs={"device": "cpu"}
            )
        
        raise LmmError(f'Unsupported embedding {embedding_name}')

    def get_embedding_list(self) -> list[str]:
        """Get available embeddings"""
        return [e.value for e in EmbeddingType]