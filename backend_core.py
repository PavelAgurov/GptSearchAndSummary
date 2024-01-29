"""
    Main core
"""
# pylint: disable=C0301,C0103,C0304,C0303,W0611,C0411,W1203

from dataclasses import dataclass
from typing import Callable
import logging

from core.file_indexing import FileIndex, FileIndexParams
from core.parsers.chunk_splitters.base_splitter import ChunkSplitterMode
from core.source_storage import SourceStorage
from core.llm_manager import LlmManager, LlmFactsResult
from core.document_set_manager import DocumentSetManager
from core.text_extractor import TextExtractor, TextExtractorParams
from core.parsers.chunk_splitters.base_splitter import ChunkSplitterParams
from core.kt_manager import KnowledgeTreeItem, KnowledgeTree, KnowledgeTreeManager
from core.table_extractor import TableExtractor, TableExtractorResult
from core.embedding_manager import EmbeddingManager, EmbeddingItem
from core.user_query_manager import UserQueryManager
from core.parsers.base_parser import DocumentParserParams, DocumentParserHTMLParams
from core.facts.fact_clustering import FactCluster, fact_k_means

import streamlit as st

logger : logging.Logger = logging.getLogger()

IN_MEMORY = False

@dataclass
class BackendTextExtractionParams:
    """Parameters of text extraction"""
    override_all            : bool
    run_html_llm_formatter  : bool # run LLM to convert text into HTML
    run_table_extraction    : bool
    store_as_facts_list     : bool # extract facts and store it as plain text
    fact_context            : str  # context to extact facts
    combine_html_headers    : bool # combine html headers
    show_progress_callback  : Callable[[str], None]

