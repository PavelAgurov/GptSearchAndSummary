"""
    File index
"""
# pylint: disable=C0301,C0103,C0304,C0303,W0611,W0511,R0913

import os
from dataclasses import dataclass

from qdrant_client import QdrantClient

from langchain.embeddings.base import Embeddings
from langchain.vectorstores import Qdrant
from langchain.docstore.document import Document

from core.parsers.chunk_splitters.base_splitter import ChunkSplitterParams
from core.parsers.chunk_splitters.token_splitter import TokenChunkSplitter

@dataclass
class FileIndexParams:
    """Parameters for indexing"""
    splitter_params : ChunkSplitterParams

@dataclass
class SearchResult:
    """Result of the search"""
    content  : str
    score    : float
    metadata : {}

class FileIndex:
    """File index class"""
    in_memory : bool

    __DISK_FOLDER = '.file-index'
    __CHUNKS_COLLECTION_NAME = 'chunks'

    def __init__(self, in_memory : bool):
        self.in_memory = in_memory
        if not in_memory:
            if not os.path.isdir(self.__DISK_FOLDER):
                os.mkdir(self.__DISK_FOLDER)

    def run_indexing(
            self, 
            index_name : str, 
            file_list  : list[str], 
            embeddings : Embeddings, 
            index_params : FileIndexParams) -> list[str]:
        """Index files from file_list based on text_splitter and embeddings and save into DB"""
        
        log = list[str]()

        plain_text_list = list[str]()
        metadatas       = list[dict]()
        for file in file_list:
            with open(file, encoding="utf-8") as f:
                plain_text_list.append(f.read())
            metadatas.append({"p_source" : os.path.basename(file)})
        log.append(f'Loaded {len(plain_text_list)} document(s)')

        token_chunk_splitter = TokenChunkSplitter(index_params.splitter_params)
        chunks  = token_chunk_splitter.split_into_documents(plain_text_list, metadatas)
        log.append(f'Total count of chunks {len(chunks)}')

        if self.in_memory:
            Qdrant.from_documents(
                chunks,
                embeddings,
                location=":memory:",
                collection_name= self.__CHUNKS_COLLECTION_NAME,
                force_recreate=True
            )
            log.append('Index has been stored in memory')
        else:
            Qdrant.from_documents(
                chunks,
                embeddings,
                path= os.path.join(self.__DISK_FOLDER, index_name),
                collection_name= self.__CHUNKS_COLLECTION_NAME,
                force_recreate=True
            )      
            log.append('Index has been stored on disk')

        return log
    
    def similarity_search(
            self, 
            index_name : str, 
            query: str, 
            embeddings : Embeddings, 
            sample_count : int, 
            score_threshold : float) -> list[SearchResult]:
        """Run similarity search"""

        if self.in_memory:
            client = QdrantClient(location=":memory:")
        else:
            client = QdrantClient(path = os.path.join(self.__DISK_FOLDER, index_name))

        qdrant = Qdrant(
                    client= client,
                    collection_name= self.__CHUNKS_COLLECTION_NAME,
                    embeddings= embeddings
                )
        
        if score_threshold == 0:
            score_threshold = None
        
        search_results : list[tuple[Document, float]] = qdrant.similarity_search_with_score(query, k= sample_count, score_threshold = score_threshold)
        return [SearchResult(s[0].page_content, s[1], s[0].metadata) for s in search_results]

    def get_index_name_list(self) -> list[str]:
        """Get list of available indexes"""
        dir_list = os.listdir(self.__DISK_FOLDER)
        return dir_list
