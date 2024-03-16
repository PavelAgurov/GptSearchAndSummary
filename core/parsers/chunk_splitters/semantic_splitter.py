"""
    Chunk splitter based langchain SemanticChunker
"""

# pylint: disable=R0903,C0305,C0301

from langchain.docstore.document import Document
from langchain_experimental.text_splitter import SemanticChunker
from langchain_community.embeddings import SentenceTransformerEmbeddings

from core.parsers.chunk_splitters.base_splitter import BaseChunkSplitter, ChunkSplitterParams

class SemanticSplitter(BaseChunkSplitter):
    """Split text based on langchain SemanticChunker"""

    text_splitter : SemanticChunker

    def __init__(self, splitter_params : ChunkSplitterParams):
        super().__init__(splitter_params)
        embedding = SentenceTransformerEmbeddings(
                model_name= 'sentence-transformers/all-MiniLM-L6-v2',
                model_kwargs={"device": "cpu"}
            )
        self.text_splitter = SemanticChunker(embedding)

    def split_into_documents(self, input_with_meta : list[tuple[str, dict]]) -> list[Document]:
        """Split input into chunks Documents"""

        texts: list[str] = []
        metadatas : list[dict] = []
        for input_item in input_with_meta:
            input_text = input_item[0]
            input_meta = input_item[1]
            texts.append(input_text)
            metadatas.append(input_meta)

        documents = self.text_splitter.create_documents(texts, metadatas)

        # documents = list[Document]()
        # for input_item in input_with_meta:
        #     index = -1
        #     input_text = input_item[0]
        #     input_meta = input_item[1]
        #     for chunk in self.split_text_on_tokens(input_text):
        #         if input_meta:
        #             meta = copy.deepcopy(input_meta)
        #         else:
        #             meta = {}
        #         index = input_text.find(chunk, index + 1)
        #         meta["p_offset"] = index
        #         new_doc = Document(page_content=chunk, metadata= meta)
        #         documents.append(new_doc)

        return documents
