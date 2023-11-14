"""
    Parser json for LLM
"""

# pylint: disable=C0301,C0103,C0304,C0303,W0611,W0511,R0913,R0402,W1203

import re
import json
import logging
import traceback

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

def get_llm_json(text : str) -> any:
    """Get fixed LLM Json"""
    try:
        return json.loads(get_fixed_json(text))
    except Exception as error: # pylint: disable=W0718
        logger.error('----------------------')
        logger.error(f'Error: {error}.')
        logger.error(f'Track: {traceback.format_exc()}')
        logger.error(f'JSON: {text}')
        logger.error('----------------------')
        raise error