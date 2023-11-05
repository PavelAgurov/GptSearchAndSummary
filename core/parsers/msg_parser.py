"""
    Msg (e-mail) parser
"""

# pylint: disable=C0301,C0103,C0304,C0303,C0305,W0611,W0511,R0903

# https://github.com/TeamMsgExtractor/msg-extractor/tree/master
import extract_msg 

from core.parsers.base_parser import DocumentContentItem, DocumentParserResult, BaseParser, DocumentParserParams

class MsgParser(BaseParser):
    """Msg parser class"""

    def _do_parse(self, params : DocumentParserParams) -> DocumentParserResult:
        """Get plain text from e-mail"""

        msg = extract_msg.openMsg(self.file_name)
        content = DocumentContentItem(
                        self.base_file_name,
                        msg.body,
                        1,
                        {"to": msg.to, "cc": msg.cc, "from" : msg.sender}
                    )
        message = f'Converted e-mail from {self.base_file_name}'
        return DocumentParserResult([content], message, None)
