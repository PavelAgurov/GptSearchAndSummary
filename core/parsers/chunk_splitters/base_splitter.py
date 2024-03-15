"""
    Base chunk splitter
"""
# pylint: disable=R0903,C0305

from enum import Enum
from abc import abstractmethod
from dataclasses import dataclass

from langchain.docstore.document import Document

class ChunkSplitterMode(Enum):
    """Chunk splitter modes"""
    TOKEN_MODE = "TokenChunkSplitter"
    FACT_LIST  = "Fact list"
    FAQ_LIST   = "FAQ list"

@dataclass
class ChunkSplitterParams:
    """Parameters for chunk splitter"""
    chunk_min_tokens     : int
    tokens_per_chunk     : int
    chunk_overlap_tokens : int
    model_name           : str
    chunk_splitter_mode  : ChunkSplitterMode

class BaseChunkSplitter():
    """Split text into chunks"""

    splitter_params : ChunkSplitterParams

    def __init__(self, splitter_params : ChunkSplitterParams):
        self.splitter_params = splitter_params

    @abstractmethod
    def split_into_documents(self, input_with_meta : list[tuple[str, dict]]) -> list[Document]:
        """Split input into chunks"""

