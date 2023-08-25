"""
    Indexing page
"""
# pylint: disable=C0301,C0103,C0304,C0303,W0611

import streamlit as st

from utils_streamlit import streamlit_hack_remove_top_space
from backend_core import BackEndCore

PAGE_NAME = "Indexing"

# ------------------------------- UI Setup

st.set_page_config(page_title= PAGE_NAME, layout="wide")
st.title(PAGE_NAME)
streamlit_hack_remove_top_space()

file_list = st.expander(label="Available files").empty()

col1 , col2 = st.columns(2)
chunk_size = col1.number_input(label="Chunk size", min_value=100, max_value=10000, value= 1000)
chunk_overlap = col2.number_input(label="Сhunk overlap", min_value=0, max_value=1000, value= 0)

st.info("Database will be created from scratch!")
run_button = st.button(label="Run indexing")
progress = st.empty()

# ------------------------------- App

text_extractor = BackEndCore.get_text_extractor()

text_files = text_extractor.get_all_files(True)
if not text_files:
    progress.markdown('Please extract text from at least one file')
    st.stop()

text_files_str = "".join([f'<li>{file_name}<br/>' for file_name in text_files])
file_list.markdown(text_files_str, unsafe_allow_html=True)

if not run_button:
    st.stop()

progress.markdown('Start indexing...')
indexing_result = BackEndCore().run_file_indexing(chunk_size, chunk_overlap)
indexing_result_str = '<br/>'.join(indexing_result)
progress.markdown(f'Result:<br/>{indexing_result_str}', unsafe_allow_html= True)
