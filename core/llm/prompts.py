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
You are a journalist.
Your job is to convert provided text (separated by XML tags) into useful facts in context "{context}".
You must ignore all information that is not relevant to given context (e.g. greetings, polite words, etc.)
You should convert all relevant facts with "{context}" as Subject and remove unuseful noise.

Do not make up facts, use only provided text!

Do no split paragraphs with programming code, json, xml etc.

For each fact you should add a score of relevance from 0 to 1 (0 - not relevant, 1 - fully relevant).
Do nice text formatting and correct English where it's needed before output.

Provide answer in JSON format with fields:
- relevant_facts - list of facts and their scores that are relevant to the given context
- count_other_facts - count of facts that are not relevant to the given context

<input_text>{input_text}</input_text>
"""