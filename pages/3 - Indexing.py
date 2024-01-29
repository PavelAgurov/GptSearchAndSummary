"""
    Indexing page
"""
# pylint: disable=C0301,C0103,C0304,C0303,W0611

import streamlit as st

from utils_streamlit import streamlit_hack_remove_top_space, hide_footer
from backend_core import BackEndCore, BackendFileIndexingParams
from ui.shared_session import set_selected_document_set, get_selected_document_set_index
from utils.app_logger import init_streamlit_logger
from core.parsers.chunk_splitters.base_splitter import ChunkSplitterMode

CREATE_MODE_NEW = "New"
CREATE_MODE_EXISTED = "Existed"
# ------------------------------- Core

document_set_manager = BackEndCore.get_document_set_manager()
text_extractor = BackEndCore.get_text_extractor()
file_index = BackEndCore.get_file_index()
embedding_manager = BackEndCore.get_embedding_manager()

init_streamlit_logger()
# ------------------------------- UI Setup
PAGE_NAME = "Indexing"
st.set_page_config(page_title= PAGE_NAME, layout="wide")
st.title(PAGE_NAME)
streamlit_hack_remove_top_space()
hide_footer()

document_set_manager.load()

selected_document_set_data  = [''] + document_set_manager.get_all_names()
selected_document_set_index = get_selected_document_set_index(selected_document_set_data)
selected_document_set = st.selectbox(
    label="Document set:",
    options= selected_document_set_data,
    key="selected_document_set_indexing",
    index= selected_document_set_index
)
set_selected_document_set(selected_document_set)

if not selected_document_set:
    st.stop()

text_files = text_extractor.get_all_source_file_names(selected_document_set, True)

file_list = st.expander(label=f'Available {len(text_files)} page(s)').empty()
text_files_str = "".join([f'{file_name}<br/>' for file_name in text_files])
file_list.markdown(text_files_str, unsafe_allow_html=True)

embedding_item = st.selectbox(
    "Select embedding:",
    key="embedding_name",
    options= embedding_manager.get_embedding_information_list(),
    index=0
)

st.info(f'{embedding_item.description}. Recommended default_threshold: {embedding_item.default_threshold}')

use_formatted  = st.checkbox(label="Use formatted text where possible")

selected_chunk_splitter_mode = st.selectbox(
        label="Chunk splitter mode", 
        options= list(ChunkSplitterMode),
        format_func= lambda m: m.value
)

col1 , col2, col3 = st.columns(3)
chunk_min_chars      = col1.number_input(label="Chunk min (tokens)", min_value=1, max_value=10000, value= 20)
chunk_size_tokens    = col2.number_input(label="Chunk size (tokens)", min_value=1, max_value=10000, value= 100)
chunk_overlap_tokens = col3.number_input(label="Сhunk overlap (tokens)", min_value=0, max_value=1000, value= 0)

st.info("Index will be created from scratch!")

create_mode = st.radio(
    label="Index", 
    options= [CREATE_MODE_NEW, CREATE_MODE_EXISTED], 
    index=0, 
    label_visibility="collapsed", 
    horizontal=True
)

if create_mode == CREATE_MODE_EXISTED:
    existed_index_name = st.selectbox(
        "Select existed index:", 
        key="existed_index", 
        options= file_index.get_index_name_list(selected_document_set), 
        index= 0, 
        label_visibility="visible"
    )
else:
    new_index_name = st.text_input(label="Enter index name:")

col1e, col2e, col3e = st.columns([10,10,40])
run_button = col1e.button(label="Run indexing")
if create_mode == CREATE_MODE_EXISTED and existed_index_name:
    delete_button = col2e.button(label="Delete index")
    if delete_button:
        file_index.delete_index(selected_document_set, existed_index_name)
        st.rerun()

    set_as_default_button = col3e.button(label="Set as default index")
    if set_as_default_button:
        document_set_manager.set_default_index(selected_document_set, existed_index_name)
        st.rerun()

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
indexing_result = BackEndCore().run_file_indexing(
    selected_document_set,
    BackendFileIndexingParams(
        embedding_item,
        index_name,
        chunk_min_chars,
        chunk_size_tokens,
        chunk_overlap_tokens,
        use_formatted,
        selected_chunk_splitter_mode
    )
)
indexing_result_str = '<br/>'.join(indexing_result)
progress.markdown(f'Result:<br/>{indexing_result_str}', unsafe_allow_html= True)
