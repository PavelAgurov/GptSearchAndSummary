"""
    Refine answer
"""
# pylint: disable=C0301,C0103,C0304,C0303,W0611,W0511,R0913,R0402

from dataclasses import dataclass
import json
from langchain.prompts.prompt import PromptTemplate
from langchain.chains import LLMChain
from langchain.callbacks import get_openai_callback

from core.llm.llm_utils import get_fixed_json

answer_initial_prompt_template = """\
Write a concise answer to the question (delimited with XML tags) from the provided text (delimited with XML tags).
If text has no answer to the question - say "No answer".
Please provide result in JSON format:
{{
    "answer": "answer here"
}}

<question>
{question}
</question>

<text>
{text}
</text>
"""

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
    error       : str = None
    steps       : [] = None

class RefineAnswerChain():
    """Refine chain"""
    refine_initial_chain : LLMChain
    refine_combine_chain : LLMChain
    
    def __init__(self, llm):
        refine_initial_prompt = PromptTemplate(template= answer_initial_prompt_template, input_variables=["question", "text"])
        self.refine_initial_chain = LLMChain(llm= llm, prompt= refine_initial_prompt)
        refine_combine_prompt = PromptTemplate(template= answer_combine_prompt_template, input_variables=["question", "existing_answer", "more_context"])
        self.refine_combine_chain = LLMChain(llm= llm, prompt= refine_combine_prompt)

    def log(self, steps, include_steps, step_message):
        """Add log item"""
        if include_steps:
            steps.append(step_message)
        return steps

    def run(self, question : str, docs : list, enable_logger : bool = False) -> RefineAnswerResult:
        """Run refine"""
        tokens_used = 0
        answer = ""
        steps = []

        try:
            steps = self.log(steps, enable_logger, 'Process doc #1')
            with get_openai_callback() as cb:
                answer_result = self.refine_initial_chain.run(question = question, text = docs[0])
            tokens_used += cb.total_tokens
            steps = self.log(steps, enable_logger, answer_result)
            steps = self.log(steps, enable_logger, f'Doc count {len(docs)}')
            answer_json = json.loads(get_fixed_json(answer_result))
            answer = answer_json["answer"]

            for index, doc in enumerate(docs[1:]):
                steps = self.log(steps, enable_logger, f'Process doc #{index+2}')
                with get_openai_callback() as cb:
                    refine_result = self.refine_combine_chain.run(question = question, existing_answer = answer, more_context = doc)
                tokens_used += cb.total_tokens
                steps = self.log(steps, enable_logger, refine_result)
                refined_json = json.loads(get_fixed_json(refine_result))
                refined_useful = not refined_json["not_useful"]
                if refined_useful:
                    answer = refined_json["refined_answer"]
            
            return RefineAnswerResult(answer, tokens_used, steps = steps)
        except Exception as error: # pylint: disable=W0718
            steps = self.log(steps, enable_logger, error)
            return RefineAnswerResult(answer, tokens_used, error= error, steps = steps)
