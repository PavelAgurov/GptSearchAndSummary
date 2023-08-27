"""
    Docx parser
"""

# pylint: disable=C0301,C0103,C0304,C0303,C0305,W0611,W0511,R0903

# https://github.com/python-openxml/python-docx
import docx

from core.parsers.base_parser import DocumentContentItem, DocumentParserResult, BaseParser

class DocxParser(BaseParser):
    """Docx parser class"""

    def _do_parse(self) -> DocumentParserResult:
        """Get plain text from docx"""

        content = list[DocumentContentItem]()

        doc = docx.Document(self.file_name)
        full_doc_text = []
        for paragraph in doc.paragraphs:
            full_doc_text.append(paragraph.text)

        content = DocumentContentItem(
                        self.base_file_name,
                        '\n'.join(full_doc_text),
                        1,
                        {"page_number": 1}
                    )

        message = f'Converted document from {self.base_file_name}'
        return DocumentParserResult([content], message, None)
    