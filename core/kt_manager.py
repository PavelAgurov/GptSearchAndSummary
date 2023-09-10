"""
    Knowledge Tree Manager
"""
# pylint: disable=C0301,C0103,C0304,C0303,W0611,W0511,R0913

import os
from dataclasses import dataclass
from dataclasses_json import dataclass_json

@dataclass_json
@dataclass
class KnowledgeTreeItem:
    """Knowledge tree item"""
    subject     : str
    predicate   : str
    objects     : list[str]

@dataclass_json
@dataclass
class KnowledgeTree:
    """Knowledge tree"""
    triples     : list[KnowledgeTreeItem]
    error       : str = None

class KnowledgeTreeManager:
    """Knowledge Tree Manager class"""

    in_memory : bool

    __DISK_FOLDER = '.document-kt'
    _KT_EXT = '.json'

    def __init__(self, in_memory : bool):
        self.in_memory = in_memory
        if not in_memory:
            os.makedirs(self.__DISK_FOLDER, exist_ok=True)

    def save(self, name : str, knowledge_tree : KnowledgeTree):
        """Save KnowledgeTree"""
        if self.in_memory:
            return
        kt_file_name = os.path.join(self.__DISK_FOLDER, f'{name}{self._KT_EXT}')
        kt_json_str = knowledge_tree.to_json(indent=4)  # pylint: disable=E1101
        with open(kt_file_name, "wt", encoding="utf-8") as f:
            f.write(kt_json_str)

    def get_list(self) ->list[str]:
        """Get list of saved KT"""
        return [f.rstrip(self._KT_EXT) for f in os.listdir(self.__DISK_FOLDER)]

    def load(self, name : str) -> KnowledgeTree:
        """Load KT from file"""
        if self.in_memory:
            return None
        kt_file_name = os.path.join(self.__DISK_FOLDER, f'{name}{self._KT_EXT}')
        if not os.path.isfile(kt_file_name):
            return KnowledgeTree(None, 'File not found')
        try:
            with open(kt_file_name, "rt", encoding="utf-8") as f:
                json_data = f.read()
            kt = KnowledgeTree.from_json(json_data) # pylint: disable=E1101
            return kt
        except Exception as error: # pylint: disable=W0718
            return KnowledgeTree(None, error)
