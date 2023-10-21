"""
    Html parser
"""

# pylint: disable=C0301,C0103,C0304,C0303,C0305,W0611,W0511,R0903

from core.parsers.base_parser import DocumentContentItem, DocumentParserResult, BaseParser

class HtmlParser(BaseParser):
    """Html parser class"""

    def _do_parse(self) -> DocumentParserResult:
        """Get plain text from html"""


    #from unstructured.partition.html import partition_html
    #elements = partition_html(url = new_uploaded_url)
    #plain_text_from_url = "\n\n".join([str(el).strip() for el in elements]).encode("utf-8")

        # content = list[DocumentContentItem]()

        # pdf = pypdf.PdfReader(self.file_name)
        # for page in pdf.pages:
        #     text = page.extract_text()
        #     content.append(DocumentContentItem(
        #                     self.base_file_name,
        #                     text,
        #                     page.page_number,
        #                     {}
        #                 )
        #     )
        # message = f'Converted {len(pdf.pages)} pages(s) from {self.base_file_name}'
        return DocumentParserResult('', '', None)
