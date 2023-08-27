"""
    Main core
"""
# pylint: disable=C0301,C0103,C0304,C0303,W0611,C0411

from core.file_indexing import FileIndex, FileIndexParams
from core.source_storage import SourceStorage
from core.llm_manager import LlmManager
from core.text_extractor import TextExtractor, TextExtractorParams
from core.parsers.chunk_splitters.base_splitter import ChunkSplitterParams

import streamlit as st

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

    def run_file_indexing(self, index_name : str, chunk_min : int, chunk_size : int, chunk_overlap : int) -> list[str]:
        """Run file indexing"""

        llm_manager = self.get_llm()
        file_index = self.get_file_index()
        text_extractor = self.get_text_extractor()

        text_files = text_extractor.get_all_files()

        fileIndexParams = FileIndexParams(
                splitter_params= ChunkSplitterParams(
                    chunk_min, 
                    chunk_size, 
                    chunk_overlap,
                    llm_manager.get_model_name()
                )
        )

        indexing_result = file_index.run_indexing(
                index_name,
                text_files,
                llm_manager.get_embeddings(),
                fileIndexParams
        )

        return indexing_result
