"""
    Citations page
"""
# pylint: disable=C0301,C0103,C0303,C0304, W0611

import streamlit as st
from utils_streamlit import streamlit_hack_remove_top_space
from backend_core import BackEndCore

PAGE_NAME = "Citations"

file_index = BackEndCore.get_file_index()

# ------------------------------- UI Setup
st.set_page_config(page_title= PAGE_NAME, layout="wide")
st.title(PAGE_NAME)
streamlit_hack_remove_top_space()

index_name = st.selectbox(
    "Select index:", 
    key="index_name", 
    options= file_index.get_index_name_list(), 
    index= 0, 
    label_visibility="visible"
)

sample_count = st.number_input(label="Count of samples", min_value=1, max_value=100, value=10)
threshold = st.number_input(label="Threshold", min_value=0.00, max_value=1.00, value=0.50, step=0.01, format="%.2f")

query = st.text_input(label="Query")
run_button = st.button(label="Run")
search_result_container = st.container()

# ------------------------------- App

if not query or not run_button:
    st.stop()

score_threshold = threshold
if score_threshold == 0:
    score_threshold = None

search_result_list = BackEndCore().similarity_search(
                        index_name,
                        query, 
                        sample_count, 
                        score_threshold
                     )

for index, search_result in enumerate(search_result_list):
    e = search_result_container.expander(label=f'Result {index+1} s-score {search_result.score:0.3f}')
    col1 , col2 = e.columns([80, 20])
    col1.markdown(search_result.content)
    col2.markdown(f'Metadata:<br/>{search_result.metadata}', unsafe_allow_html=True)