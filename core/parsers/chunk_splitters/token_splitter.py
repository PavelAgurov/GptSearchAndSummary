"""
    Chunk splitter based on tokens
"""

# pylint: disable=R0903,C0305,C0301

import tiktoken
from tiktoken.core import Encoding

from langchain.docstore.document import Document
from langchain.text_splitter import TextSplitter

from core.parsers.chunk_splitters.base_splitter import BaseChunkSplitter, ChunkSplitterParams

class SpecialTokenTextSplitter(TextSplitter):
    """Splitting text to tokens using model tokenizer with special parameters."""

    encoding : Encoding
    splitter_params : ChunkSplitterParams

    def __init__(self, splitter_params : ChunkSplitterParams):
        super().__init__(
            splitter_params.tokens_per_chunk,
            splitter_params.chunk_overlap_tokens,
            add_start_index = True
        )
        self.splitter_params = splitter_params
        self.encoding = tiktoken.encoding_for_model(splitter_params.model_name)

    def split_text_on_tokens(self, text: str) -> list[str]:
        """Split incoming text and return chunks using tokenizer (copided from langchain)."""
        splits: list[str] = []
        input_ids = self.encoding.encode(text)
        start_index = 0
        cur_index = min(start_index + self.splitter_params.tokens_per_chunk, len(input_ids))
        chunk_ids = input_ids[start_index:cur_index]
        while start_index < len(input_ids):
        
            # skip empty and too small chunks
            chunk_ids_size = len(chunk_ids)
            if chunk_ids_size > 0 and chunk_ids_size > self.splitter_params.chunk_min_tokens:
                splits.append(self.encoding.decode(chunk_ids))

            # next chunk
            start_index += self.splitter_params.tokens_per_chunk - self.splitter_params.chunk_overlap_tokens
            cur_index = min(start_index + self.splitter_params.tokens_per_chunk, len(input_ids))
            chunk_ids = input_ids[start_index:cur_index]
        return splits

    def split_text(self, text: str) -> list[str]:
        """Split text into multiple components."""
        return self.split_text_on_tokens(text)

class TokenChunkSplitter(BaseChunkSplitter):
    """Split text into chunks"""

    text_splitter : SpecialTokenTextSplitter

    def __init__(self, splitter_params : ChunkSplitterParams):
        super().__init__(splitter_params)
        self.text_splitter = SpecialTokenTextSplitter(self.splitter_params)

    def create_documents(self, texts: list[str], metadatas: list[dict] = None) -> list[Document]:
        """Create documents from input"""
        return self.text_splitter.create_documents(texts, metadatas)

    def split_documents(self, documents : list[Document]) -> list[Document]:
        """Split input into chunks"""
        return self.text_splitter.split_documents(documents)

