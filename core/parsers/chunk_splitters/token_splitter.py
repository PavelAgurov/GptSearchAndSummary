"""
    Chunk splitter based on tokens
"""

# pylint: disable=R0903,C0305

from langchain.docstore.document import Document
from langchain.text_splitter import TokenTextSplitter

from core.parsers.chunk_splitters.base_splitter import BaseChunkSplitter, ChunkSplitterParams

class TokenChunkSplitter(BaseChunkSplitter):
    """Split text into chunks"""

    text_splitter : TokenTextSplitter

    def __init__(self, splitter_params : ChunkSplitterParams):
        super().__init__(splitter_params)
        self.text_splitter = TokenTextSplitter(
                            chunk_size    = self.splitter_params.chunk_size_tokens,
                            chunk_overlap = self.splitter_params.chunk_overlap_tokens,
                            model_name    = self.splitter_params.model_name
                        )


    def create_documents(self, texts: list[str], metadatas: list[dict] = None) -> list[Document]:
        """Create documents from input"""
        return self.text_splitter.create_documents(texts, metadatas)

    def split_documents(self, documents : list[Document]) -> list[Document]:
        """Split input into chunks"""
        chunk_list = self.text_splitter.split_documents(documents)

        result = list[Document]()
        for chunk in chunk_list:
            
            # cut no content chunks
            if not chunk.page_content:
                continue
            
            # cut small chunks
            if len(chunk.page_content) < self.splitter_params.chunk_min_chars:
                continue

            result.append(chunk)

        return result

