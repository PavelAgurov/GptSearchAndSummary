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
You are a networked intelligence helping a human track knowledge triples about all relevant people, things, concepts, etc. 
and integrating them with your knowledge stored within your weights as well as that stored in a knowledge graph. 
Extract all of the knowledge triples from the last line of conversation. 
A knowledge triple is a clause that contains a subject, a predicate, and an object. 
The subject is the entity being described, the predicate is the property of the subject that is being described, 
and the object is the value of the property.

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


format_prompt_template = """\
You are the best parsing linguist. 
I will give you text (separated by XML tags). 
Your task is to find all paragraphs,  tables, headers and sub-topics in provided text and mark them by HTML tags <h1>,<h2>,<p>,<table> etc. 
Remove uninformative short paragraphs. 
Mark paragraphs with programming code, json, xml etc. by <code> tag.
For each table you should add attribute 'title' into table header.
Do not create nested tables.
Return this text with this new tags, tables and good formatted paragraphs into XML tag 'output_text'.

<output_text>
    Output text here
</output_text>

<input_text>
{input_text}
</input_text>
"""

extract_facts_prompt_template = """/
You are a expert in fact extraction.

Do your job step by step:
1. read provided text (separated by XML tags).
2. find tables: relevant header, columns and rows.
3. find paragraphs with programming code, json, xml etc.
4. extract useful facts in context "{context}".
5. remove unuseful noise that is no relevant to the context "{context}".
6. table should be included into one fact with header, do not split tables as separated facts.
7. programming code should be included into fact, do not split code as separated facts.
8. ignore all information that is not relevant to given context (e.g. greetings, polite words, etc).
9. do nice text formatting and correct English where it's needed before output.
10. for each fact you should add a score of relevance from 0 to 1 (0 - not relevant, 1 - fully relevant).
11. if fact has no useful information you should set score to 0.

Provide answer in JSON format with fields:
- relevant_facts - list of facts and their scores that are relevant to the given context
- count_other_facts - count of facts that are not relevant to the given context

<input_text>{input_text}</input_text>
"""