"""
    Document set manager
"""

# pylint: disable=C0301,C0103,C0304,C0303,W0611,C0411

import os
from dataclasses import dataclass
from dataclasses_json import dataclass_json

@dataclass_json
@dataclass
class DocumentSetItem():
    """One document set item"""
    name : str

@dataclass_json
@dataclass
class DocumentSetList():
    """List of items"""
    document_set : list[DocumentSetItem]

class DocumentSetManager:
    """Source of doument set"""

    _storage  : DocumentSetList
    in_memory : bool

    __DISK_FOLDER = '.document-set'
    __FILE_NAME   = 'document-set.json'

    def __init__(self, in_memory : bool):
        self.in_memory = in_memory
        self._storage = DocumentSetList(list[DocumentSetItem]())
        if not self.in_memory:
            os.makedirs(self.__DISK_FOLDER, exist_ok=True)

    def __get_storage_file_name(self):
        """Get storage file name"""
        return os.path.join(self.__DISK_FOLDER, self.__FILE_NAME)
    
    def save(self):
        """Save storage"""
        if self.in_memory:
            return
        json_str = self._storage.to_json(indent=4)
        file_name = self.__get_storage_file_name()

        dir_name = os.path.dirname(file_name)
        os.makedirs(dir_name, exist_ok=True)

        with open(file_name,"wt", encoding="utf-8") as file:
            file.write(json_str)

    def load(self):
        """Load storage"""
        self._storage = DocumentSetList(list[DocumentSetItem]())
        if self.in_memory:
            return

        file_name = self.__get_storage_file_name()
        if os.path.isfile(file_name):
            with open(file_name,"rt", encoding="utf-8") as file:
                json_str = file.read()
            self._storage = DocumentSetList.from_json(json_str) # pylint: disable=E1101

    def get_all_names(self) -> list[str]:
        """Load storage"""
        return [d.name for d in self._storage.document_set]

    def  find_name(self, name : str) -> DocumentSetItem:
        """Find document set by name"""
        for document_set in self._storage.document_set:
            if document_set.name.lower() == name.lower():
                return document_set
        return None
    
    def add(self, name : str, auto_save : bool):
        """Add new document set"""
        name = name.strip()
        document_set = self.find_name(name)
        if document_set:
            return
        self._storage.document_set.append(DocumentSetItem(name))
        if auto_save and not self.in_memory:
            self.save()