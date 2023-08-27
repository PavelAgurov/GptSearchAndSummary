"""
    Citations page
"""
# pylint: disable=C0301,C0103,C0303,C0304, W0611

import streamlit as st
from utils_streamlit import streamlit_hack_remove_top_space
from backend_core import BackEndCore

PAGE_NAME = "Citations"

# ------------------------------- UI Setup
st.set_page_config(page_title= PAGE_NAME, layout="wide")
st.title(PAGE_NAME)
streamlit_hack_remove_top_space()

sample_count = st.number_input(label="Count of samples", min_value=1, max_value=100, value=10)
threshold = st.number_input(label="Threshold", min_value=0.00, max_value=1.00, value=0.50, step=0.01, format="%.2f")

query = st.text_input(label="Query")
run_button = st.button(label="Run")
search_result_container = st.container()

# ------------------------------- App

if not query or not run_button:
    st.stop()

fileIndex = BackEndCore.get_file_index()
llm_manager = BackEndCore.get_llm()

score_threshold = threshold
if score_threshold == 0:
    score_threshold = None

search_result_list = fileIndex.similarity_search(
    query, 
    llm_manager.get_embeddings(), 
    sample_count, 
    score_threshold
)

for index, search_result in enumerate(search_result_list):
    e = search_result_container.expander(label=f'Result {index+1} score {search_result.score}')
    e.markdown(search_result.content)