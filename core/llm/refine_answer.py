"""
    Refine answer
"""
# pylint: disable=C0301,C0103,C0304,C0303,W0611,W0511,R0913,R0402,W1203

import logging
import traceback
from dataclasses import dataclass

from langchain.callbacks import get_openai_callback
from langchain.prompts.prompt import PromptTemplate
from langchain.chains import LLMChain

from core.llm.llm_json_parser import get_llm_json

logger : logging.Logger = logging.getLogger()

NO_ANSWER_STR = "No answer"

refine_initial_prompt_template = """\
You are a professor of linguistics working in University. 
First you should read provided input text and create useful summary.
After it write an answer (full or partial) to the question based on created summary.
If summary has no answer to the question - say {no_answer}.

<input_text>
{input_text}
</input_text>

<question>
{question}
</question>

Please provide result in JSON format:
{{
    "score" : score how your answer is relevant to the question,
    "answer": "answer to the question here"
}}
"""


refine_combine_prompt_template = """\
You are a professor of linguistics.
Try to expand existed answer to the provided question with more context.
Given the new context, refine the original answer (only if new context is useful) otherwise say that it's not useful.

Please provide result in JSON format:
{{
    "not_useful": "True if new context was not useful, False if new content was used",
    "refined_answer": "refined answer here if new context was useful"
}}

<question>
{question}
</question>

<existed_answer>
{existed_answer}
</existed_answer>

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
    
    def __init__(self, llm):
        refine_initial_prompt = PromptTemplate(template= refine_initial_prompt_template, input_variables=["question", "input_text", "no_answer"])
        self.refine_initial_chain = LLMChain(llm= llm, prompt= refine_initial_prompt)
        refine_combine_prompt = PromptTemplate(template= refine_combine_prompt_template, input_variables=["question", "existing_answer", "more_context"])
        self.refine_combine_chain = LLMChain(llm= llm, prompt= refine_combine_prompt)

    def run(self, question : str, docs : list[str]) -> RefineAnswerResult:
        """Run refine"""
        tokens_used = 0

        logger.info(f"Run answer extraction question: [{question}]")
        try:
            # find first userful document with answers
            processed_doc_index = 0
            for doc in docs:
                logger.info(f'Process doc #{processed_doc_index+1} (document size={len(doc)})')
                with get_openai_callback() as cb:
                    answer_result = self.refine_initial_chain.run(question = question, input_text = docs[processed_doc_index], no_answer = NO_ANSWER_STR)
                tokens_used += cb.total_tokens
                logger.debug(answer_result)

                answer_json = get_llm_json(answer_result)
                answer = answer_json["answer"]
                logger.info(f'answer={answer}')

                processed_doc_index += 1
                if answer and answer != NO_ANSWER_STR:
                    break

            # try to extend answer if possible
            for doc in docs[processed_doc_index:]:
                logger.info(f'Process doc #{processed_doc_index+1} (document size={len(doc)})')
                with get_openai_callback() as cb:
                    refine_result = self.refine_combine_chain.run(question = question, existed_answer = answer, more_context = doc)
                tokens_used += cb.total_tokens
                logger.debug(refine_result)
                refined_json = get_llm_json(refine_result)
                refined_useful = not refined_json["not_useful"]
                if refined_useful:
                    answer = refined_json["refined_answer"]
                    logger.info('Refined answer was accepted')
                else:
                    logger.info('Refined answer was rejected')
            
            return RefineAnswerResult(answer, tokens_used, False)
        except Exception as error: # pylint: disable=W0718
            logger.exception(error)
            logger.error(traceback.format_exc())
            return RefineAnswerResult("", tokens_used, True)
