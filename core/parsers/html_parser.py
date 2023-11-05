"""
    Html parser
"""

# pylint: disable=C0301,C0103,C0304,C0303,C0305,W0611,W0511,R0903,C0411

import re
from bs4 import BeautifulSoup, Tag, Comment, Doctype
from dataclasses import dataclass

from core.parsers.base_parser import DocumentContentItem, DocumentParserResult, BaseParser, DocumentParserParams

@dataclass
class HtmlItem:
    """Html item"""
    header_index : int
    header_text  : str

class HtmlHeaderStack:
    """Stack for headers"""
    header_stack : list[HtmlItem]

    def __init__(self):
        self.header_stack = list[HtmlItem]()

    def append_header(self, tag_name : str, header : str):
        """Append header into stack"""
        header_index = int(tag_name.removeprefix('h'))
        while self.header_stack and self.header_stack[-1].header_index >= header_index:
            self.header_stack.pop()
        self.header_stack.append(HtmlItem(header_index, header))

    def get_full_header(self)-> str:
        """Get current header"""
        return ' '.join([h.header_text+'.' for h in self.header_stack])

def is_excluded_id_or_class(tag : Tag, excluded_names : list[str]):
    """True if tag should be excluded"""

    for excluded_name in excluded_names:
        if excluded_name in tag.name:
            return True
        
    if tag.has_attr('id'):
        tag_id = tag['id']
        for excluded_name in excluded_names:
            if excluded_name in tag_id:
                return True
            
    if tag.has_attr('class'):
        tag_classes = tag['class']
        for excluded_name in excluded_names:
            for tag_class in tag_classes: 
                if excluded_name in tag_class:
                    return True
    return False

class HtmlParser(BaseParser):
    """Html parser class"""

    def _do_parse(self, params : DocumentParserParams) -> DocumentParserResult:
        """Get plain text from html"""

        try:
            with open(self.file_name, encoding="utf-8") as f:
                page_content = f.read()
        except UnicodeDecodeError:
            with open(self.file_name, encoding="cp1251") as f:
                page_content = f.read()

        content_soup = self.__get_content_soup(
                            page_content, 
                            params.html_params.excluded_names,
                            params.html_params.tag_to_remove
                        )
            
        if not params.html_params.combine_html_headers:
            content = content_soup.get_text()
            message = f'Extract plain text from {self.base_file_name}'
            return DocumentParserResult([DocumentContentItem(self.base_file_name, content, 1, {})], message, None)

        content = self.__extract_content(content_soup, 0, HtmlHeaderStack())
        pattern = r'<HEADER>(.*?)<\/HEADER>\s*(.*?)(?=<HEADER>|$)'
        matches = re.findall(pattern, content, re.DOTALL)

        result_content = list[DocumentContentItem]()
        for index, header_match in enumerate(matches):
            text = f'{header_match[0]}\n\n{header_match[1]}'
            result_content.append(DocumentContentItem(
                            self.base_file_name,
                            text,
                            index+1,
                            {}
                        )
            )

        message = f'Extract plain text from {self.base_file_name}: {len(result_content)} part(s).'
        return DocumentParserResult(result_content, message, None)

    def __get_content_soup(self, html_text : str, excluded_names : list[str], tag_to_remove : list[str]) -> BeautifulSoup:
        """Get content"""
        soup = BeautifulSoup(html_text, 'html.parser')

        # Find the tags to exclude by their id
        def exclude_lambda(tag : Tag):
            return is_excluded_id_or_class(tag, excluded_names)

        exclude_tags = soup.find_all(exclude_lambda)
        # Remove the exclude_tags and their descendants
        for tag in exclude_tags:
            tag.decompose()

        # Remove 'head'
        exclude_tags = soup.find_all(tag_to_remove)
        for tag in exclude_tags:
            tag.decompose()

        return soup

    def __extract_content(self, tag : Tag, ul_count : int, h_stack : HtmlHeaderStack) -> str:
        """Extract content recurs."""

        if tag.name in ['h1', 'h2', 'h3', 'h4']:
            h_stack.append_header(tag.name, str(tag.text))
            return f'\n\n<HEADER>{h_stack.get_full_header()}</HEADER>\n\n'

        result = ''
        for item in tag.contents:
            if item.name == 'br':
                result += '\n'
            elif item.name == 'strong':
                result += str(item.text) + ' '
            elif item.name == 'li':
                content = self.__extract_content(item, ul_count+1, h_stack)
                if content.strip():
                    li_prefix = '\n' + '-'*(ul_count+1) + ' '
                    result += li_prefix + content
            elif item.name is None:
                if isinstance(item, (Doctype, Comment)):
                    continue
                text = item.strip()
                if text:
                    result += text + ' '
            elif item.name:
                content = self.__extract_content(item, ul_count, h_stack)
                if content:
                    result += content
        return result

    
    