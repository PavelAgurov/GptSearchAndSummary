"""
    Document set
"""
# pylint: disable=C0301,C0103,C0304,C0303,W0611

import streamlit as st

from utils_streamlit import streamlit_hack_remove_top_space
from backend_core import BackEndCore

PAGE_NAME = "Document set"

# ------------------------------- Core

document_set_manager = BackEndCore.get_document_set_manager()

# ------------------------------- UI Setup
st.set_page_config(page_title= PAGE_NAME, layout="wide")
st.title(PAGE_NAME)
streamlit_hack_remove_top_space()

document_set_manager.load()

current_documentsets = st.expander(label="Currently available document sets", expanded=True)
current_documentsets.markdown('<br/>'.join(document_set_manager.get_all_names()), unsafe_allow_html=True)

with st.form(key="addForm", clear_on_submit=True):
    new_name = st.text_input(label="Document set name:")
    submitted = st.form_submit_button("Add")
    new_name = new_name.strip()
    if submitted and new_name:
        document_set_manager.add(new_name, True)
        st.experimental_rerun()
