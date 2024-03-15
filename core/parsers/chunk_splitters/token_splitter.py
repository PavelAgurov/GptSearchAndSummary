"""
    Chunk splitter based on tokens
"""

# pylint: disable=R0903,C0305,C0301

import copy

import tiktoken
from tiktoken.core import Encoding

from langchain.docstore.document import Document

from core.parsers.chunk_splitters.base_splitter import BaseChunkSplitter, ChunkSplitterParams

class TokenChunkSplitter(BaseChunkSplitter):
    """Split text into chunks based on tokens"""

    encoding : Encoding

    def __init__(self, splitter_params : ChunkSplitterParams):
        super().__init__(splitter_params)
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

    def split_into_documents(self, input_with_meta : list[tuple[str, dict]]) -> list[Document]:
        """Split input into chunks Documents"""
        documents = list[Document]()
        for input_item in input_with_meta:
            index = -1
            input_text = input_item[0]
            input_meta = input_item[1]
            for chunk in self.split_text_on_tokens(input_text):
                if input_meta:
                    meta = copy.deepcopy(input_meta)
                else:
                    meta = {}
                index = input_text.find(chunk, index + 1)
                meta["p_offset"] = index
                new_doc = Document(page_content=chunk, metadata= meta)
                documents.append(new_doc)

        return documents
