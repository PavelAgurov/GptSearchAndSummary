"""
    LLM
"""

# pylint: disable=C0301,C0103,C0304,C0303,W0611,W0511,R0913,R0402

import os
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
from core.llm.llm_utils import get_llm_json, parse_llm_xml
from core.llm.refine_answer import RefineAnswerChain, RefineAnswerResult

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

@dataclass
class LlmKnowledgeTreeItem:
    """Item of knowledge tree"""
    subject     : str
    predicate   : str
    objects     : list[str]

@dataclass
class LlmKnowledgeTree:
    """LLM knowledge tree"""
    triples     : list[LlmKnowledgeTreeItem]
    token_used  : int
    error       : str

@dataclass
class LlmFormatResult:
    """LLM format result"""
    output_text : str
    token_used  : int
    error       : str

class LlmManager():
    """LLM Manager"""

    llm_answer   : ChatOpenAI
    relevance_llm : ChatOpenAI
    relevance_prompt : PromptTemplate
    relevance_chain : LLMChain
    kt_llm    : ChatOpenAI
    kt_prompt : PromptTemplate
    kt_chain  : LLMChain
    format_llm    : LLMChain
    format_prompt : PromptTemplate
    format_chain  : LLMChain

    _BASE_MODEL_NAME = "gpt-3.5-turbo" # gpt-3.5-turbo-16k
    _KT_MODEL_NAME = 'gpt-4'
    _TIKTOKEN_CACHE_DIR = ".tiktoken-cache"

    def __init__(self):
        langchain.llm_cache = SQLiteCache()

        # https://github.com/openai/tiktoken/issues/75
        os.makedirs(self._TIKTOKEN_CACHE_DIR)
        os.environ["TIKTOKEN_CACHE_DIR"] = self._TIKTOKEN_CACHE_DIR

        self.llm_answer = None
        self.relevance_llm  = None
        self.relevance_prompt = None
        self.relevance_chain = None
        self.kt_llm = None
        self.kt_prompt = None
        self.kt_chain = None
        self.format_llm = None
        self.format_prompt = None
        self.format_chain = None

    def __get_api_key(self):
        return os.environ["OPENAI_API_KEY"]

    def get_model_name(self):
        """Return model name"""
        return self._BASE_MODEL_NAME

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

    def get_relevance_score(self, query : str, content : str) -> LlmRelevanceScore:
        """Get relevance score betwee query and content"""

        if not self.relevance_llm:
            self.relevance_llm = ChatOpenAI(
                    openai_api_key= self.__get_api_key(),
                    model_name  = self._BASE_MODEL_NAME,
                    temperature = 0,
                    max_tokens  = 1000
            )
            self.relevance_prompt = PromptTemplate.from_template(prompts.relevance_prompt_template)
            self.relevance_chain  = self.relevance_prompt | self.relevance_llm | StrOutputParser()

        with get_openai_callback() as llm_callback:
            relevance_result = self.relevance_chain.invoke({
                    "query" : query, 
                    "content" : content
                })
        try:
            relevance_json = get_llm_json(relevance_result)
            return LlmRelevanceScore(
                        relevance_json['score'], 
                        relevance_json['explanation'], 
                        llm_callback.total_tokens, 
                        None
                    )
        except Exception as error: # pylint: disable=W0718
            return LlmRelevanceScore(0, None, llm_callback.total_tokens, error)
            
    def build_answer(self, question : str, chunk_list : list[str]) -> RefineAnswerResult:
        """Build LLM summary"""

        if not self.llm_answer:
            self.llm_answer = ChatOpenAI(
                    openai_api_key= self.__get_api_key(),
                    model_name  = self._BASE_MODEL_NAME,
                    temperature = 0,
                    max_tokens  = 1000
            )

        refine_chain = RefineAnswerChain(self.llm_answer)
        return refine_chain.run(question, chunk_list, False)

    def build_knowledge_tree(self, input_str : str) -> LlmKnowledgeTree:
        """Build knowledge tree"""
        if not self.kt_llm:
            self.kt_llm = ChatOpenAI(
                    openai_api_key= self.__get_api_key(),
                    model_name  = self._KT_MODEL_NAME,
                    temperature = 0,
                    max_tokens  = 1000
            )
            self.kt_prompt = PromptTemplate.from_template(prompts.knowledge_tree_prompt_template)
            self.kt_chain  = self.kt_prompt | self.kt_llm | StrOutputParser()

        with get_openai_callback() as llm_callback:
            kt_result = self.kt_chain.invoke({
                    "text" : input_str
                })
        token_used = llm_callback.total_tokens

        print(kt_result)

        try:
            kt_result_json = get_llm_json(kt_result)["triples"]
            triples = list[LlmKnowledgeTreeItem]()
            for kt_json in kt_result_json:
                objects = []
                if "Objects" in kt_json:
                    objects = [obj["object"] for obj in kt_json["Objects"]]
                if "Object" in kt_json:
                    objects = [kt_json["Object"]]
                if "object" in kt_json:
                    objects = [kt_json["object"]]

                knowledge_tree_item = LlmKnowledgeTreeItem(
                    kt_json["Subject"],
                    kt_json["Predicate"],
                    objects
                 )
                triples.append(knowledge_tree_item)

            return LlmKnowledgeTree(triples, token_used, None)
        except Exception as error: # pylint: disable=W0718
            return LlmKnowledgeTree(None,  token_used, error)

    def run_llm_format(self, input_text : str) -> LlmFormatResult:
        """Run LLM format for text"""
        if not self.format_llm:
            self.format_llm = ChatOpenAI(
                    openai_api_key= self.__get_api_key(),
                    model_name  = self._BASE_MODEL_NAME,
                    temperature = 0,
                    max_tokens  = 1000
            )
            self.format_prompt = PromptTemplate.from_template(prompts.format_prompt_template)
            self.format_chain  = self.format_prompt | self.format_llm | StrOutputParser()

        with get_openai_callback() as llm_callback:
            format_result = self.format_chain.invoke({
                    "input_text" : input_text
                })

        print(f'--->{format_result}')

        format_result_xml = parse_llm_xml(format_result, ["output_text"])
        return LlmFormatResult(format_result_xml["output_text"], llm_callback.total_tokens, None)
