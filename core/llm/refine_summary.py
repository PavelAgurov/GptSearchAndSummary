"""
    Refine summary
"""
# pylint: disable=C0301,C0103,C0304,C0303,W0611,W0511,R0913,R0402

from dataclasses import dataclass
import json
from langchain.prompts.prompt import PromptTemplate
from langchain.chains import LLMChain
from langchain.callbacks import get_openai_callback

from core.llm.llm_utils import get_fixed_json

refine_initial_prompt_template = """\
Write a concise summary of the text (delimited with XML tags).
Please provide result in JSON format:
{{
    "summary": "summary here"
}}

<text>
{text}
</text>
"""

refine_combine_prompt_template = """\
Your job is to produce a final summary. We have provided an existing summary up to a certain point (delimited with XML tags).
We have the opportunity to refine the existing summary (only if needed) with some more context (delimited with XML tags).
Given the new context, refine the original summary (only if new context is useful) otherwise say that it's not useful.
Please provide result in JSON format:
{{
    "not_useful": "True if new context was not useful, False if new content was used",
    "refined_summary": "refined summary here if new context was useful"
}}

<existing_summary>
{existing_summary}
</existing_summary>

<more_context>
{more_context}
</more_context>
"""

@dataclass
class RefineSummaryResult():
    """Result of refine"""
    summary : str
    tokens_used : int
    error : str = None
    steps : [] = None

class RefineSummaryChain():
    """Refine chain"""
    refine_initial_chain : LLMChain
    refine_combine_chain : LLMChain
    
    def __init__(self, llm):
        refine_initial_prompt = PromptTemplate(template= refine_initial_prompt_template, input_variables=["text"])
        self.refine_initial_chain = LLMChain(llm= llm, prompt= refine_initial_prompt)
        refine_combine_prompt = PromptTemplate(template= refine_combine_prompt_template, input_variables=["existing_summary", "more_context"])
        self.refine_combine_chain = LLMChain(llm= llm, prompt= refine_combine_prompt)

    def log(self, steps, include_steps, step_message):
        """Add log item"""
        if include_steps:
            steps.append(step_message)
        return steps

    def run(self, docs : list, enable_logger : bool = False) -> RefineSummaryResult:
        """Run refine"""
        tokens_used = 0
        summary = ""
        steps = []

        try:
            steps = self.log(steps, enable_logger, 'Process doc #1')
            with get_openai_callback() as cb:
                summary_result = self.refine_initial_chain.run(text = docs[0])
            tokens_used += cb.total_tokens
            steps = self.log(steps, enable_logger, summary_result)
            steps = self.log(steps, enable_logger, f'Doc count {len(docs)}')
            summary_json = json.loads(get_fixed_json(summary_result))
            summary = summary_json["summary"]

            for index, doc in enumerate(docs[1:]):
                steps = self.log(steps, enable_logger, f'Process doc #{index+2}')
                with get_openai_callback() as cb:
                    refine_result = self.refine_combine_chain.run(existing_summary = summary, more_context = doc)
                tokens_used += cb.total_tokens
                steps = self.log(steps, enable_logger, refine_result)
                refined_json = json.loads(get_fixed_json(refine_result))
                refined_useful = not refined_json["not_useful"]
                if refined_useful:
                    summary = refined_json["refined_summary"]
            
            return RefineSummaryResult(summary, tokens_used, steps = steps)
        except Exception as error: # pylint: disable=W0718
            steps = self.log(steps, enable_logger, error)
            return RefineSummaryResult(summary, tokens_used, error= error, steps = steps)
