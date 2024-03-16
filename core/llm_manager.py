"""
    LLM
"""

# pylint: disable=C0301,C0103,C0304,C0303,W0611,W0511,R0913,R0402,W1203

import os
from dataclasses import dataclass
import logging

from langchain.prompts.prompt import PromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain.globals import set_llm_cache
from langchain.cache import SQLiteCache
from langchain_community.callbacks import get_openai_callback
from langchain_openai import ChatOpenAI, AzureChatOpenAI
from langchain.chains import LLMChain
from langchain.text_splitter import TokenTextSplitter

import core.llm.prompts as prompts
from core.llm.llm_json_parser import get_llm_json
from core.llm.llm_xml_parser import parse_llm_xml
from core.llm.refine_answer import RefineAnswerChain, RefineAnswerResult

logger : logging.Logger = logging.getLogger()

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

@dataclass
class LlmFactsResult:
    """LLM facts result"""
    fact_list     : list[str]
    token_used    : int
    error_list    : list[str]

@dataclass
class LlmTableResult:
    """LLM table result"""
    output_str  : str
    token_used  : int
    error       : str

class LlmManager():
    """LLM Manager"""

    openai_api_type : str
    openai_api_deployment : str

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
    facts_llm    : LLMChain
    facts_prompt : PromptTemplate
    facts_chain  : LLMChain

    _BASE_MODEL_NAME = "gpt-3.5-turbo" # gpt-3.5-turbo-16k
    _KT_MODEL_NAME = 'gpt-4'
    _TIKTOKEN_CACHE_DIR = ".tiktoken-cache"

    def __init__(self, all_secrets : dict[str, any]):
        # Init cache
        set_llm_cache(SQLiteCache(database_path=".langchain.db"))

        # https://github.com/openai/tiktoken/issues/75
        os.makedirs(self._TIKTOKEN_CACHE_DIR, exist_ok=True)
        os.environ["TIKTOKEN_CACHE_DIR"] = self._TIKTOKEN_CACHE_DIR

        self.init_openai_environment(all_secrets)

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
        self.facts_llm    = None
        self.facts_prompt = None
        self.facts_chain  = None

    def init_openai_environment(self, all_secrets : dict[str, any]):
        """Inint OpenAI or Azure environment"""

        self.openai_api_type = 'openai'
        self.openai_api_deployment = None
        if not all_secrets:
            return
 
        # read from secrets
        self.openai_api_type = all_secrets.get('OPENAI_API_TYPE')

        if self.openai_api_type == 'openai':
            openai_secrets = all_secrets.get('open_api_openai')
            if openai_secrets:
                os.environ["OPENAI_API_KEY"] = openai_secrets.get('OPENAI_API_KEY')
                base_model_name = openai_secrets.get('OPENAI_BASE_MODEL_NAME')
                if base_model_name:
                    self._BASE_MODEL_NAME = base_model_name
                logger.info(f'Run with OpenAI from config file [{len(os.environ["OPENAI_API_KEY"])}]')
                logger.info(f'Base model {self._BASE_MODEL_NAME}')
            else:
                logger.error('open_api_openai section is required')
            return
        
        if self.openai_api_type == 'azure':
            azure_secrets = all_secrets.get('open_api_azure')
            if azure_secrets:
                os.environ["OPENAI_API_KEY"] = azure_secrets.get('OPENAI_API_KEY')
                os.environ["OPENAI_API_TYPE"] = "azure"
                os.environ["OPENAI_API_VERSION"] = azure_secrets.get('OPENAI_API_VERSION')
                os.environ["OPENAI_API_BASE"] = azure_secrets.get('OPENAI_API_BASE')
                self.openai_api_deployment = azure_secrets.get('OPENAI_API_DEPLOYMENT')
                base_model_name = azure_secrets.get('OPENAI_BASE_MODEL_NAME')
                if base_model_name:
                    self._BASE_MODEL_NAME = base_model_name
                logger.info('Run with Azure OpenAI config file')
                logger.info(f'Base model {self._BASE_MODEL_NAME}')
            else:
                logger.error('open_api_azure section is required')
            return
        
        logger.error(f'unsupported OPENAI_API_TYPE: {self.openai_api_type}')

    def get_model_name(self):
        """Return model name"""
        return self._BASE_MODEL_NAME
    
    def create_llm(self, max_tokens : int, model_name : str = "") -> ChatOpenAI:
        """Create LLM"""
        if not model_name:
            model_name = self._BASE_MODEL_NAME

        if self.openai_api_type == 'openai':
            return ChatOpenAI(
                model_name     = model_name,
                max_tokens     = max_tokens,
                temperature    = 0,
                verbose        = False,
                model_kwargs={
                    "frequency_penalty": 0.0,
                    "presence_penalty" : 0.0,
                    "top_p" : 1.0
                }        
            )
        
        if self.openai_api_type == 'azure':
            return AzureChatOpenAI(
                model_name     = model_name,
                max_tokens     = max_tokens,
                temperature    = 0,
                verbose        = False,
                deployment_name=  self.openai_api_deployment,
                model_kwargs={
                    "frequency_penalty": 0.0,
                    "presence_penalty" : 0.0,
                    "top_p" : 1.0
                }        
            )
        
        logger.error(f'unsupported OPENAI_API_TYPE: {self.openai_api_type}')
        return None

    def get_relevance_score(self, query : str, content : str) -> LlmRelevanceScore:
        """Get relevance score betwee query and content"""

        if not self.relevance_llm:
            self.relevance_llm = self.create_llm(max_tokens= 1000)
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
            logger.error(error)
            return LlmRelevanceScore(0, None, llm_callback.total_tokens, error)
            
    def build_answer(self, question : str, chunk_list : list[str]) -> RefineAnswerResult:
        """Build LLM summary"""

        if not self.llm_answer:
            self.llm_answer = self.create_llm(max_tokens= 1000)
        refine_chain = RefineAnswerChain(self.llm_answer)
        return refine_chain.run(question, chunk_list)

    def build_knowledge_tree(self, input_str : str) -> LlmKnowledgeTree:
        """Build knowledge tree"""
        
        logger.info("Build KT")

        if not self.kt_llm:
            self.kt_llm = self.create_llm(max_tokens= 1000, model_name= self._KT_MODEL_NAME)
            self.kt_prompt = PromptTemplate.from_template(prompts.knowledge_tree_prompt_template)
            self.kt_chain  = self.kt_prompt | self.kt_llm | StrOutputParser()

        with get_openai_callback() as llm_callback:
            kt_result = self.kt_chain.invoke({
                    "text" : input_str
                })
        token_used = llm_callback.total_tokens

        logger.debug(kt_result)

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
            logger.error(error)
            return LlmKnowledgeTree(None,  token_used, error)

    def run_llm_format(self, input_text : str) -> LlmFormatResult:
        """Run LLM format for text"""
        if not self.format_llm:
            self.format_llm    = self.create_llm(max_tokens= 1000)
            self.format_prompt = PromptTemplate.from_template(prompts.format_prompt_template)
            self.format_chain  = self.format_prompt | self.format_llm | StrOutputParser()

        with get_openai_callback() as llm_callback:
            format_result = self.format_chain.invoke({
                    "input_text" : input_text
                })

        logger.debug(f'FORMATTED: {format_result}')

        format_result_xml = parse_llm_xml(format_result, ["output_text"])
        return LlmFormatResult(format_result_xml["output_text"], llm_callback.total_tokens, None)

    def get_fact_list(self, input_text : str, context : str) -> LlmFactsResult:
        """Run LLM fact extractor"""
        max_tokens = 1500

        if not self.facts_llm:
            self.facts_llm = self.create_llm(max_tokens= max_tokens)
            self.facts_prompt = PromptTemplate.from_template(prompts.extract_facts_prompt_template)
            self.facts_chain  = self.facts_prompt | self.facts_llm | StrOutputParser()

        text_splitter = TokenTextSplitter(chunk_size=max_tokens-100, chunk_overlap=20)
        texts = text_splitter.split_text(input_text)

        fact_list  = []
        error_list = []
        total_tokens = 0
        for chunk_text in texts:
            facts_result = ''
            try:
                with get_openai_callback() as llm_callback:
                    facts_result = self.facts_chain.invoke({
                            "input_text" : chunk_text,
                            "context"    : context
                        })
                total_tokens += llm_callback.total_tokens
            except Exception as error_llm: # pylint: disable=W0718
                error_list.append(str(error_llm))
                logger.error(error_llm)
                continue

            logger.debug(f'FACTS: {facts_result}')

            try:
                facts_result_json = get_llm_json(facts_result)

                for f in facts_result_json['relevant_facts']:
                    fact_str = str(f["fact"])
                    score = f["score"]
                    if score == 0:
                        continue
                    fact_str = fact_str.replace('\n\n', '\n')
                    fact_list.append(fact_str)

            except Exception as error_json: # pylint: disable=W0718
                error_list.append(str(error_json))
                logger.error(error_json)

        return LlmFactsResult(fact_list, total_tokens, error_list)

