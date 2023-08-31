"""
    LLM
"""

# pylint: disable=C0301,C0103,C0304,C0303,W0611,W0511,R0913,R0402

import os
import re
import json
from enum import Enum
from dataclasses import dataclass

import langchain
from langchain.embeddings import OpenAIEmbeddings
from langchain.embeddings import SentenceTransformerEmbeddings
from langchain import PromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain.cache import SQLiteCache
from langchain.callbacks import get_openai_callback
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain

import core.llm.prompts as prompts

class EmbeddingType(Enum):
    """Types of embeddings"""
    OPENAI = "Open AI Embeddings"
    SBERT = "SBERT (https://www.sbert.net/)"

class LlmError(Exception):
    """Lmm related exception"""

@dataclass
class LlmRelevanceScore:
    """Chunk of search result"""
    llm_score   : float
    llm_expl    : str
    used_tokens : int
    error       : str

class LlmManager():
    """LLM Manager"""

    llm_relevance : ChatOpenAI
    relevance_prompt : PromptTemplate
    relevance_chain : LLMChain

    _MODEL_NAME = "gpt-3.5-turbo" # gpt-3.5-turbo-16k

    def __init__(self):
        langchain.llm_cache = SQLiteCache()
        self.llm_relevance  = None
        self.relevance_prompt = None
        self.relevance_chain = None

    def __get_api_key(self):
        return os.environ["OPENAI_API_KEY"]

    def get_model_name(self):
        """Return model name"""
        return self._MODEL_NAME

    def get_embeddings(self, embedding_name : str):
        """Embeddings"""
        if embedding_name == EmbeddingType.OPENAI.value:
            # https://api.python.langchain.com/en/latest/embeddings/langchain.embeddings.openai.OpenAIEmbeddings.html
            return OpenAIEmbeddings(openai_api_key= self.__get_api_key())
        
        if embedding_name == EmbeddingType.SBERT.value:
            # https://www.sbert.net/
            return SentenceTransformerEmbeddings(
                model_name= 'sentence-transformers/all-MiniLM-L6-v2',
                model_kwargs={"device": "cpu"}
            )
        
        raise LlmError(f'Unsupported embedding {embedding_name}')

    def get_embedding_list(self) -> list[str]:
        """Get available embeddings"""
        return [e.value for e in EmbeddingType]
    
    def get_fixed_json(self, text : str) -> str:
        """Fix LLM json"""
        text = re.sub(r"},\s*]", "}]", text)
        open_bracket = min(text.find('['), text.find('{'))
        if open_bracket == -1:
            return text
                
        close_bracket = max(text.rfind(']'), text.rfind('}'))
        if close_bracket == -1:
            return text
        return text[open_bracket:close_bracket+1]

    def get_relevance_score(self, query : str, content : str) -> LlmRelevanceScore:
        """Get relevance score betwee query and content"""

        if not self.llm_relevance:
            self.llm_relevance = ChatOpenAI(
                    openai_api_key= self.__get_api_key(),
                    model_name  = self._MODEL_NAME,
                    temperature = 0,
                    max_tokens  = 1000
            )
            self.relevance_prompt = PromptTemplate.from_template(prompts.relevance_prompt_template)
            self.relevance_chain  = self.relevance_prompt | self.llm_relevance | StrOutputParser()

        with get_openai_callback() as llm_callback:
            relevance_result = self.relevance_chain.invoke({
                    "query" : query, 
                    "content" : content
                })
            try:
                relevance_json = json.loads(self.get_fixed_json(relevance_result))
                return LlmRelevanceScore(
                            relevance_json['score'], 
                            relevance_json['explanation'], 
                            llm_callback.total_tokens, 
                            None
                        )
            except Exception as error:
                return LlmRelevanceScore(0, None, llm_callback.total_tokens, error)