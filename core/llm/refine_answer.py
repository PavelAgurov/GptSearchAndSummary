"""
    Refine answer
"""
# pylint: disable=C0301,C0103,C0304,C0303,W0611,W0511,R0913,R0402,W1203

import logging
import traceback
from dataclasses import dataclass
from pydantic import BaseModel, Field

from langchain.callbacks import get_openai_callback
from langchain.utils.openai_functions import convert_pydantic_to_openai_function
from langchain.prompts import ChatPromptTemplate
from langchain.prompts.prompt import PromptTemplate
from langchain.chains import LLMChain

from core.llm.json_parser import JsonFixOutputFunctionsParser, JsonFixLLMOutputParser

logger : logging.Logger = logging.getLogger()

NO_ANSWER_STR = 'There is no answer in the information provided'

class ExtractedAnswer(BaseModel):
    """Extracted answer if there is answer in text provided text."""
    answer  : str   = Field(description="Direct answer to the provided question")
    score   : float = Field(description="Score of relevance between question and answer")

extract_answer_system_prompt = """\
Find the answer to the question from the provided text. DO NOT MAKE UP ANSWER, use only provided information. 
If there is no answer in the provided text - do not guess.
"""

extract_answer_params = "<question>{question}</question><input_text>{input_text}</input_text>"

answer_combine_prompt_template = """\
Your job is to produce a final answer. We have provided an existing answer up to a certain point (delimited with XML tags).
We have the opportunity to refine the existing answer (only if needed) with some more context (delimited with XML tags).
Given the new context, refine the original answer (only if new context is useful) otherwise say that it's not useful.
Please provide result in JSON format:
{{
    "not_useful": "True if new context was not useful, False if new content was used",
    "refined_answer": "refined answer here if new context was useful"
}}

<question>
{question}
</question>

<existing_answer>
{existing_answer}
</existing_answer>

<more_context>
{more_context}
</more_context>
"""


@dataclass
class RefineAnswerResult():
    """Result of refine"""
    answer      : str
    tokens_used : int
    error       : bool

class RefineAnswerChain():
    """Refine chain"""
    
    openai_api_type : str

    def __init__(self, llm, openai_api_type : str):
        self.openai_api_type = openai_api_type
        extraction_functions = [convert_pydantic_to_openai_function(ExtractedAnswer)]

        if self.openai_api_type == 'openai':
            extraction_model = llm.bind(functions=extraction_functions, function_call="auto")
            prompt = ChatPromptTemplate.from_messages([
                ("system", extract_answer_system_prompt),
                ("human" , extract_answer_params)
            ])
            self.extraction_chain = prompt | extraction_model | JsonFixOutputFunctionsParser()

        if self.openai_api_type == 'azure':
            extract_answer_system_prompt_old_style = extract_answer_system_prompt + \
                "\nPlease provide result based on JSON schema:\n" + \
                str(extraction_functions).replace('{', '{{').replace('}', '}}').replace("'", "\"") + \
                extract_answer_params
            prompt = PromptTemplate(template= extract_answer_system_prompt_old_style, input_variables=["question", "input_text"])
            self.extraction_chain  = LLMChain(llm= llm, prompt= prompt, output_parser = JsonFixLLMOutputParser(function_name = 'ExtractedAnswer'))

        # refine_initial_prompt = PromptTemplate(template= answer_initial_prompt_template, input_variables=["question", "input_text"])
        # self.refine_initial_chain = LLMChain(llm= llm, prompt= refine_initial_prompt)
        # refine_combine_prompt = PromptTemplate(template= answer_combine_prompt_template, input_variables=["question", "existing_answer", "more_context"])
        # self.refine_combine_chain = LLMChain(llm= llm, prompt= refine_combine_prompt)

    def run(self, question : str, docs : list) -> RefineAnswerResult:
        """Run refine"""
        tokens_used = 0

        logger.info(f"Run answer extraction question: [{question}]")
        try:
            logger.debug('Process doc #1')
            with get_openai_callback() as cb:
                if self.openai_api_type == 'openai':
                    answer_result = self.extraction_chain.invoke({"question": question, "input_text" : docs[0]})
                if self.openai_api_type == 'azure':
                    answer_result = self.extraction_chain.run(question = question, input_text = docs[0])
            tokens_used += cb.total_tokens

            logger.debug(answer_result)

            if answer_result is None:
                return RefineAnswerResult(NO_ANSWER_STR, tokens_used, False)

            if isinstance(answer_result, str):
                return RefineAnswerResult(answer_result, tokens_used, False)

            extracted_answer = ExtractedAnswer(**answer_result)
            logger.info(f'extracted_answer={extracted_answer.answer} [{extracted_answer.score}]')

            answer = extracted_answer.answer
            if not answer:
                answer = NO_ANSWER_STR

            # for index, doc in enumerate(docs[1:]):
            #     steps = self.log(steps, enable_logger, f'Process doc #{index+2}')
            #     with get_openai_callback() as cb:
            #         refine_result = self.refine_combine_chain.run(question = question, existing_answer = answer, more_context = doc)
            #     tokens_used += cb.total_tokens
            #     steps = self.log(steps, enable_logger, refine_result)
            #     refined_json = json.loads(get_fixed_json(refine_result))
            #     refined_useful = not refined_json["not_useful"]
            #     if refined_useful:
            #         answer = refined_json["refined_answer"]
            
            return RefineAnswerResult(answer, tokens_used, False)
        except Exception as error: # pylint: disable=W0718
            logger.exception(error)
            logger.error(traceback.format_exc())
            return RefineAnswerResult("", tokens_used, True)
