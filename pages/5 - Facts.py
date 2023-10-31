"""
    Fact page
"""
# pylint: disable=C0301,C0103,C0303,W0611

import pandas as pd
import streamlit as st
from utils_streamlit import streamlit_hack_remove_top_space, hide_footer

from backend_core import BackEndCore
from ui.shared_session import set_selected_document_set, get_selected_document_set_index

# ------------------------------- Core

document_set_manager = BackEndCore.get_document_set_manager()
text_extractor = BackEndCore.get_text_extractor()

# ------------------------------- UI Setup
PAGE_NAME = "Fact page"
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
    key="selected_document_facts",
    index= selected_document_set_index
)
set_selected_document_set(selected_document_set)

if not selected_document_set:
    st.stop()

all_fact_files = text_extractor.get_all_facts_file_names(selected_document_set, True)

for fact_file in all_fact_files:
    facts = text_extractor.get_facts_from_file(selected_document_set, fact_file)
    if facts:
        data = {'Fact': facts}
        df = pd.DataFrame(data)
        df = df.applymap(lambda x: x.replace('\n', '<br>'))
        fact_expander = st.expander(label=fact_file, expanded=False)
        fact_expander.markdown(df.to_html(escape=False, index=False, header=False), unsafe_allow_html=True)
        fact_expander.markdown('\n')
        
