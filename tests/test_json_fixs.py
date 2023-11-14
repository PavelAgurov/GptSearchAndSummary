"""
    Tests
    To run: pytest
"""

# pylint: disable=C0103,R0915,C0301,C0411,C0413

import pytest
import json

import llm_json_parser as utils

bad_json = """
{ "topics":[ 
    {"topicID": 1, "score": 0.3, "explanation": "The article"}, 
    {"topicID": 11, "score": 0, "explanation": "The article ."},
    {"topicID": 12, "score": 0, "explanation": "The article ."}, ], 
    "primary_topic":
        { "topic_id" : 5, "score": 0.5, "explanation": "The article ." }, 
    "secondary_topic":
        { "topic_id" : 1, "score": 0.3, "explanation": " potential connection to the topic." } 
}
"""

bad_json1 = """
{ "topics":[ 
    {"topicID": 1, "score": 0.3, "explanation": "The article"}, 
    {"topicID": 11, "score": 0, "explanation": "The article ."},
    {"topicID": 12, "score": 0, "explanation": "The article ."}, 
   ], 
    "primary_topic":
        { "topic_id" : 5, "score": 0.5, "explanation": "The article ." }, 
    "secondary_topic":
        { "topic_id" : 1, "score": 0.3, "explanation": " potential connection to the topic." } 
}
"""

bad_json2 = """
{ "topics":[ 
    {"topicID": 1, "score": 0.3, "explanation": "The article"}, 
    {"topicID": 11, "score": 0, "explanation": "The article ."},
    {"topicID": 12, "score": 0, "explanation": "The article ."},    ], 
    "primary_topic":
        { "topic_id" : 5, "score": 0.5, "explanation": "The article ." }, 
    "secondary_topic":
        { "topic_id" : 1, "score": 0.3, "explanation": " potential connection to the topic." } 
}
"""

bad_json3 = """This is your json:
{ "topics":[ 
    {"topicID": 1, "score": 0.3, "explanation": "The article"}, 
    {"topicID": 11, "score": 0, "explanation": "The article ."},
    {"topicID": 12, "score": 0, "explanation": "The article ."}, 
   ], 
    "primary_topic":
        { "topic_id" : 5, "score": 0.5, "explanation": "The article ." }, 
    "secondary_topic":
        { "topic_id" : 1, "score": 0.3, "explanation": " potential connection to the topic." } 
}
Feel free to contact me if any questions.
"""

def check_bad_json(s : str):
    """Check that provided json raises exception, but it's fixed after get_fixed_json"""
    with pytest.raises(Exception):
        _ = json.loads(s)

    ok_json = json.loads(utils.get_fixed_json(s))
    assert ok_json is not None

def test_json_fix():
    """Test for fix json"""
    check_bad_json(bad_json)
    check_bad_json(bad_json1)
    check_bad_json(bad_json2)
    check_bad_json(bad_json3)
