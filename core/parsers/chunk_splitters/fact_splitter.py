"""
    Chunk splitter based on facts
"""

# pylint: disable=R0903,C0305,C0301

import copy

import tiktoken
from tiktoken.core import Encoding

from langchain.docstore.document import Document

from core.parsers.chunk_splitters.base_splitter import BaseChunkSplitter, ChunkSplitterParams

class FactChunkSplitter(BaseChunkSplitter):
    """Split text into chunks based on tokens"""

    encoding : Encoding
    fact_line_separator : str

    def __init__(self, splitter_params : ChunkSplitterParams, fact_line_separator : str):
        super().__init__(splitter_params)
        self.encoding = tiktoken.encoding_for_model(splitter_params.model_name)
        self.fact_line_separator = fact_line_separator

    def split_text_by_fact_line(self, text: str) -> list[str]:
        """Split incoming text by fact line"""
        splits: list[str] = text.split(self.fact_line_separator)
        splits= [s.strip() for s in splits if s.strip()]
        return splits

    def split_into_documents(self, input_with_meta : list[tuple([str, {}])]) -> list[Document]:
        """Split input into chunks Documents"""
        documents = list[Document]()
        for input_item in input_with_meta:
            index = -1
            input_text = input_item[0]
            input_meta = input_item[1]
            for chunk in self.split_text_by_fact_line(input_text):
                if input_meta:
                    meta = copy.deepcopy(input_meta)
                else:
                    meta = {}
                index = input_text.find(chunk, index + 1)
                meta["p_offset"] = index
                new_doc = Document(page_content=chunk, metadata= meta)
                documents.append(new_doc)

        return documents
