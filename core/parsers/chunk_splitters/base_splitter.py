"""
    Base chunk splitter
"""
# pylint: disable=R0903

from abc import abstractmethod
from dataclasses import dataclass

from langchain.docstore.document import Document

@dataclass
class ChunkSplitterParams:
    """Parameters for chunk splitter"""
    chunk_min_tokens     : int
    tokens_per_chunk     : int
    chunk_overlap_tokens : int
    model_name           : str

class BaseChunkSplitter():
    """Split text into chunks"""

    splitter_params : ChunkSplitterParams

    def __init__(self, splitter_params : ChunkSplitterParams):
        self.splitter_params = splitter_params

    @abstractmethod
    def create_documents(self, texts: list[str], metadatas: list[dict] = None) -> list[Document]:
        """Create documents from input"""

    @abstractmethod
    def split_documents(self, documents : list[Document]) -> list[Document]:
        """Split input into chunks"""

