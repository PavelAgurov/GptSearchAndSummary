"""
    Extract plain text page
"""
# pylint: disable=C0301,C0103,C0304,C0303,W0611

import streamlit as st

from utils_streamlit import streamlit_hack_remove_top_space
from backend_core import BackEndCore

PAGE_NAME = "Extract plain text"

# ------------------------------- UI Setup

st.set_page_config(page_title= PAGE_NAME, layout="wide")
st.title(PAGE_NAME)
streamlit_hack_remove_top_space()

file_list = st.expander(label="Availble files").empty()

run_button = st.button(label="Run extraction")
progress = st.empty()

# ------------------------------- App

source_index = BackEndCore.get_source_index()

uploaded_files = source_index.get_all_files(True)
if not uploaded_files:
    progress.markdown('Please load at least one file')
    st.stop()

uploaded_files_str = "".join([f'<li>{file_name}<br/>' for file_name in uploaded_files])
file_list.markdown(uploaded_files_str, unsafe_allow_html=True)

if not run_button:
    st.stop()

progress.markdown('Start converting...')
extraction_result = BackEndCore().run_text_extraction()
extraction_result_str = '<br/>'.join(extraction_result)
progress.markdown(f'Result:<br/>{extraction_result_str}', unsafe_allow_html= True)