@dataclass
class BackendFileIndexingParams:
    """Parameters for file indexing"""
    embedding_item : EmbeddingItem
    index_name     : str
    chunk_min      : int 
    chunk_size     : int
    chunk_overlap  : int
    use_formatted  : bool
    chunk_splitter_mode : ChunkSplitterMode

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
    _SESSION_TABLE_EXTRACTOR = 'table_extractor'
    _SESSION_EMBEDDING_MANAGER = 'embedding_manager'
    _SESSION_USER_QUERY_MANAGER = 'user_query_manager'

    __MIN_PLAIN_TEXT_SIZE = 50

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
            all_secrets = {s[0]:s[1] for s in st.secrets.items()}
            st.session_state[cls._SESSION_LLM] = LlmManager(all_secrets)
        return st.session_state[cls._SESSION_LLM]

    @classmethod
    def get_embedding_manager(cls) -> EmbeddingManager:
        """Get embedding Manager"""
        if cls._SESSION_EMBEDDING_MANAGER not in st.session_state:
            st.session_state[cls._SESSION_EMBEDDING_MANAGER] = EmbeddingManager()
        return st.session_state[cls._SESSION_EMBEDDING_MANAGER]

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

    @classmethod
    def get_table_extractor(cls) -> TableExtractor:
        """Get TableExtractor"""
        if cls._SESSION_TABLE_EXTRACTOR not in st.session_state:
            st.session_state[cls._SESSION_TABLE_EXTRACTOR] = TableExtractor()
        return st.session_state[cls._SESSION_TABLE_EXTRACTOR]

    @classmethod
    def get_user_query_manager(cls) -> UserQueryManager:
        """Get UserQueryManager"""
        if cls._SESSION_USER_QUERY_MANAGER not in st.session_state:
            st.session_state[cls._SESSION_USER_QUERY_MANAGER] = UserQueryManager(IN_MEMORY)
        return st.session_state[cls._SESSION_USER_QUERY_MANAGER]

    def run_text_extraction(self, document_set : str, params : BackendTextExtractionParams) -> list[str]:
        """Extract plain text from source files"""

        source_storage  = self.get_source_storage()
        text_extractor  = self.get_text_extractor()
        llm_manager     = self.get_llm_manager()
        table_extractor = self.get_table_extractor()

        uploaded_files = source_storage.get_all_files(document_set)
        textExtractorParams = TextExtractorParams(
            params.override_all,
            params.show_progress_callback,
            DocumentParserParams(
                DocumentParserHTMLParams(
                    params.combine_html_headers,
                    ['header', 'footer', 'breadcrumb'],
                    ['head', 'script', 'button']
                )
            )
        )

        # extract plain text
        output_log : list[str] = text_extractor.text_extraction_and_save(document_set, uploaded_files, textExtractorParams)

        # additional formatting and table extraction
        if params.run_html_llm_formatter or params.run_table_extraction:
            plain_text_files = text_extractor.get_all_source_file_names(document_set, True)
            for plain_text_file_name in plain_text_files:
                plain_text = text_extractor.get_input_by_file_name(document_set, plain_text_file_name)
                if len(plain_text) < self.__MIN_PLAIN_TEXT_SIZE:
                    continue

                if params.run_html_llm_formatter:
                    self.__exec_llm_formatter(
                        document_set, 
                        plain_text_file_name, 
                        plain_text,
                        text_extractor, 
                        llm_manager, 
                        params.show_progress_callback,
                        output_log
                    )
        
                if params.run_table_extraction:
                    self.__exec_extract_tables(
                        document_set,
                        plain_text_file_name,
                        text_extractor,
                        table_extractor,
                        params.show_progress_callback,
                        output_log
                    )

        # fact extractor
        if params.store_as_facts_list:
            plain_text_files = text_extractor.get_all_source_file_names(document_set, True)
            for index, plain_text_file_name in enumerate(plain_text_files):
                params.show_progress_callback(f'Extract facts from {plain_text_file_name} ({index+1}/{len(plain_text_files)})...')
                plain_text = text_extractor.get_input_by_file_name(document_set, plain_text_file_name)
                fact_list_result : LlmFactsResult = llm_manager.get_fact_list(plain_text, params.fact_context)
                if fact_list_result.error_list:
                    error_str = "\n".join(fact_list_result.error_list)
                    output_log.append(f'ERROR. File={plain_text_file_name}. {error_str}')
                    continue
                text_extractor.save_fact_text(document_set, plain_text_file_name, fact_list_result.fact_list)


        return output_log

    def __exec_llm_formatter(
            self, 
            document_set, 
            plain_text_file_name, 
            plain_text,
            text_extractor, 
            llm_manager, 
            show_progress_callback : Callable[[str], None],
            output_log : list[str]
        ):
        """Execute LLM formatter"""
        output_log.append(f'LLM formatting of {plain_text_file_name}')
        show_progress_callback(f'Run LLM formatting of {plain_text_file_name}...')
        formatted_text_result = llm_manager.run_llm_format(plain_text)
        if formatted_text_result.error:
            output_log.append(f'ERROR {plain_text_file_name}: {formatted_text_result.error}')
        else:
            output_log.append('Saved formatted text')
            text_extractor.save_formatted_text(document_set, plain_text_file_name, formatted_text_result.output_text)

    def __exec_extract_tables(
            self,
            document_set : str,
            plain_text_file_name : str,
            text_extractor : TextExtractor, 
            table_extractor : TableExtractor, 
            show_progress_callback : Callable[[str], None],
            output_log : list[str] 
        ):
        """Extract tables from formatted document"""
        text_extractor.delete_table(document_set, plain_text_file_name)
        output_log.append(f'Table extaction from {plain_text_file_name}')
        show_progress_callback(f'Table extaction from {plain_text_file_name}...')
        formatted_text = text_extractor.get_formatted_text(document_set, plain_text_file_name)
        if len(formatted_text) < self.__MIN_PLAIN_TEXT_SIZE:
            return
        table_list_result = table_extractor.get_table_from_html(formatted_text)
        if not table_list_result:
            return
        if table_list_result.error:
            output_log.append(f'ERROR {plain_text_file_name}: {table_list_result.error}')
            return
        if not table_list_result.table_list or len(table_list_result.table_list) == 0:
            return
        table_extractor_result_json = table_extractor.get_table_extractor_result_json(table_list_result)
        output_log.append('Saved extracted table(s)')
        text_extractor.save_tables(document_set, plain_text_file_name, table_extractor_result_json)

    def run_file_indexing(self, document_set : str, params : BackendFileIndexingParams) -> list[str]:
        """Run file indexing"""

        llm_manager = self.get_llm_manager()
        file_index = self.get_file_index()
        text_extractor = self.get_text_extractor()
        embedding_manager = self.get_embedding_manager()

        fileIndexParams = FileIndexParams(
                ChunkSplitterParams(
                    params.chunk_min,
                    params.chunk_size,
                    params.chunk_overlap,
                    llm_manager.get_model_name(),
                    params.chunk_splitter_mode,
                ),
                text_extractor.FACT_LINE_SEPARATOR
        )

        input_with_meta = text_extractor.get_input_with_meta(document_set, params.use_formatted)

        indexing_result = file_index.run_indexing(
                document_set,
                params.index_name,
                input_with_meta,
                params.embedding_item.embedding_type.name,
                params.embedding_item.default_threshold,
                embedding_manager.get_embeddings(params.embedding_item.embedding_type.name),
                fileIndexParams
        )

        return indexing_result

    def similarity_search(
            self, 
            document_set : str,
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
        embedding_manager = self.get_embedding_manager()

        show_status_callback('Load index...')
        fileIndexMeta = file_index.get_file_index_meta(document_set, index_name)

        show_status_callback('Similarity search...')
        similarity_result = file_index.similarity_search(
            document_set,
            index_name,
            query, 
            embedding_manager.get_embeddings(fileIndexMeta.embedding_name), 
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
        logger.info('Build summary by LLM...')
        llm_manager = self.get_llm_manager()
        answer_result = llm_manager.build_answer(question, [c.content for c in chunk_list])
        if answer_result.error:
            return answer_result.error
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
                logger.error(f'ERROR LLM ={kt_list.error}')
        result = KnowledgeTree(triples)
        show_progress_callback('Save ...')
        kt_manager.save(name, result)
        show_progress_callback('')
        return result

    def get_tables_from_file(self, document_set : str, file_name : str) -> TableExtractorResult:
        """Load tables from file"""
        text_extractor = self.get_text_extractor()
        table_extractor = self.get_table_extractor()

        table_json = text_extractor.load_table_json(document_set, file_name)
        if not table_json or len(table_json) == 0:
            return None
        return table_extractor.get_table_extractor_result_from_json(table_json)

    def get_fact_clusters(self, selected_document_set : str, cluster_count : int, embedding_item : EmbeddingItem) -> list[FactCluster]:
        """Get fact clusters"""
        text_extractor = self.get_text_extractor()
        embedding_manager = self.get_embedding_manager()

        all_fact_files = text_extractor.get_all_facts_file_names(selected_document_set, True)

        full_fact_list = []
        for fact_file in all_fact_files:
            facts = text_extractor.get_facts_from_file(selected_document_set, fact_file)
            full_fact_list.extend(facts)
        
        embedding_encode_call = embedding_manager.get_embeddings_encode_call(embedding_item.embedding_type.name)
        return fact_k_means(full_fact_list, cluster_count, embedding_encode_call)
