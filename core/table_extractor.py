""""
    Table extractor
"""
# pylint: disable=C0301,C0103,C0304,C0303,W0611

from dataclasses import dataclass
import pandas as pd
from dataclasses_json import dataclass_json

@dataclass_json
@dataclass
class TableExtractorItem:
    """One table"""
    table_name : str
    table_data : pd.DataFrame

@dataclass_json
@dataclass
class TableExtractorResult:
    """List of tables as result of extraction"""
    table_list : list[TableExtractorItem]
    error      : str

class TableExtractor:
    """Table extractor class"""

    def get_table_from_html(self, html_text : str) -> TableExtractorResult:
        """Extract table from html"""
        if ('<table ' not in html_text) and ('<table>' not in html_text):
            return None
        return TableExtractorResult([TableExtractorItem(html_text[0:50], pd.DataFrame(['1','2', '3']))], None)
    
    def get_table_extractor_result_json(self, result : TableExtractorResult) -> str:
        """Convert TableExtractorResult into json"""
        return result.to_json(indent=4) # pylint: disable=E1101