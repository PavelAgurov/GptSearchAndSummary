"""
    Source file storage
"""

import os
from typing import Any

class SourceStorage:
    """Source storage class"""

    in_memory : bool
    __DISK_FOLDER = '.document-source'

    def __init__(self, in_memory : bool):
        self.in_memory = in_memory
        if not self.in_memory:
            os.makedirs(self.__DISK_FOLDER, exist_ok=True)

    def __get_storage_folder(self, document_set : str):
        storage_folder = os.path.join(self.__DISK_FOLDER, document_set)
        if not self.in_memory:
            os.makedirs(storage_folder, exist_ok=True)
        return storage_folder
    
    def __get_file_name(self, document_set : str, file_name : str):
        return os.path.join(self.__get_storage_folder(document_set), file_name)

    def save_file(self, document_set: str, file_name : str, buffer : Any):
        """Save file from buffer into file_name on disk"""
        with open(self.__get_file_name(document_set, file_name),"wb") as file:
            file.write(buffer)

    def get_all_files(self, document_set: str, only_names : bool = False) -> list[str]:
        """Get all available files"""
        storage_folder = self.__get_storage_folder(document_set)
        file_list = os.listdir(storage_folder)
        if only_names:
            return [os.path.basename(file_name) for file_name in file_list]
        return [os.path.join(storage_folder, file_name) for file_name in file_list]
        
    def delete_file(self, document_set : str, file_name : str):
        """Remove file from source folder"""
        os.remove(self.__get_file_name(document_set, file_name))