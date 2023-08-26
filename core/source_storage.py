"""
    Source file storage
"""

import os
from typing import Any

class SourceStorage:
    """Source storage class"""

    __DISK_FOLDER = '.data'

    def __init__(self):
        if not os.path.isdir(self.__DISK_FOLDER):
            os.mkdir(self.__DISK_FOLDER)

    def save_file(self, file_name : str, buffer : Any):
        """Save file from buffer into file_name on disk"""
        with open(os.path.join(self.__DISK_FOLDER, file_name),"wb") as file:
            file.write(buffer)

    def get_all_files(self, only_names : bool = False) -> list[str]:
        """Get all available files"""
        file_list = os.listdir(self.__DISK_FOLDER)
        if only_names:
            return [os.path.basename(file_name) for file_name in file_list]
        return [os.path.join(self.__DISK_FOLDER, file_name) for file_name in file_list]
        
    def delete_file(self, file_name : str):
        """Remove file from source folder"""
        os.remove(os.path.join(self.__DISK_FOLDER, file_name))