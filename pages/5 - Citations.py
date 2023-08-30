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

if index_name:
    index_info = file_index.get_file_index_meta(index_name)
    splitter_params= index_info.chunkSplitterParams.splitter_params
    st.info(f'Embedding name: {index_info.embedding_name}. \
            Chunk min={splitter_params.chunk_min_tokens}, \
            chunk size={splitter_params.tokens_per_chunk},\
            overlap={splitter_params.chunk_overlap_tokens}'
    )

col1, col2 = st.columns(2)
sample_count = col1.number_input(label="Count of samples", min_value=1, max_value=100, value=10)
threshold = col2.number_input(label="Threshold", min_value=0.00, max_value=1.00, value=0.50, step=0.01, format="%.2f")

add_llm_score = st.checkbox(label="Add LLM score")

query = st.text_input(label="Query")
run_button = st.button(label="Run")
search_result_container = st.container()

# ------------------------------- App

if not query or not run_button:
    st.stop()

score_threshold = threshold
if score_threshold == 0:
    score_threshold = None

chunk_list = BackEndCore().similarity_search(
                        index_name,
                        query, 
                        sample_count, 
                        score_threshold,
                        add_llm_score
                     )

for index, chunk_item in enumerate(chunk_list):
    chunk_label = f'Result {index+1} s-score {chunk_item.score:0.3f}'
    if add_llm_score:
        chunk_label = f'{chunk_label} llm-score {chunk_item.llm_score:0.3f}'
    e = search_result_container.expander(label=chunk_label)
    col1 , col2 = e.columns([80, 20])
    col1.markdown(chunk_item.content)
    col2.markdown(f'Metadata:<br/>{chunk_item.metadata}', unsafe_allow_html=True)
    if add_llm_score:
        col2.divider()
        col2.markdown(f'LLM explanation:<br/>{chunk_item.llm_expl}', unsafe_allow_html=True)