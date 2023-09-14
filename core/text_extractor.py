"""
    Extract plain text from source files
"""

# pylint: disable=C0301,C0103,C0304,C0303,C0305,W0611,W0511,C0411

import os
import json
from dataclasses import dataclass
from typing import Callable

from core.parsers.base_parser import BaseParser, DocumentParserResult
from core.parsers.pdf_parser import PdfParser
from core.parsers.msg_parser import MsgParser
from core.parsers.docx_parser import DocxParser
from core.parsers.txt_parser import TxtParser
from core.parsers.unst_parser import UnstructuredParser

@dataclass
class TextExtractorParams:
    """Parameters for text extraction"""
    override_all  : bool # clean up storage before new run
    show_progress_callback : Callable[[str], None]

class TextExtractor:
    """Converted from source files into plain text"""

    __DISK_FOLDER = '.document-plain-text'
    __PLAIN_TEXT_EXT = '.txt'
    __FORMATTER_EXT = '.html'
    __META_EXT = '.json'

    __parser_map = {
        '.pdf' : PdfParser,
        '.msg' : MsgParser,
        '.docx' : DocxParser,
        '.txt' : TxtParser
    }

    def __init__(self):
        os.makedirs(self.__DISK_FOLDER, exist_ok=True)

    def __get_document_set_folder_for_plain_text(self, document_set : str):
        return os.path.join(self.__DISK_FOLDER, document_set)

    def __get_meta_file_name(self, source_file_name : str) -> str:
        """Create file name for meta info"""
        return f'{source_file_name}{self.__META_EXT}'

    def text_extraction(self, document_set : str, file_list : list[str], params : TextExtractorParams) -> list[str]:
        """Convert into plain text"""
        
        document_set_folder = self.__get_document_set_folder_for_plain_text(document_set)
        os.makedirs(document_set_folder, exist_ok=True)

        output_log = list[str]()

        if params.override_all:
            output_log.append('Clean up storage')
            params.show_progress_callback('Clean up storage')
            for f in os.listdir(document_set_folder):
                os.remove(os.path.join(document_set_folder, f))
            params.show_progress_callback('')

        for file in file_list:
            base_file_name = os.path.basename(file)
            base_file_name_lower = base_file_name.lower()
            _, base_file_extension = os.path.splitext(base_file_name_lower)

            parser_type : BaseParser = UnstructuredParser
            if base_file_extension in self.__parser_map:
                parser_type = self.__parser_map[base_file_extension]

            params.show_progress_callback(f'Parse {base_file_name}...')
            parser_instance = parser_type(file)
            parserResult : DocumentParserResult = parser_instance.parse()
            
            if parserResult.error:
                output_log.append(parserResult.error)
                continue

            for content_item in parserResult.content:
                page_file_name = f'{base_file_name}-{content_item.page_number:02d}{self.__PLAIN_TEXT_EXT}'
                page_content = content_item.page_content
                page_content = page_content.strip()

                # save content
                with open(os.path.join(document_set_folder, page_file_name), "wt", encoding="utf-8") as f:
                    f.write(page_content)
                
                # save metadata
                metadata = content_item.metadata
                if not metadata:
                    metadata = {}
                metadata["s_source"] = base_file_name
                metadata["page_number"] = content_item.page_number
                metadata["p_source"] = os.path.basename(page_file_name)

                meta_file_name = self.__get_meta_file_name(page_file_name)
                with open(os.path.join(document_set_folder, meta_file_name), "wt", encoding="utf-8") as f:
                    f.write(json.dumps(metadata))

            output_log.append(parserResult.message)

        params.show_progress_callback('')
        return output_log
    
    def get_all_source_file_names(self, document_set : str, only_names : bool = False) -> list[str]:
        """Get all available files from plain text folder"""
        document_set_folder = self.__get_document_set_folder_for_plain_text(document_set)
        if not os.path.isdir(document_set_folder):
            return []
        file_list = os.listdir(document_set_folder)
        if only_names:
            return [os.path.basename(file_name) for file_name in file_list if file_name.endswith(self.__PLAIN_TEXT_EXT)]
        return [os.path.join(document_set_folder, file_name) for file_name in file_list if file_name.endswith(self.__PLAIN_TEXT_EXT)]

    def __get_source_file_names(self, document_set : str, input_file_list : list[str], only_names : bool = False) -> list[str]:
        """Get files from plain text folder"""
        document_set_folder = self.__get_document_set_folder_for_plain_text(document_set)
        if not os.path.isdir(document_set_folder):
            return []
        file_list = []
        for input_file in input_file_list:
            if not input_file.endswith(self.__PLAIN_TEXT_EXT):
                input_file = f'{input_file}{self.__PLAIN_TEXT_EXT}'
            if only_names:
                file_list.append(os.path.basename(input_file))
            else:
                file_list.append(os.path.join(document_set_folder, input_file))
        return file_list

    def get_input_with_meta(self, document_set : str, use_formatted : bool) -> list[tuple([str, {}])]:
        """Get all available data with meta"""
        source_files = self.get_all_source_file_names(document_set, False)

        result = list[tuple([str, {}])]()
        for source_file in source_files:

            metadata_file = self.__get_meta_file_name(source_file)
            with open(metadata_file, encoding="utf-8") as f:
                metadata = json.loads(f.read())
            
            formatted_file_name = f'{source_file}{self.__FORMATTER_EXT}'
            if use_formatted and os.path.isfile(formatted_file_name):
                with open(formatted_file_name, encoding="utf-8") as f:
                    source = f.read()
            else:
                with open(source_file, encoding="utf-8") as f:
                    source = f.read()

            result.append(tuple([source, metadata]))

        return result

    def get_input_by_file_name(self, document_set : str, input_file : str) -> str:
        """Get all available data"""
        source_files = self.__get_source_file_names(document_set, [input_file], False)
        with open(source_files[0], encoding="utf-8") as f:
            source = f.read()
        return source

    def get_input_with_meta_by_files(self,  document_set : str, input_file_list : list[str]) -> list[tuple([str, {}])]:
        """Get all available data with meta by file names"""
        source_files = self.__get_source_file_names(document_set, input_file_list, False)
        print(source_files)

        result = list[tuple([str, {}])]()
        for source_file in source_files:
            print(source_file)
            metadata_file = self.__get_meta_file_name(source_file)
            with open(metadata_file, encoding="utf-8") as f:
                metadata = json.loads(f.read())
            with open(source_file, encoding="utf-8") as f:
                source = f.read()
            result.append(tuple([source, metadata]))

        return result

    def save_formatted_text(self, document_set : str, plain_text_file : str, formatted_text : str):
        """Save formatted text"""
        source_file = self.__get_source_file_names(document_set, [plain_text_file], False)[0]
        formatted_file_name = f'{source_file}{self.__FORMATTER_EXT}'
        with open(formatted_file_name, "wt", encoding="utf-8") as f:
            f.write(formatted_text)
