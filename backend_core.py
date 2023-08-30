"""
    Main core
"""
# pylint: disable=C0301,C0103,C0304,C0303,W0611,C0411

from dataclasses import dataclass

from core.file_indexing import FileIndex, FileIndexParams
from core.source_storage import SourceStorage
from core.llm_manager import LlmManager
from core.text_extractor import TextExtractor, TextExtractorParams
from core.parsers.chunk_splitters.base_splitter import ChunkSplitterParams

import streamlit as st

@dataclass
class BackendChunk:
    """Chunk of search result"""
    content   : str
    score     : float
    metadata  : {}
    llm_score : float
    llm_expl  : str

class BackEndCore():
    """Main back-end manager"""

    _SESSION_FILE_INDEX = 'file_index'
    _SESSION_SOURCE_INDEX = 'source_index'
    _SESSION_LLM = 'llm_instance'
    _SESSION_TEXT_EXTRACTOR = 'plain_text_extractor'

    def __new__(cls):
        """Singleton"""
        if not hasattr(cls, 'instance'):
            cls.instance = super(BackEndCore, cls).__new__(cls)
        return cls.instance

    @classmethod
    def get_file_index(cls) -> FileIndex:
        """Get FileIndex"""
        if cls._SESSION_FILE_INDEX not in st.session_state:
            st.session_state[cls._SESSION_FILE_INDEX] = FileIndex(False)
        return st.session_state[cls._SESSION_FILE_INDEX]

    @classmethod
    def get_source_index(cls) -> SourceStorage:
        """Get SourceIndex"""
        if cls._SESSION_SOURCE_INDEX not in st.session_state:
            st.session_state[cls._SESSION_SOURCE_INDEX] = SourceStorage()
        return st.session_state[cls._SESSION_SOURCE_INDEX]

    @classmethod
    def get_llm(cls) -> LlmManager:
        """Get LLM Manager"""
        if cls._SESSION_LLM not in st.session_state:
            st.session_state[cls._SESSION_LLM] = LlmManager()
        return st.session_state[cls._SESSION_LLM]

    @classmethod
    def get_text_extractor(cls) -> TextExtractor:
        """Get TextExtractor"""
        if cls._SESSION_TEXT_EXTRACTOR not in st.session_state:
            st.session_state[cls._SESSION_TEXT_EXTRACTOR] = TextExtractor()
        return st.session_state[cls._SESSION_TEXT_EXTRACTOR]

    def run_text_extraction(self) -> list[str]:
        """Extract plain text from source files"""
        uploaded_files = self.get_source_index().get_all_files()
        textExtractorParams = TextExtractorParams(True)
        return self.get_text_extractor().text_extraction(uploaded_files, textExtractorParams)

    def run_file_indexing(self, 
                          embedding_name : str, 
                          index_name : str, 
                          chunk_min : int, 
                          chunk_size : int, 
                          chunk_overlap : int) -> list[str]:
        """Run file indexing"""

        llm_manager = self.get_llm()
        file_index = self.get_file_index()
        text_extractor = self.get_text_extractor()

        fileIndexParams = FileIndexParams(
                splitter_params= ChunkSplitterParams(
                    chunk_min, 
                    chunk_size, 
                    chunk_overlap,
                    llm_manager.get_model_name()
                )
        )

        input_with_meta = text_extractor.get_input_with_meta()

        indexing_result = file_index.run_indexing(
                index_name,
                input_with_meta,
                embedding_name,
                llm_manager.get_embeddings(embedding_name),
                fileIndexParams
        )

        return indexing_result

    def similarity_search(
            self, 
            index_name : str, 
            query: str, 
            sample_count : int, 
            score_threshold : float,
            add_llm_score : bool) -> list[BackendChunk]:
        """Run similarity search"""

        llm_manager = self.get_llm()
        file_index = self.get_file_index()

        fileIndexMeta = file_index.get_file_index_meta(index_name)

        similarity_result = file_index.similarity_search(
            index_name,
            query, 
            llm_manager.get_embeddings(fileIndexMeta.embedding_name), 
            sample_count, 
            score_threshold
        )

        chunk_list = [
            BackendChunk(
                similarity_item.content,
                similarity_item.score,
                similarity_item.metadata,
                0,
                None
            )
            for similarity_item in similarity_result
        ]

        if add_llm_score:
            for chunk in chunk_list:
                relevance_score = llm_manager.get_relevance_score(query, chunk.content)
                chunk.llm_score = relevance_score.llm_score
                chunk.llm_expl = relevance_score.llm_expl

        return chunk_list
