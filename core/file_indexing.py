"""
    File index
"""
# pylint: disable=C0301,C0103,C0304,C0303,W0611,W0511,R0913

import os
import shutil
import logging
from dataclasses import dataclass
from typing import Optional
from dataclasses_json import dataclass_json

from qdrant_client import QdrantClient

from langchain.embeddings.base import Embeddings
from langchain_community.vectorstores import Qdrant
from langchain.docstore.document import Document

from core.parsers.chunk_splitters.base_splitter import ChunkSplitterParams, ChunkSplitterMode
from core.parsers.chunk_splitters.token_splitter import TokenChunkSplitter
from core.parsers.chunk_splitters.fact_splitter import FactChunkSplitter
from core.parsers.chunk_splitters.faq_splitter import FAQChunkSplitter

logger : logging.Logger = logging.getLogger()

class FileIndexingError(Exception):
    """File indexing related exception"""

@dataclass_json
@dataclass
class FileIndexParams:
    """Parameters for indexing"""
    splitter_params     : ChunkSplitterParams
    fact_line_separator : str

@dataclass_json
@dataclass
class SearchResult:
    """Result of the search"""
    content   : str
    score     : float
    metadata  : {}

@dataclass_json
@dataclass
class FileIndexMeta:
    """Meta info about index"""
    chunkSplitterParams : FileIndexParams
    document_set        : str
    embedding_name      : str
    default_threshold   : Optional[float] = None
    error               : Optional[str] = None

