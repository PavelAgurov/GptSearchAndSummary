"""
    Base classes for parsers (text extractors)
"""

# pylint: disable=C0301,C0103,C0304,C0303,C0305,W0611,W0511,R0903

from abc import abstractmethod
import os
from dataclasses import dataclass

@dataclass
class DocumentParserParams:
    """Parser parameters"""
    set_chunk_headers : bool # set h1/h2/h3 headers for each chunk

@dataclass
class DocumentContentItem:
    """Content item of the document"""
    file_name    : str
    page_content : str
    page_number  : int
    metadata     : dict

@dataclass
class DocumentParserResult:
    """Result of parsing"""
    content : list[DocumentContentItem]
    message : str
    error   : str

class BaseParser():
    """Base parser class"""

    file_name : str
    base_file_name : str

    def __init__(self, file_name : str):
        self.file_name = file_name
        self.base_file_name = os.path.basename(self.file_name)

    def parse(self) -> DocumentParserResult:
        """Get plain text from file"""
        try:
            return self._do_parse()
        except Exception as error: # pylint: disable=W0718
            error_message = f'ERROR: file {self.file_name}. Exception: {error} [{type(error)}]'
            return DocumentParserResult(None, None, error_message)
        
    @abstractmethod
    def _do_parse(self) -> DocumentParserResult:
        """Get plain text from file"""