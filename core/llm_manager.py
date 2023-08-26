"""
    LLM
"""

from enum import Enum
import os

from langchain.embeddings import OpenAIEmbeddings
from langchain.embeddings import SentenceTransformerEmbeddings

class EmbeddingType(Enum):
    """Types of embeddings"""
    OPENAI = "OpenAIEmbeddings"
    SBERT = "SBERT"

class LmmError(Exception):
    """Lmm related exception"""

class LlmManager():
    """LLM Manager"""

    _MODEL_NAME = "gpt-3.5-turbo" # gpt-3.5-turbo-16k
    _EMBEDDING = EmbeddingType.SBERT

    def __get_api_key(self):
        return os.environ["OPENAI_API_KEY"]

    def get_model_name(self):
        """Return model name"""
        return self._MODEL_NAME

    def get_embeddings(self):
        """Embeddings"""
        if self._EMBEDDING == EmbeddingType.OPENAI:
            # https://api.python.langchain.com/en/latest/embeddings/langchain.embeddings.openai.OpenAIEmbeddings.html
            return OpenAIEmbeddings(openai_api_key= self.__get_api_key())
        if self._EMBEDDING == EmbeddingType.SBERT:
            sbert_embeddings = SentenceTransformerEmbeddings(
                model_name= 'sentence-transformers/all-MiniLM-L6-v2',
                model_kwargs={"device": "cpu"}
            )
            return sbert_embeddings
        raise LmmError(f'Unsupported embedding {self._EMBEDDING}')

    def get_embedding_list(self) -> list[str]:
        """Get available embeddings"""
        return [e.value for e in EmbeddingType]