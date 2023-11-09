"""
    LLM
"""

# pylint: disable=C0301,C0103,C0304,C0303,W0611,W0511,R0913,R0402

import os
from enum import Enum
from dataclasses import dataclass
from typing import Callable

from langchain.embeddings import OpenAIEmbeddings
from langchain.embeddings import SentenceTransformerEmbeddings

class EmbeddingType(Enum):
    """Types of embeddings"""
    SBERT    = "SBERT (https://www.sbert.net/)"
    MULTILP  = "paraphrase-multilingual-MiniLM-L12-v2" 
    OPENAI35 = "Open AI Embeddings"

@dataclass
class EmbeddingItem:
    """Emdedding information"""
    embedding_type    : EmbeddingType
    url               : str
    description       : str
    default_threshold : float

    def __repr__(self):
        return f'{self.embedding_type.value}'

class LlmEmbeddingError(Exception):
    """Lmm embedding exception"""

class EmbeddingManager():
    """Embedding Manager"""

    _OPENAI_MODEL_NAME = "gpt-3.5-turbo" # gpt-3.5-turbo-16k

    def __get_api_key(self):
        return os.environ["OPENAI_API_KEY"]

    def get_embedding_information_list(self) -> list[EmbeddingItem]:
        """List of available embeddings"""
        return [
                EmbeddingItem(
                    EmbeddingType.SBERT,
                    "https://www.sbert.net/",
                    "Sentence Transformers (https://www.sbert.net/), Free",
                    0.76
                ),
                EmbeddingItem(
                    EmbeddingType.MULTILP,
                    "https://huggingface.co/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
                    "Sentence Transformers - paraphrase multilingual, Free",
                    0.35
                ),
                EmbeddingItem(
                    EmbeddingType.OPENAI35,
                    "https://api.python.langchain.com/en/latest/embeddings/langchain.embeddings.openai.OpenAIEmbeddings.html",
                    "OpenAI gpt-3.5-turbo embedding, not free",
                    0.76
                )
        ]

    def get_embeddings(self, embedding_name : EmbeddingType)-> (OpenAIEmbeddings | SentenceTransformerEmbeddings):
        """Embeddings"""
        
        if embedding_name == EmbeddingType.OPENAI35.name:
            # https://api.python.langchain.com/en/latest/embeddings/langchain.embeddings.openai.OpenAIEmbeddings.html
            return OpenAIEmbeddings(openai_api_key= self.__get_api_key())
        
        if embedding_name == EmbeddingType.SBERT.name:
            # https://www.sbert.net/
            return SentenceTransformerEmbeddings(
                model_name= 'sentence-transformers/all-MiniLM-L6-v2',
                model_kwargs={"device": "cpu"}
            )
        
        if embedding_name == EmbeddingType.MULTILP.name:
            # https://huggingface.co/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
            return SentenceTransformerEmbeddings(
                model_name= 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
            )
        
        raise LlmEmbeddingError(f'Unsupported embedding {embedding_name}')

    def get_embeddings_encode_call(self, embedding_name : EmbeddingType) -> Callable[..., list[list[float]]]:
        """Get encode method for embedding"""
        embedding = self.get_embeddings(embedding_name)

        embed_documents_call = getattr(embedding, "embed_documents", None)
        if callable(embed_documents_call):
            return embed_documents_call
        
        encode_call = getattr(embedding, "encode", None)
        if callable(encode_call):
            return encode_call
        
        raise LlmEmbeddingError(embedding_name)