class FileIndex:
    """File index class"""
    in_memory : bool
    full_index_folder : str

    # folder structure:
    #   .document-index
    #      \<index-name>
    #         \index
    #             <Qdrant db>
    #         \chunks
    #             chunk-nnnnn.txt
    #         index_meta.json

    __DISK_FOLDER = '.document-index'
    __INDEX_FOLDER = 'index'
    __CHUNKS_FOLDER = 'chunks'
    __CHUNKS_COLLECTION_NAME = 'chunks'
    __INDEX_META_FILE = 'index_meta.json'

    def __init__(self, in_memory : bool):
        self.in_memory = in_memory
        if not in_memory:
            os.makedirs(self.__DISK_FOLDER, exist_ok=True)

    def get_chunk_name(self, index : int) -> str:
        """Get chunk file name by index"""
        return f'chunk-{index:05}.txt'

    def save_chunks(
            self, 
            document_set : str, 
            index_name : str, 
            chunks : list[Document]):
        """Save chunks"""
        chunks_folder = os.path.join(self.__DISK_FOLDER, document_set, index_name, self.__CHUNKS_FOLDER)
        if os.path.isdir(chunks_folder):
            shutil.rmtree(chunks_folder)
        os.makedirs(chunks_folder)
        for index, document in enumerate(chunks):
            chunk_file_name = self.get_chunk_name(index)
            with open(os.path.join(chunks_folder, chunk_file_name), "wt", encoding="utf-8") as f:
                f.write(document.page_content)

    def run_indexing(
            self,
            document_set : str,
            index_name  : str,
            input_with_meta : list[tuple([str, {}])],
            embedding_name : str,
            default_threshold : float,
            embeddings : Embeddings, 
            index_params : FileIndexParams) -> list[str]:
        """Index files from file_list based on text_splitter and embeddings and save into DB"""
        
        log = list[str]()

        log.append(f'Loaded {len(input_with_meta)} document(s)')

        chunk_splitter_value = index_params.splitter_params.chunk_splitter_mode.value
        if  chunk_splitter_value== ChunkSplitterMode.FACT_LIST.value:
            fact_chunk_splitter = FactChunkSplitter(index_params.splitter_params, index_params.fact_line_separator)
            chunks  = fact_chunk_splitter.split_into_documents(input_with_meta)
        elif  chunk_splitter_value== ChunkSplitterMode.FAQ_LIST.value:
            fact_chunk_splitter = FAQChunkSplitter(index_params.splitter_params)
            chunks  = fact_chunk_splitter.split_into_documents(input_with_meta)
        elif chunk_splitter_value== ChunkSplitterMode.TOKEN_MODE.value:
            token_chunk_splitter = TokenChunkSplitter(index_params.splitter_params)
            chunks  = token_chunk_splitter.split_into_documents(input_with_meta)
        else:
            raise FileIndexingError(f'Unsupported ChunkSplitterMode: {chunk_splitter_value}')
        
        log.append(f'Total count of chunks {len(chunks)}')

        # remove index before creating
        self.delete_index(document_set, index_name)

        # save all chunks
        self.save_chunks(document_set, index_name, chunks)

        # create index folder
        if not self.in_memory:
            os.makedirs(os.path.join(self.__DISK_FOLDER, document_set, index_name), exist_ok=True)

        # save meta data
        file_index_meta = FileIndexMeta(
            index_params,
            document_set,
            embedding_name,
            default_threshold
        )

        meta_json_str = file_index_meta.to_json(indent=4)  # pylint: disable=E1101
        with open(os.path.join(self.__DISK_FOLDER, document_set, index_name, self.__INDEX_META_FILE), "wt", encoding="utf-8") as f:
            f.write(meta_json_str)

        # create db
        qdrant = None
        try:
            if self.in_memory:
                qdrant = Qdrant.from_documents( # pylint: disable=E1101
                    chunks,
                    embeddings,
                    location=":memory:",
                    collection_name= self.__CHUNKS_COLLECTION_NAME,
                    force_recreate=True
                )
                log.append('Index has been stored in memory')
            else:
                qdrant = Qdrant.from_documents( # pylint: disable=E1101
                    chunks,
                    embeddings,
                    path = os.path.join(self.__DISK_FOLDER, document_set, index_name, self.__INDEX_FOLDER),
                    collection_name= self.__CHUNKS_COLLECTION_NAME,
                    force_recreate=True
                )      
                log.append('Index has been stored on disk')
        except Exception as error: # pylint: disable=W0718
            log.append(error)
            logger.error(error)

        if qdrant is not None:
            qdrant.client.close()

        return log
    
    def similarity_search(
            self, 
            document_set : str,
            index_name : str, 
            query: str, 
            embeddings : Embeddings, 
            sample_count : int, 
            score_threshold : float) -> list[SearchResult]:
        """Run similarity search"""

        if self.in_memory:
            client = QdrantClient(location=":memory:")
        else:
            index_folder = os.path.join(self.__DISK_FOLDER, document_set, index_name, self.__INDEX_FOLDER)
            client = QdrantClient(path = index_folder)

        qdrant = Qdrant( # pylint: disable=E1102
                    client= client,
                    collection_name= self.__CHUNKS_COLLECTION_NAME,
                    embeddings= embeddings
                )
        
        if score_threshold == 0:
            score_threshold = None
        
        search_results : list[tuple[Document, float]] = qdrant.similarity_search_with_score(query, k= sample_count, score_threshold = score_threshold)
        return [SearchResult(s[0].page_content, s[1], s[0].metadata) for s in search_results]

    def get_index_name_list(self, document_set : str) -> list[str]:
        """Get list of available indexes"""
        index_folder = os.path.join(self.__DISK_FOLDER, document_set)
        if not os.path.isdir(index_folder):
            return []
        return os.listdir(index_folder)

    def get_file_index_meta(self, document_set : str, index_name : str) -> FileIndexMeta:
        """Get meta info about index"""
        try:
            with open(os.path.join(self.__DISK_FOLDER, document_set, index_name, self.__INDEX_META_FILE), "rt", encoding="utf-8") as f:
                json_data = f.read()
            file_index_meta = FileIndexMeta.from_json(json_data) # pylint: disable=E1101
            return file_index_meta
        except Exception as error: # pylint: disable=W0718
            logger.error(error)
            return FileIndexMeta(None, None, None, error)
    
    def delete_index(self, document_set : str, index_name : str):
        """Delete existed index"""
        index_folder = os.path.join(self.__DISK_FOLDER, document_set, index_name)
        if os.path.isdir(index_folder):
            shutil.rmtree(index_folder)