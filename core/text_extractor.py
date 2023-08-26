"""
    Extract plain text from source files
"""

# pylint: disable=C0301,C0103,C0304,C0303,C0305,W0611,W0511

import os
from dataclasses import dataclass

#TODO: to suppot PPT by UnstructuredFileLoader we need to install libreoffice
#TODO: to check if UnstructuredFileLoader use external API and send information to their API
#TODO: save additional meta-information
#TODO: process e-mails

from langchain.document_loaders import UnstructuredFileLoader
import pypdf
import docx

@dataclass
class TextExtractorParams:
    """Parameters for text extraction"""
    override_all : bool # clean up storage before new run

@dataclass
class DocumentContentItem:
    """Content item of the document"""
    file_name    : str
    page_content : str
    page_number  : int
    metadata     : dict

class TextExtractor:
    """Converted from source files into plain text"""

    __DISK_FOLDER = '.plain-text'

    def __init__(self):
        if not os.path.isdir(self.__DISK_FOLDER):
            os.mkdir(self.__DISK_FOLDER)

    def text_extraction(self, file_list : list[str], params : TextExtractorParams) -> list[str]:
        """Convert into plain text"""
        
        result = list[str]()

        if params.override_all:
            result.append('Clean up storage')
            for f in os.listdir(self.__DISK_FOLDER):
                os.remove(os.path.join(self.__DISK_FOLDER, f))

        for file in file_list:
            base_file_name = os.path.basename(file)
            base_file_name_lower = base_file_name.lower()
            document_content_list = list[DocumentContentItem]()

            if base_file_name_lower.endswith('.pdf'):
                pdf = pypdf.PdfReader(file)
                for page in pdf.pages:
                    text = page.extract_text()
                    document_content_list.append(DocumentContentItem(
                                    base_file_name,
                                    text,
                                    page.page_number,
                                    {"page_number": page.page_number}
                                )
                    )
                result.append(f'Converted {len(pdf.pages)} pages(s) from {base_file_name}')
            elif base_file_name_lower.endswith('.docx'):
                # docx format has no information about page number
                # we can only save paragraphs index
                doc = docx.Document(file)
                full_doc_text = []
                for paragraph in doc.paragraphs:
                    full_doc_text.append(paragraph.text)
                document_content_list.append(DocumentContentItem(
                                base_file_name,
                                '\n'.join(full_doc_text),
                                1,
                                {"page_number": 1}
                            )
                )
                result.append(f'Converted document from {base_file_name}')
            elif base_file_name_lower.endswith('.txt'):
                # txt is plain text, it's not needed to convert it
                with open(file, encoding="utf-8") as f:
                    page_content = f.read()
                document_content_list.append(DocumentContentItem(
                                    base_file_name,
                                    page_content,
                                    1,
                                    {}
                                )
                )
                result.append(f'Copied plain text document from {base_file_name}')
            else:
                loader = UnstructuredFileLoader(file, mode= "single")
                document_content_list.extend([DocumentContentItem(
                                    base_file_name,
                                    d.page_content,
                                    1,
                                    d.metadata
                                ) for d in loader.load()]
                )
                result.append(f'Converted {len(document_content_list)} document(s) from {base_file_name}')
            
            for content_item in document_content_list:
                page_file_name = f'{base_file_name}-{content_item.page_number}.txt'
                with open(os.path.join(self.__DISK_FOLDER, page_file_name), "wt", encoding="utf-8") as f:
                    f.write(content_item.page_content)

        return result
    
    def get_all_files(self, only_names : bool = False) -> list[str]:
        """Get all available files from plain text folder"""
        file_list = os.listdir(self.__DISK_FOLDER)
        if only_names:
            return [os.path.basename(file_name) for file_name in file_list]
        return [os.path.join(self.__DISK_FOLDER, file_name) for file_name in file_list]

    