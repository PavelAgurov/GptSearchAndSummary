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

knowledge_tree_prompt_template = """\
Extract detailed semantic triples and relations between triples from the provided text (separated by XML tags), including Subject, Predicate and Objects for every triple. 
Format all the results as indented pretty JSON. Return only JSON.

Example input:
The attrition rates related to our IT professionals who have worked for us for at least six months were 13.1%, 10.7% and 9.1% for 2013, 
2012 and 2011, respectively.

Example output:
{{
  "triples": [
    {{
    "Subject": "attrition rates",
        "Predicate": "were",
        "Objects": [
            {{"object": "13.1% for 2013"}},
            {{"object": "10.7% for 2012"}},
            {{"object": "9.1% for 2011"}}
        ]
    }},
    {{
      "Subject": "IT professionals",
      "Predicate": "have worked for us",
      "Objects":[
            {{"object": ""at least six month"}}
      ]
    }},    
  ]
}}

<text>
{text}
</text>
"""
