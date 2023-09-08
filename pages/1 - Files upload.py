"""
    Upload files
"""
# pylint: disable=C0301,C0103,C0304,C0303,W0611

import streamlit as st

from utils_streamlit import streamlit_hack_remove_top_space
from backend_core import BackEndCore

PAGE_NAME = "Files Upload"

SESSION_UPLOADED_STATUS = 'files_uploaded_status'
if SESSION_UPLOADED_STATUS not in st.session_state:
    st.session_state[SESSION_UPLOADED_STATUS] = None

# ------------------------------- Core

document_set_manager = BackEndCore.get_document_set_manager()
source_index = BackEndCore.get_source_storage()

# ------------------------------- UI Setup
st.set_page_config(page_title= PAGE_NAME, layout="wide")
st.title(PAGE_NAME)
streamlit_hack_remove_top_space()

document_set_manager.load()
selected_document_set = st.selectbox(
    label="Data set:",
    options=document_set_manager.get_all_names(),
    key="selected_document_set_file_upload"
)

currently_uploaded_files = source_index.get_all_files(selected_document_set, True)

current_file_list = st.expander(label=f"Currently available {len(currently_uploaded_files)} file(s)")
st.info('When files are uploaded or deleted, indexing does not start automatically')

if currently_uploaded_files:
    for index, file_name in enumerate(currently_uploaded_files):
        emp = current_file_list.empty()
        col1, col2 = emp.columns([9, 1])
        col1.markdown(file_name)
        if col2.button("Del", key=f"button_delete_{index}"):
            source_index.delete_file(selected_document_set, file_name)
            st.experimental_rerun()
else:
    current_file_list.markdown("No files available")

with st.form(key="uploadFiles", clear_on_submit=True):
    new_uploaded_files = st.file_uploader(
        'Choose files for indexing (PDF, Word, Txt)',
        type=["pdf", "docx", "txt", "msg"],
        accept_multiple_files= True,
        key="new_uploaded_files"
    )

    load_button = st.form_submit_button(label="Upload")
    progress = st.empty()

# ------------------------------- App
status = st.session_state[SESSION_UPLOADED_STATUS]
if status:
    st.info(f'Uploaded {status}')
st.session_state[SESSION_UPLOADED_STATUS] = None

if not load_button:
    st.stop()

if not new_uploaded_files:
    progress.markdown('Please load at least one file')
    st.stop()

progress.markdown('Saving files...')
for file in new_uploaded_files:
    source_index.save_file(selected_document_set, file.name, file.getbuffer())
st.session_state[SESSION_UPLOADED_STATUS] = f'Uploaded {len(new_uploaded_files)} file(s)'
st.experimental_rerun()
