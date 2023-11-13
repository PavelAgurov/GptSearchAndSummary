"""
    LLM Utils
"""

# pylint: disable=C0305,C0303

import json
import traceback
from core.llm.json_parser import get_fixed_json

def parse_llm_xml(text : str, variables : list[str]) -> dict[str, str]:
    """Parse XML for LLM"""
    result = dict[str, str]()
    for var_name in variables:
        result[var_name] = ''
        start_var_name = f'<{var_name}>'
        start_index = text.find(start_var_name)
        if start_index == -1:
            continue
        end_index = text.find(f'</{var_name}>')
        if end_index == -1:
            # hack - if we have only one tag and it's not closed - guess that it's full text
            if len(variables) == 1:
                var_value_fixed = text[start_index + len(start_var_name):]
                if var_value_fixed:
                    var_value_fixed = var_value_fixed.strip()
                result[var_name] = var_value_fixed
            continue
        var_value = text[start_index + len(start_var_name):end_index]
        if var_value:
            var_value = var_value.strip()
        result[var_name] = var_value
    return result

def get_llm_json(text : str) -> any:
    """Get fixed LLM Json"""
    try:
        return json.loads(get_fixed_json(text))
    except Exception as error: # pylint: disable=W0718
        print('----------------------')
        print(f'Error: {error}.')
        print(f'Track: {traceback.format_exc()}')
        print(f'JSON: {text}')
        print('----------------------')
        raise error

