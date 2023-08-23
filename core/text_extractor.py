"""
    Extract plain text from source files
"""

# pylint: disable=C0301,C0103,C0304,C0303,W0611

import os

from langchain.document_loaders import UnstructuredFileLoader

class TextExtractor:
    """Converted from source files into plain text"""

    __DISK_FOLDER = '.plain-text'

    def __init__(self):
        if not os.path.isdir(self.__DISK_FOLDER):
            os.mkdir(self.__DISK_FOLDER)

    def text_extraction(self, file_list : list[str], override_all : bool) -> list[str]:
        """Convert into plain text"""
        
        result = list[str]()

        if override_all:
            result.append('Clean up storage')
            for f in os.listdir(self.__DISK_FOLDER):
                os.remove(os.path.join(self.__DISK_FOLDER, f))

        for file in file_list:
            loader = UnstructuredFileLoader(file)
            documents = loader.load()
            result.append(f'Converted {len(documents)} document(s) from {os.path.basename(file)}')
            
            base_file_name = os.path.basename(file)

            for index, doc in enumerate(documents):
                with open(os.path.join(self.__DISK_FOLDER, f'{base_file_name}-{index}.txt'), "wt", encoding="utf-8") as f:
                    f.write(doc.page_content)

        return result
    
    def get_all_files(self, only_names : bool = False) -> list[str]:
        """Get all available files from plain text folder"""
        file_list = os.listdir(self.__DISK_FOLDER)
        if only_names:
            return [os.path.basename(file_name) for file_name in file_list]
        return [os.path.join(self.__DISK_FOLDER, file_name) for file_name in file_list]
