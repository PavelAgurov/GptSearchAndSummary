"""
    LLM prompts
"""

# pylint: disable=C0103


relevance_prompt_template = """\
You are the best linguist who can compare texts.
You should understand if provided content (separated by XML tags) is relevant to the query (separated by XML tags).
Relevance score is a number from 0 till 1. 0 means "not relevant", 1 means "relevant".
Content is only relevant when you have FULL DIRECT answer to the query, not a reference to other place.
###
Provide result in JSON:
{{
    "score" : score how provided content is relevant to the query,
    "explanation" : "explanation why provided content is relevant to the query or why not"
}}
###
<query>
{query}
</query>
###
<content>
{content}
</content>

"""