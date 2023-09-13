"""
    Main core
"""
# pylint: disable=C0301,C0103,C0304,C0303,W0611,C0411

from dataclasses import dataclass
from typing import Callable

from core.file_indexing import FileIndex, FileIndexParams
from core.source_storage import SourceStorage
from core.llm_manager import LlmManager
from core.document_set_manager import DocumentSetManager
from core.text_extractor import TextExtractor, TextExtractorParams
from core.parsers.chunk_splitters.base_splitter import ChunkSplitterParams
from core.kt_manager import KnowledgeTreeItem, KnowledgeTree, KnowledgeTreeManager

import streamlit as st

IN_MEMORY = False

@dataclass
class BackendChunk:
    """Chunk of search result"""
    content   : str
    score     : float
    metadata  : dict[str, str]
    llm_score : float
    llm_expl  : str

class BackEndCore():
    """Main back-end manager"""

    _SESSION_FILE_INDEX = 'file_index'
    _SESSION_SOURCE_INDEX = 'source_index'
    _SESSION_LLM = 'llm_instance'
    _SESSION_TEXT_EXTRACTOR = 'plain_text_extractor'
    _SESSION_DOCUMENT_SET = 'document_set_manager'
    _SESSION_KT_MANAGER = 'knowledge_tree_manager'

    def __new__(cls):
        """Singleton"""
        if not hasattr(cls, 'instance'):
            cls.instance = super(BackEndCore, cls).__new__(cls)
        return cls.instance

    @classmethod
    def get_document_set_manager(cls) -> DocumentSetManager:
        """Get DocumentSetManager"""
        if cls._SESSION_DOCUMENT_SET not in st.session_state:
            document_set_manager= DocumentSetManager(IN_MEMORY)
            document_set_manager.load()
            st.session_state[cls._SESSION_DOCUMENT_SET] = document_set_manager

        return st.session_state[cls._SESSION_DOCUMENT_SET]

    @classmethod
    def get_file_index(cls) -> FileIndex:
        """Get FileIndex"""
        if cls._SESSION_FILE_INDEX not in st.session_state:
            st.session_state[cls._SESSION_FILE_INDEX] = FileIndex(IN_MEMORY)
        return st.session_state[cls._SESSION_FILE_INDEX]

    @classmethod
    def get_source_storage(cls) -> SourceStorage:
        """Get SourceIndex"""
        if cls._SESSION_SOURCE_INDEX not in st.session_state:
            st.session_state[cls._SESSION_SOURCE_INDEX] = SourceStorage(IN_MEMORY)
        return st.session_state[cls._SESSION_SOURCE_INDEX]

    @classmethod
    def get_llm_manager(cls) -> LlmManager:
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

    @classmethod
    def get_knowledge_tree_manager(cls) -> KnowledgeTreeManager:
        """Get KnowledgeTreeManager"""
        if cls._SESSION_KT_MANAGER not in st.session_state:
            st.session_state[cls._SESSION_KT_MANAGER] = KnowledgeTreeManager(IN_MEMORY)
        return st.session_state[cls._SESSION_KT_MANAGER]

    def run_text_extraction(self, document_set : str) -> list[str]:
        """Extract plain text from source files"""
        uploaded_files = self.get_source_storage().get_all_files(document_set)
        textExtractorParams = TextExtractorParams(True)
        return self.get_text_extractor().text_extraction(document_set, uploaded_files, textExtractorParams)

    def run_file_indexing(self,
                          document_set : str,
                          embedding_name : str, 
                          index_name : str, 
                          chunk_min : int, 
                          chunk_size : int, 
                          chunk_overlap : int) -> list[str]:
        """Run file indexing"""

        llm_manager = self.get_llm_manager()
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

        input_with_meta = text_extractor.get_input_with_meta(document_set)

        indexing_result = file_index.run_indexing(
                document_set,
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
            add_llm_score : bool,
            llm_threshold : float,
            show_status_callback : Callable[[str], None]) -> list[BackendChunk]:
        """Run similarity search"""

        llm_manager = self.get_llm_manager()
        file_index = self.get_file_index()

        show_status_callback('Load index...')
        fileIndexMeta = file_index.get_file_index_meta(index_name)

        show_status_callback('Similarity search...')
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
                ''
            )
            for similarity_item in similarity_result
        ]

        if add_llm_score:
            llm_chunk_list = []
            for chunk_index, chunk in enumerate(chunk_list):
                show_status_callback(f'LLM score {chunk_index+1}/{len(chunk_list)}...')
                relevance_score = llm_manager.get_relevance_score(query, chunk.content)
                if relevance_score.llm_score >= llm_threshold:
                    chunk.llm_score = relevance_score.llm_score
                    chunk.llm_expl = relevance_score.llm_expl
                    llm_chunk_list.append(chunk)
            chunk_list = llm_chunk_list

        show_status_callback('')
        return chunk_list

    def build_answer(self, question : str, chunk_list : list[BackendChunk]) -> str:
        """Build LLM answer"""
        llm_manager = self.get_llm_manager()
        answer_result = llm_manager.build_answer(question, [c.content for c in chunk_list])
        return answer_result.answer

    def build_knowledge_tree(
            self,
            document_set : str,
            name : str,
            input_file_list : list[str],
            append_mode : bool,
            show_progress_callback : Callable[[str], None]
        ) -> KnowledgeTree:
        """Build knowledge tree"""

        text_extractor = self.get_text_extractor()
        llm_manager = self.get_llm_manager()
        kt_manager = self.get_knowledge_tree_manager()

        existed_triples = []
        if append_mode:
            existed_tree = kt_manager.load(name)
            if not existed_tree.error and existed_tree.triples and len(existed_tree.triples) > 0:
                existed_triples = existed_tree.triples

        input_list_text_with_meta = text_extractor.get_input_with_meta_by_files(document_set, input_file_list)
        triples = list[KnowledgeTreeItem](existed_triples)
        for index, input_item in enumerate(input_list_text_with_meta):
            show_progress_callback(f'Process {index+1}/{len(input_list_text_with_meta)}...')
            kt_list = llm_manager.build_knowledge_tree(input_item[0])
            if not kt_list.error:
                for kt_item in kt_list.triples:
                    triples.append(KnowledgeTreeItem(
                        kt_item.subject,
                        kt_item.predicate,
                        kt_item.objects,
                        input_item[1]
                    ))
            else:
                print(f'ERROR LLM ={kt_list.error}')
        result = KnowledgeTree(triples)
        show_progress_callback('Save ...')
        kt_manager.save(name, result)
        show_progress_callback('')
        return result
