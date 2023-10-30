"""
    User query manager
"""
# pylint: disable=C0301,C0103,C0304,C0303,W0611,R1716

import os

from dataclasses import dataclass

@dataclass
class UserQueryItem:
    """One table"""
    query : str
    answer: str


class UserQueryManager:
    """User query manager class"""

    in_memory : bool
    __DISK_FOLDER = '.document-user-query'
    __FILE_NAME   = 'log_query.txt'

    __QUERY_PREFIX  = 'Q:'
    __ANSWER_PREFIX = 'A:'
    __SETUP_PREFIX  = 'S:'

    __memory : dict[str, list[UserQueryItem]]

    def __init__(self, in_memory : bool):
        self.in_memory = in_memory
        if not self.in_memory:
            os.makedirs(self.__DISK_FOLDER, exist_ok=True)
        else:
            self.__memory = dict[str, list[UserQueryItem]]()

    def __get_storage_folder(self, document_set : str):
        storage_folder = os.path.join(self.__DISK_FOLDER, document_set)
        if not self.in_memory:
            os.makedirs(storage_folder, exist_ok=True)
        return storage_folder
  
    def __get_file_name(self, document_set : str):
        return os.path.join(self.__get_storage_folder(document_set), self.__FILE_NAME)

    def log_query(self, document_set: str, query : str, answer : str = '', setup_str : str = ''):
        """Save query and answer"""
        full_file_name = self.__get_file_name(document_set)

        if self.in_memory:
            if not self.__memory[full_file_name]:
                self.__memory[full_file_name] = list[UserQueryItem]()
            self.__memory[full_file_name].append(UserQueryItem(query, answer))
            return

        with open(full_file_name,"at", encoding="utf-8") as file_txt:
            file_txt.write(f'{self.__QUERY_PREFIX}{query}\n')
            if answer:
                file_txt.write(f'{self.__ANSWER_PREFIX}{answer}\n')
            if setup_str:
                file_txt.write(f'{self.__SETUP_PREFIX}{setup_str}\n')
            file_txt.write('\n')

    def get_query_history(self, document_set: str, limit : int = 0) -> list[UserQueryItem]:
        """Get query histoty"""
        full_file_name = self.__get_file_name(document_set)

        if self.in_memory:
            result_from_memory = self.__memory[full_file_name]
            if not result_from_memory:
                return []
            if not limit:
                return result_from_memory
            return result_from_memory[:limit]

        if not os.path.isfile(full_file_name):
            return []

        result = list[UserQueryItem]()
        with open(full_file_name,"rt", encoding="utf-8") as file_txt:
            all_lines = file_txt.readlines()

        query  = ''
        answer = ''
        for line in all_lines:
            if not line:
                continue

            if line.startswith(self.__QUERY_PREFIX):
                if query:
                    result.append(UserQueryItem(query, answer))
                    if limit > 0 and len(result) >= limit:
                        break
                query = line.removeprefix(self.__QUERY_PREFIX).strip('\n')
                answer = ''
                continue

            if line.startswith(self.__ANSWER_PREFIX):
                answer = line.removeprefix(self.__ANSWER_PREFIX).strip('\n')
                continue

        if limit > 0 and len(result) < limit:
            result.append(UserQueryItem(query, answer))

        return result
   
    def get_query_history_query(self, document_set: str, limit : int = 0) -> list[str]:
        """Get query histoty"""
        result = self.get_query_history(document_set, limit)
        return [q.query for q in result]
