""""
    Table extractor
"""
# pylint: disable=C0301,C0103,C0304,C0303,W0611,C0411

import re
from dataclasses import field, dataclass
import pandas as pd
from dataclasses_json import config, dataclass_json

@dataclass_json
@dataclass
class TableExtractorItem:
    """One table"""
    table_name : str
    table_data : pd.DataFrame = field(metadata=config(decoder=pd.DataFrame.from_records, encoder=lambda x: x.to_dict(orient="records")))

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

        # Find all table title and table content
        matches = re.findall(r'<table[\s]*[title=]*([^>]*)>(.*?)</table>', html_text, re.DOTALL)
        if not matches or len(matches) == 0:
            return None

        tables = list[TableExtractorItem]()
        for match in matches:
            table_name = ''
            if match[0]:
                table_name = str(match[0]).strip('"').strip()

            table_data_str = f'<table>{match[1]}</table>'
            table_data_list = pd.read_html(table_data_str)

            for table_data in table_data_list:
                tables.append(TableExtractorItem(table_name, table_data))

        return TableExtractorResult(tables, None)
    
    def get_table_extractor_result_json(self, result : TableExtractorResult) -> str:
        """Convert TableExtractorResult into json"""
        return result.to_json(indent=4) # pylint: disable=E1101