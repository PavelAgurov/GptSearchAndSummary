"""
    Utils
"""
# pylint: disable=C0301,C0103,C0304,C0303,W0611,C0411,R0903

import os

class DocHelper():
    """Doc utilites"""

    __DOC_FOLDER = 'docs'

    @classmethod
    def get_md(cls, doc_name : str) -> str:
        """Get doc file"""
        with open(os.path.join(cls.__DOC_FOLDER, f'{doc_name}.md'), encoding="utf-8") as f:
            return f.read()
