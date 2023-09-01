"""
    Indexing page
"""
# pylint: disable=C0301,C0103,C0304,C0303,W0611

import streamlit as st

from utils_streamlit import streamlit_hack_remove_top_space
from backend_core import BackEndCore

PAGE_NAME = "Indexing"
CREATE_MODE_NEW = "New"
CREATE_MODE_EXISTED = "Existed"
# ------------------------------- Core

text_extractor = BackEndCore.get_text_extractor()
file_index = BackEndCore.get_file_index()
llm = BackEndCore.get_llm_manager()
# ------------------------------- UI Setup

st.set_page_config(page_title= PAGE_NAME, layout="wide")
st.title(PAGE_NAME)
streamlit_hack_remove_top_space()

text_files = text_extractor.get_all_source_files(True)

file_list = st.expander(label=f'Available {len(text_files)} file(s)').empty()
text_files_str = "".join([f'<li>{file_name}<br/>' for file_name in text_files])
file_list.markdown(text_files_str, unsafe_allow_html=True)

embedding_name = st.selectbox(
    "Select embedding:",
    key="embedding_name",
    options= llm.get_embedding_list(),
    index=0
)

col1 , col2, col3 = st.columns(3)
chunk_min_chars      = col1.number_input(label="Chunk min (tokens)", min_value=1, max_value=10000, value= 50)
chunk_size_tokens    = col2.number_input(label="Chunk size (tokens)", min_value=100, max_value=10000, value= 1000)
chunk_overlap_tokens = col3.number_input(label="Сhunk overlap (tokens)", min_value=0, max_value=1000, value= 0)

st.info("Database will be created from scratch!")

create_mode = st.radio(
    label="Index", 
    options= [CREATE_MODE_NEW, CREATE_MODE_EXISTED], 
    index=0, 
    label_visibility="collapsed", 
    horizontal=True
)

if create_mode == CREATE_MODE_EXISTED:
    existed_index_name = st.selectbox(
        "Select existed indexes:", 
        key="existed_index", 
        options= file_index.get_index_name_list(), 
        index= 0, 
        label_visibility="visible"
    )
else:
    new_index_name = st.text_input(label="Enter index name")

run_button = st.button(label="Run indexing")
progress = st.empty()

if not text_files:
    progress.markdown('There are no files for indexing.')
    st.stop()

if not run_button:
    st.stop()

if create_mode == CREATE_MODE_NEW:
    if not new_index_name: 
        progress.markdown('Enter index name.')
        st.stop()
    index_name = new_index_name

if create_mode == CREATE_MODE_EXISTED:
    if not existed_index_name: 
        progress.markdown('There is no selected index.')
        st.stop()
    index_name = existed_index_name

progress.markdown(f'Start indexing [{index_name}] ...')
indexing_result = BackEndCore().run_file_indexing(embedding_name, index_name, chunk_min_chars, chunk_size_tokens, chunk_overlap_tokens)
indexing_result_str = '<br/>'.join(indexing_result)
progress.markdown(f'Result:<br/>{indexing_result_str}', unsafe_allow_html= True)
