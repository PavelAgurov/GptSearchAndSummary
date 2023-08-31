"""
    LLM Utils
"""

# pylint: disable=C0305,C0303

import re
 
def get_fixed_json(text : str) -> str:
    """Fix LLM json"""
    text = re.sub(r"},\s*]", "}]", text)
    open_bracket = min(text.find('['), text.find('{'))
    if open_bracket == -1:
        return text
           
    close_bracket = max(text.rfind(']'), text.rfind('}'))
    if close_bracket == -1:
        return text
    return text[open_bracket:close_bracket+1]

