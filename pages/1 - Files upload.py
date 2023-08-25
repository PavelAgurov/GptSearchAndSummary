"""
    Upload files
"""
# pylint: disable=C0301,C0103,C0304,C0303,W0611

import streamlit as st

from utils_streamlit import streamlit_hack_remove_top_space
from strings import UPLOAD_FILE_MESSAGE
from backend_core import BackEndCore

PAGE_NAME = "Files Upload"

# ------------------------------- UI Setup
st.set_page_config(page_title= PAGE_NAME, layout="wide")
st.title(PAGE_NAME)
streamlit_hack_remove_top_space()

current_file_list = st.expander(label="Currently available files").empty()

new_uploaded_files = st.file_uploader(
    UPLOAD_FILE_MESSAGE,
    type=["pdf", "docx", "txt"],
    accept_multiple_files= True
)

load_button = st.button(label="Upload")
progress = st.empty()

# ------------------------------- App

source_index = BackEndCore.get_source_index()
currently_uploaded_files = source_index.get_all_files(True)
currently_uploaded_files_str = "".join([f'{file_name}<br/>' for file_name in currently_uploaded_files])
current_file_list.markdown(currently_uploaded_files_str, unsafe_allow_html=True)

if not load_button:
    st.stop()

if not new_uploaded_files:
    progress.markdown('Please load at least one file')
    st.stop()

progress.markdown('Saving files...')
for file in new_uploaded_files:
    source_index.save_file(file.name, file.getbuffer())
progress.markdown(f'Saved {len(new_uploaded_files)} files.')
