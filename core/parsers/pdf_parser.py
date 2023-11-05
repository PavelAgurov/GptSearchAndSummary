"""
    Pdf parser
"""

# pylint: disable=C0301,C0103,C0304,C0303,C0305,W0611,W0511,R0903

import pypdf

from core.parsers.base_parser import DocumentContentItem, DocumentParserResult, BaseParser, DocumentParserParams

class PdfParser(BaseParser):
    """Pdf parser class"""

    def _do_parse(self, params : DocumentParserParams) -> DocumentParserResult:
        """Get plain text from pdf"""

        content = list[DocumentContentItem]()

        pdf = pypdf.PdfReader(self.file_name)
        for page in pdf.pages:
            text = page.extract_text()
            content.append(DocumentContentItem(
                            self.base_file_name,
                            text,
                            page.page_number,
                            {}
                        )
            )
        message = f'Converted {len(pdf.pages)} pages(s) from {self.base_file_name}'
        return DocumentParserResult(content, message, None)
