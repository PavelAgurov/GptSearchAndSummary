"""
    File index
"""
# pylint: disable=C0301,C0103,C0304,C0303,W0611,W0511,R0913

import os
from dataclasses import dataclass

from qdrant_client import QdrantClient

from langchain.text_splitter import TextSplitter
from langchain.embeddings.base import Embeddings
from langchain.vectorstores import Qdrant
from langchain.docstore.document import Document

#TODO: index metadata (page number)

@dataclass
class SearchResult:
    """Result of the search"""
    content : str
    score   : float

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

    def _create_client(self, index_name : str) -> QdrantClient:
        if self.in_memory:
            return QdrantClient(location=":memory:")
        return QdrantClient(path = os.path.join(self.__DISK_FOLDER, index_name))

    def run_indexing(self, index_name : str, file_list : list[str], text_splitter : TextSplitter, embeddings : Embeddings) -> list[str]:
        """Index files from file_list based on text_splitter and embeddings and save into DB"""
        
        result = list[str]()

        plain_text_list = []
        for file in file_list:
            with open(file, encoding="utf-8") as f:
                plain_text_list.append(f.read())

        result.append(f'Loaded {len(plain_text_list)} document(s)')

        chunks = text_splitter.split_documents(text_splitter.create_documents(plain_text_list))
        result.append(f'Total count of chunks {len(chunks)}')

        if self.in_memory:
            Qdrant.from_documents(
                chunks,
                embeddings,
                location=":memory:",
                collection_name= self.__CHUNKS_COLLECTION_NAME,
                force_recreate=True
            )
            result.append('Index has been stored in memory')
        else:
            Qdrant.from_documents(
                chunks,
                embeddings,
                path= os.path.join(self.__DISK_FOLDER, index_name),
                collection_name= self.__CHUNKS_COLLECTION_NAME,
                force_recreate=True
            )      
            result.append('Index has been stored on disk')

        return result
    
    def similarity_search(self, index_name : str, query: str, embeddings : Embeddings, sample_count : int, score_threshold : float = None):
        """Run similarity search"""

        qdrant = Qdrant(
                    client= self._create_client(index_name),
                    collection_name= self.__CHUNKS_COLLECTION_NAME,
                    embeddings= embeddings
                )
        
        search_results : list[tuple[Document, float]] = qdrant.similarity_search_with_score(query, k= sample_count, score_threshold = score_threshold)
        return [SearchResult(s[0].page_content, s[1]) for s in search_results]

    def get_index_name_list(self) -> list[str]:
        """Get list of available indexes"""
        dir_list = os.listdir(self.__DISK_FOLDER)
        return dir_list
