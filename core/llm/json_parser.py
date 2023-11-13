"""
    JsonFixOutputFunctionsParser
"""

# pylint: disable=C0301,C0103,C0304,C0303,W0611,W0511,R0913,R0402,W1203

import re
import json
from typing import List, Union
import logging

from langchain.schema import (
    ChatGeneration,
    Generation,
    OutputParserException,
    BaseLLMOutputParser
)

from langchain.output_parsers.openai_functions import JsonOutputFunctionsParser

logger : logging.Logger = logging.getLogger()

def get_fixed_json(text : str) -> str:
    """Fix LLM json"""
    text = re.sub(r'",\s*}', '"}', text)
    text = re.sub(r"},\s*]", "}]", text)
    text = re.sub(r"}\s*{", "},{", text)

    open_bracket = min(text.find('['), text.find('{'))
    if open_bracket == -1:
        return text

    close_bracket = max(text.rfind(']'), text.rfind('}'))
    if close_bracket == -1:
        return text
    return text[open_bracket:close_bracket+1]

def is_json( text: str) -> str:
    """True if string can be json"""
    return text.startswith('[') or text.startswith('{')

class JsonFixLLMOutputParser(BaseLLMOutputParser):
    """Parse an output as the Json object."""

    function_name : str
    """Name of function to parse"""

    def __init__(self, function_name : str):
        """Initialize"""
        super().__init__()
        self.function_name = function_name

    def parse_result(self, result: List[Generation], *, partial: bool = False) -> Union[str, dict]:
        """Parse a list of candidate model Generations into a specific format."""

        if len(result) != 1:
            raise OutputParserException(
                f"Expected exactly one result, but got {len(result)}"
            )
        generation = result[0]
        if not isinstance(generation, ChatGeneration):
            raise OutputParserException(
                "This output parser can only be used with a chat generation."
            )

        logger.debug(f'generation={generation}')

        content = generation.message.content
        if not is_json(content):
            return content

        fixed_json = None
        try:
            fixed_json = json.loads(get_fixed_json(content))
        except Exception as error: # pylint: disable=W0718
            logger.error(error)
            return None

        if isinstance(fixed_json, list):
            fixed_json = fixed_json[0]

        if 'name' in fixed_json and 'parameters' in fixed_json:
            fixed_json = fixed_json['parameters']
            if 'properties' not in fixed_json:
                return fixed_json
            return fixed_json['properties']
        
        output_json = fixed_json
        if self.function_name in fixed_json:
            output_json = fixed_json[self.function_name]
            
        if not output_json:
            return None

        not_null_values = [v for v in output_json.values() if v]
        if not_null_values:
            return output_json
        
        return None
            
class JsonFixOutputFunctionsParser(JsonOutputFunctionsParser):
    """Parse an output as the Json object."""

    def parse_result(self, result: List[Generation], *, partial: bool = False) -> Union[str, dict]:
        
        if len(result) != 1:
            raise OutputParserException(
                f"Expected exactly one result, but got {len(result)}"
            )
        generation = result[0]
        if not isinstance(generation, ChatGeneration):
            raise OutputParserException(
                "This output parser can only be used with a chat generation."
            )

        message = generation.message

        # in some cases content contains full copy of 'function_call' - need to avoid it
        if message.content and "function_call" not in message.additional_kwargs:
            return message.content

        # TODO: to add type validation        
        # call_name = message.additional_kwargs['name']
        # if call_name != self.expected_type.__name__:
        #     raise OutputParserException(
        #         f"Expected function_call ExtractedAnswer in result: {self.expected_type.__name__}, got {call_name}"
        #     )

        try:
            function_call = message.additional_kwargs["function_call"]
        except KeyError as exc:
            if partial:
                return None
            raise OutputParserException("Could not parse function call") from exc
        fixed_json = get_fixed_json(str(function_call["arguments"]))
        return json.loads(fixed_json)