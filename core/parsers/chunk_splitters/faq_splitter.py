"""
    Chunk splitter based on FAQ format
"""

# pylint: disable=R0903,C0305,C0301

import copy

import tiktoken
from tiktoken.core import Encoding

from langchain.docstore.document import Document

from core.parsers.chunk_splitters.base_splitter import BaseChunkSplitter, ChunkSplitterParams

class FAQChunkSplitter(BaseChunkSplitter):
    """Split text into chunks based on tokens"""

    encoding : Encoding
    faq_line_separator : str

    __QUESTION_PREFIX = '"question":'
    __ANSWER_PREFIX   = '"answer":'

    def __init__(self, splitter_params : ChunkSplitterParams):
        super().__init__(splitter_params)
        self.encoding = tiktoken.encoding_for_model(splitter_params.model_name)
        self.faq_line_separator = "#### FAQ ####"

    def format_faq_item(self, faq_item : str) -> str:
        """Format one FAQ item"""
        result = []
        for line in faq_item.split('\n'):
            line = line.strip()
            if not line:
                continue
            if line.startswith('#'):
                continue

            if line.startswith(self.__QUESTION_PREFIX):
                line = line.removeprefix(self.__QUESTION_PREFIX)
                line = line.strip().strip('"')
                result.append(f'<h1>{line}</h1>')
                continue

            if line.startswith(self.__ANSWER_PREFIX):
                line = line.removeprefix(self.__ANSWER_PREFIX)
                line = line.strip().strip('"')
                result.append(line)
                continue

        return '\n'.join(result)

    def split_text_by_fact_line(self, text: str) -> list[str]:
        """Split incoming text by fact line"""
        splits: list[str] = text.split(self.faq_line_separator)
        splits = [self.format_faq_item(s) for s in splits if s.strip()]
        splits = [s for s in splits if s.strip()]
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
