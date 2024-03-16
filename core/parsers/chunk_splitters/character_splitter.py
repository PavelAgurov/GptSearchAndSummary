"""
    Chunk splitter by defined characters
"""

# pylint: disable=R0903,C0305,C0301

from langchain.docstore.document import Document
from langchain_text_splitters import CharacterTextSplitter

from core.parsers.chunk_splitters.base_splitter import BaseChunkSplitter, ChunkSplitterParams

class CharacterSplitter(BaseChunkSplitter):
    """Split based on langchain CharacterTextSplitter"""

    text_splitter : CharacterTextSplitter

    def __init__(self, splitter_params : ChunkSplitterParams):
        super().__init__(splitter_params)
        self.text_splitter = CharacterTextSplitter(
            separator="\n\n",
            chunk_size    = splitter_params.tokens_per_chunk,
            chunk_overlap = splitter_params.chunk_overlap_tokens,
            length_function=len,
            is_separator_regex=False,
        )

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
