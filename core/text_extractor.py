"""
    Extract plain text from source files
"""

# pylint: disable=C0301,C0103,C0304,C0303,C0305,W0611,W0511,C0411

import os
import json
from dataclasses import dataclass

from core.parsers.base_parser import BaseParser, DocumentParserResult
from core.parsers.pdf_parser import PdfParser
from core.parsers.msg_parser import MsgParser
from core.parsers.docx_parser import DocxParser
from core.parsers.txt_parser import TxtParser
from core.parsers.unst_parser import UnstructuredParser

@dataclass
class TextExtractorParams:
    """Parameters for text extraction"""
    override_all : bool # clean up storage before new run

class TextExtractor:
    """Converted from source files into plain text"""

    __DISK_FOLDER = '.plain-text'
    __PLAIN_TEXT_EXT = '.txt'
    __META_EXT = '.json'

    __parser_map = {
        '.pdf' : PdfParser,
        '.msg' : MsgParser,
        '.docx' : DocxParser,
        '.txt' : TxtParser
    }

    def __init__(self):
        if not os.path.isdir(self.__DISK_FOLDER):
            os.mkdir(self.__DISK_FOLDER)

    def text_extraction(self, file_list : list[str], params : TextExtractorParams) -> list[str]:
        """Convert into plain text"""
        
        result = list[str]()

        if params.override_all:
            result.append('Clean up storage')
            for f in os.listdir(self.__DISK_FOLDER):
                os.remove(os.path.join(self.__DISK_FOLDER, f))

        for file in file_list:
            base_file_name = os.path.basename(file)
            base_file_name_lower = base_file_name.lower()
            _, base_file_extension = os.path.splitext(base_file_name_lower)

            parser_type : BaseParser = UnstructuredParser
            if base_file_extension in self.__parser_map:
                parser_type = self.__parser_map[base_file_extension]

            parser_instance = parser_type(file)
            parserResult : DocumentParserResult = parser_instance.parse()
            
            if not parserResult.error:
                for content_item in parserResult.content:
                    
                    # save content
                    page_file_name = f'{base_file_name}-{content_item.page_number}{self.__PLAIN_TEXT_EXT}'
                    with open(os.path.join(self.__DISK_FOLDER, page_file_name), "wt", encoding="utf-8") as f:
                        f.write(content_item.page_content)
                    
                    # save metadata
                    metadata = content_item.metadata
                    if not metadata:
                        metadata = {}
                    metadata["s_source"] = base_file_name
                    metadata["page_number"] = content_item.page_number
                    metadata["p_source"] = os.path.basename(page_file_name)

                    meta_file_name = f'{page_file_name}{self.__META_EXT}'
                    with open(os.path.join(self.__DISK_FOLDER, meta_file_name), "wt", encoding="utf-8") as f:
                        f.write(json.dumps(metadata))

                result.append(parserResult.message)
            else:
                result.append(parserResult.error)

        return result
    
    def get_all_source_files(self, only_names : bool = False) -> list[str]:
        """Get all available files from plain text folder"""
        file_list = os.listdir(self.__DISK_FOLDER)
        if only_names:
            return [os.path.basename(file_name) for file_name in file_list if file_name.endswith(self.__PLAIN_TEXT_EXT)]
        return [os.path.join(self.__DISK_FOLDER, file_name) for file_name in file_list if file_name.endswith(self.__PLAIN_TEXT_EXT)]

    def get_input_with_meta(self) -> list[tuple([str, {}])]:
        """Get all available data with meta"""
        source_files = self.get_all_source_files(False)

        result = list[tuple([str, {}])]()
        for source_file in source_files:

            metadata_file = f'{source_file}{self.__META_EXT}'
            with open(metadata_file, encoding="utf-8") as f:
                metadata = json.loads(f.read())
            with open(source_file, encoding="utf-8") as f:
                source = f.read()
            result.append(tuple([source, metadata]))

        return result

