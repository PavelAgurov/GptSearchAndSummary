"""
    Main core
"""
# pylint: disable=C0301,C0103,C0304,C0303,W0611,C0411

from core.file_index import FileIndex
from core.source_index import SourceIndex
from core.llm_manager import LlmManager
from core.text_extractor import TextExtractor

import streamlit as st

from langchain.text_splitter import TokenTextSplitter

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
    def get_source_index(cls) -> SourceIndex:
        """Get SourceIndex"""
        if cls._SESSION_SOURCE_INDEX not in st.session_state:
            st.session_state[cls._SESSION_SOURCE_INDEX] = SourceIndex()
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
        return self.get_text_extractor().text_extraction(uploaded_files, True)

    def run_file_indexing(self, chunk_size : int, chunk_overlap : int) -> list[str]:
        """Run file indexing"""

        llm_manager = self.get_llm()
        file_index = self.get_file_index()
        text_extractor = self.get_text_extractor()

        text_splitter = TokenTextSplitter(
                            chunk_size    = chunk_size,
                            chunk_overlap = chunk_overlap,
                            model_name    = llm_manager.get_model_name()
                        )

        text_files = text_extractor.get_all_files()

        indexing_result = file_index.run_indexing(
                text_files,
                text_splitter,
                llm_manager.get_embeddings()
        )

        return indexing_result
