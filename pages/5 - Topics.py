"""
    Topics page
"""
# pylint: disable=C0301,C0103,C0303,W0611

import streamlit as st
from utils_streamlit import streamlit_hack_remove_top_space

from backend_core import BackEndCore

# ------------------------------- Core

document_set_manager = BackEndCore.get_document_set_manager()
topic_manager = BackEndCore.get_topic_manager()

# ------------------------------- UI Setup
PAGE_NAME = "Topics"
st.set_page_config(page_title= PAGE_NAME, layout="wide")
st.title(PAGE_NAME)
streamlit_hack_remove_top_space()

document_set_manager.load()
selected_document_set = st.selectbox(
    label="Document set:",
    options=document_set_manager.get_all_names(),
    key="selected_document_set_topics"
)

selected_topic = st.selectbox(
    label="Topic:",
    options= topic_manager.get_topic_list(),
    key="topic_to_edit"
)

st.markdown(f'Similarity request: [{selected_topic.similarity_request}]. Threshold: {selected_topic.similarity_threshold}')
