"""
    Txt parser
"""

# pylint: disable=C0301,C0103,C0304,C0303,C0305,W0611,W0511,R0903

from core.parsers.base_parser import DocumentContentItem, DocumentParserResult, BaseParser, DocumentParserParams

class TxtParser(BaseParser):
    """Txt parser class"""

    def _do_parse(self, params : DocumentParserParams) -> DocumentParserResult:
        """Get plain text from txt"""

        try:
            with open(self.file_name, encoding="utf-8") as f:
                page_content = f.read()
        except UnicodeDecodeError:
            with open(self.file_name, encoding="cp1251") as f:
                page_content = f.read()

        content = DocumentContentItem(
                            self.base_file_name,
                            page_content,
                            1,
                            {}
                        )
        message = f'Copied plain text document from {self.base_file_name}'
        return DocumentParserResult([content], message, None)
    