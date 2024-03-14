"""
    Parser based on UnstructuredFileLoader
"""

# pylint: disable=C0301,C0103,C0304,C0303,C0305,W0611,W0511,R0903

from langchain_community.document_loaders import UnstructuredFileLoader

from core.parsers.base_parser import DocumentContentItem, DocumentParserResult, BaseParser, DocumentParserParams

class UnstructuredParser(BaseParser):
    """Parser based on UnstructuredFileLoader"""

    def _do_parse(self, params : DocumentParserParams) -> DocumentParserResult:
        """Get plain text from pdf"""

        loader = UnstructuredFileLoader(self.file_name, mode= "single")
        content = [DocumentContentItem(
                            self.base_file_name,
                            d.page_content,
                            1,
                            d.metadata
                    ) 
                    for d in loader.load()]
        message =  f'Converted {len(content)} document(s) from {self.base_file_name}'
        return DocumentParserResult(content, message, None)
