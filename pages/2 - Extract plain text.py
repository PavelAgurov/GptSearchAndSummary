"""
    Extract plain text page
"""
# pylint: disable=C0301,C0103,C0304,C0303,W0611

import streamlit as st

from utils_streamlit import streamlit_hack_remove_top_space
from backend_core import BackEndCore

PAGE_NAME = "Extract plain text"

# ------------------------------- Core

source_index = BackEndCore.get_source_storage()
text_extractor = BackEndCore.get_text_extractor()
document_set_manager = BackEndCore.get_document_set_manager()

# ------------------------------- UI Setup

st.set_page_config(page_title= PAGE_NAME, layout="wide")
st.title(PAGE_NAME)
streamlit_hack_remove_top_space()

document_set_manager.load()
selected_document_set = st.selectbox(
    label="Document set:",
    options=document_set_manager.get_all_names(),
    key="selected_document_set_extract"
)

uploaded_files = source_index.get_all_files(selected_document_set, True)

file_list = st.expander(label=f"Available {len(uploaded_files)} source file(s)").empty()

uploaded_files_str = "".join([f'{file_name}<br/>' for file_name in uploaded_files])
file_list.markdown(uploaded_files_str, unsafe_allow_html=True)

text_files = text_extractor.get_all_source_files(selected_document_set, True)
st.info(f'There are {len(text_files)} chunks for selected document set. They will be re-created.')

progress = st.empty()

if not uploaded_files:
    progress.markdown('Please load at least one file')
    st.stop()

run_button = st.button(label="Run extraction")
if not run_button:
    st.stop()

progress.markdown('Start converting...')
extraction_result = BackEndCore().run_text_extraction(selected_document_set)
extraction_result_str = '<br/>'.join(extraction_result)
progress.markdown(f'Result:<br/>{extraction_result_str}', unsafe_allow_html= True)
