"""
    Citations page
"""
# pylint: disable=C0301,C0103,C0303,C0304, W0611

import streamlit as st
from utils_streamlit import streamlit_hack_remove_top_space, hide_footer
from backend_core import BackEndCore
from ui.shared_session import set_selected_document_set, set_selected_document_set_index

# ------------------------------- Const
QUERY_MODE_NEW = "New query"
QUERY_MODE_FROM_HISOTRY = "Saved query"

# ------------------------------- Core

document_set_manager = BackEndCore.get_document_set_manager()
file_index = BackEndCore.get_file_index()
user_query_manager = BackEndCore.get_user_query_manager()

# ------------------------------- UI Setup
PAGE_NAME = "Citations"
st.set_page_config(page_title= PAGE_NAME, layout="wide")
st.title(PAGE_NAME)
streamlit_hack_remove_top_space()
hide_footer()

document_set_manager.load()

selected_document_set_data  = [''] + document_set_manager.get_all_names()
selected_document_set_index = set_selected_document_set_index(selected_document_set_data)
selected_document_set = st.selectbox(
    label="Document set:",
    options= selected_document_set_data,
    key="selected_document_set_indexing",
    index= selected_document_set_index
)
set_selected_document_set(selected_document_set)

if not selected_document_set:
    st.stop()

index_name = st.selectbox(
    "Select index:", 
    key="index_name_c", 
    options= file_index.get_index_name_list(selected_document_set), 
    index= 0, 
    label_visibility="visible"
)

if index_name:
    index_info = file_index.get_file_index_meta(selected_document_set, index_name)
    if not index_info.error:
        splitter_params= index_info.chunkSplitterParams.splitter_params
        index_info_str = f'Document set: {index_info.document_set}.\
                Embedding name: {index_info.embedding_name}. \
                Chunk min={splitter_params.chunk_min_tokens}, \
                chunk size={splitter_params.tokens_per_chunk},\
                overlap={splitter_params.chunk_overlap_tokens}.'
        if index_info.default_threshold > 0:
            index_info_str += f' Recommended Default threshold for similarity: {index_info.default_threshold}.'
        st.info(index_info_str)
    else:
        st.info(index_info.error)
        st.stop()

col11, col12 = st.columns(2)
sample_count = col11.number_input(label="Count of samples:", min_value=1, max_value=100, value=3)
threshold = col12.number_input(label="Similarity threshold:", min_value=0.00, max_value=1.00, value=0.50, step=0.01, format="%.2f")

col41, col42, _ = st.columns([20, 20, 80])
add_llm_score = col41.checkbox(label="Add LLM score", value=False)
llm_threshold = col42.number_input(label="LLM Threshold:", min_value=0.00, max_value=1.00, value=0.50, step=0.01, format="%.2f", disabled=not add_llm_score)

build_summary = st.checkbox(label="Build summary", value=True)

query_mode = st.radio(
    label="Query", 
    options= [QUERY_MODE_NEW, QUERY_MODE_FROM_HISOTRY], 
    index=0, 
    label_visibility="collapsed", 
    horizontal=True
)

if query_mode == QUERY_MODE_NEW:
    query = st.text_input(label="Query:")
if query_mode == QUERY_MODE_FROM_HISOTRY:
    query = st.selectbox(label="Saved query:", options= user_query_manager.get_query_history_query(selected_document_set, 10))

col21, col22 = st.columns(2)
run_button = col21.button(label="Run")
run_status = col22.empty()

search_result_container  = st.container()
summary_result_container = st.container()


def show_status_callback(status_str : str):
    """Show progress/status"""
    run_status.markdown(status_str)

# ------------------------------- App
show_status_callback('')

if not query:
    show_status_callback('No query')
    st.stop()

if not run_button:
    st.stop()

score_threshold = threshold
if score_threshold == 0:
    score_threshold = None

chunk_list = BackEndCore().similarity_search(
                        selected_document_set,
                        index_name,
                        query, 
                        sample_count, 
                        score_threshold,
                        add_llm_score,
                        llm_threshold,
                        show_status_callback
                     )

if add_llm_score:
    chunk_list.sort(key=lambda x: x.llm_score, reverse=True)

for index, chunk_item in enumerate(chunk_list):
    chunk_label = f'Result {index+1} s-score {chunk_item.score:0.3f}'
    if add_llm_score:
        chunk_label = f'{chunk_label} llm-score {chunk_item.llm_score:0.3f}'
    e = search_result_container.expander(label=chunk_label)
    col31 , col32 = e.columns([80, 20])
    col31.markdown(chunk_item.content)
    col32.markdown(f'Metadata:<br/>{chunk_item.metadata}', unsafe_allow_html=True)
    if add_llm_score:
        col32.divider()
        col32.markdown(f'LLM explanation:<br/>{chunk_item.llm_expl}', unsafe_allow_html=True)

if not chunk_list:
    summary_result_container.markdown('There are no relevant information')
    st.stop()
    
if not build_summary:
    st.stop()

summary = BackEndCore().build_answer(query, chunk_list)
summary_result_container.markdown(summary)

setup_str = f'sample_count={sample_count}, score_threshold={score_threshold}, add_llm_score={add_llm_score}, llm_threshold={llm_threshold}'
user_query_manager.log_query(selected_document_set, query, summary, setup_str)
