"""
    File index
"""
# pylint: disable=C0301,C0103,C0304,C0303,W0611,W0511,R0913

import os
import json
from dataclasses import dataclass, asdict

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

@dataclass
class FileIndexMeta:
    """Meta info about index"""
    chunkSplitterParams : FileIndexParams
    embedding_name       : str

class FileIndex:
    """File index class"""
    in_memory : bool
    full_index_folder : str

    # folder structure:
    #   .file-index
    #      \<index-name>
    #         \index
    #             <Qdrant db>
    #         index_meta.json

    __DISK_FOLDER = '.file-index'
    __INDEX_FOLDER = 'index'
    __CHUNKS_COLLECTION_NAME = 'chunks'
    __INDEX_META_FILE = 'index_meta.json'

    def __init__(self, in_memory : bool):
        self.in_memory = in_memory
        if not in_memory:
            os.makedirs(self.__DISK_FOLDER, exist_ok=True)

    def run_indexing(
            self, 
            index_name  : str,
            input_with_meta : list[tuple([str, {}])],
            embedding_name : str,
            embeddings : Embeddings, 
            index_params : FileIndexParams) -> list[str]:
        """Index files from file_list based on text_splitter and embeddings and save into DB"""
        
        log = list[str]()

        log.append(f'Loaded {len(input_with_meta)} document(s)')

        token_chunk_splitter = TokenChunkSplitter(index_params.splitter_params)
        chunks  = token_chunk_splitter.split_into_documents(input_with_meta)
        log.append(f'Total count of chunks {len(chunks)}')

        # create index folder
        if not self.in_memory:
            os.makedirs(os.path.join(self.__DISK_FOLDER, index_name), exist_ok=True)

        # save meta data
        file_index_meta = FileIndexMeta(
            index_params,
            embedding_name
        )
        with open(os.path.join(self.__DISK_FOLDER, index_name, self.__INDEX_META_FILE), "wt", encoding="utf-8") as f:
            json.dump(asdict(file_index_meta), f, indent=4)

        # create db
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
                path = os.path.join(self.__DISK_FOLDER, index_name, self.__INDEX_FOLDER),
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
            client = QdrantClient(path = os.path.join(self.__DISK_FOLDER, index_name, self.__INDEX_FOLDER))

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

    def get_file_index_meta(self, index_name : str) -> FileIndexMeta:
        """Get meta info about index"""
        with open(os.path.join(self.__DISK_FOLDER, index_name, self.__INDEX_META_FILE), "rt", encoding="utf-8") as f:
            json_data = json.load(f)

        return FileIndexMeta(
            FileIndexParams(
                ChunkSplitterParams(**json_data['chunkSplitterParams']['splitter_params'])
            ),
            json_data['embedding_name']
        )