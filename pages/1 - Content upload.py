"""
    Upload content
"""
# pylint: disable=C0301,C0103,C0304,C0303,W0611

import urllib
import streamlit as st

from utils_streamlit import streamlit_hack_remove_top_space, hide_footer
from backend_core import BackEndCore

# ------------------------------- Consts

CONTENT_FROM_FILE = 'From file'
CONTENT_FROM_URL_HTML  = 'From URL (html)'

# ------------------------------- Session

SESSION_UPLOADED_STATUS = 'content_uploaded_status'
if SESSION_UPLOADED_STATUS not in st.session_state:
    st.session_state[SESSION_UPLOADED_STATUS] = None

# ------------------------------- Core

document_set_manager = BackEndCore.get_document_set_manager()
source_index = BackEndCore.get_source_storage()

# ------------------------------- UI Setup
PAGE_NAME = "Content Upload"
st.set_page_config(page_title= PAGE_NAME, layout="wide")
st.title(PAGE_NAME)
streamlit_hack_remove_top_space()
hide_footer()

document_set_manager.load()
selected_document_set = st.selectbox(
    label="Document set:",
    options=document_set_manager.get_all_names(),
    key="selected_document_set_content_upload"
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

content_type = st.radio("Content type:", [CONTENT_FROM_FILE, CONTENT_FROM_URL_HTML], horizontal=True)

new_uploaded_files = None
new_uploaded_url   = None

with st.form(key="uploadContent", clear_on_submit=True):
    if content_type == CONTENT_FROM_FILE:
        new_uploaded_files = st.file_uploader(
            'Choose files for indexing (PDF, Word, Txt)',
            type=["pdf", "docx", "txt", "msg"],
            accept_multiple_files= True,
            key="new_uploaded_files"
        )
    if content_type == CONTENT_FROM_URL_HTML:
        new_uploaded_url = st.text_input("URL (html):")
    load_button = st.form_submit_button(label="Upload")
    
progress = st.empty()

# ------------------------------- App
status = st.session_state[SESSION_UPLOADED_STATUS]
if status:
    st.info(f'Uploaded {status}')
st.session_state[SESSION_UPLOADED_STATUS] = None

if not load_button:
    st.stop()

if content_type == CONTENT_FROM_FILE and not new_uploaded_files:
    progress.markdown('Please load at least one file')
    st.stop()

if content_type == CONTENT_FROM_URL_HTML and not new_uploaded_url:
    progress.markdown('Please provide URL for downloading')
    st.stop()

if content_type == CONTENT_FROM_FILE:
    progress.markdown('Saving files...')
    for file in new_uploaded_files:
        source_index.save_file(selected_document_set, file.name, file.getbuffer())
    st.session_state[SESSION_UPLOADED_STATUS] = f'Uploaded {len(new_uploaded_files)} file(s)'
    st.rerun()

if content_type == CONTENT_FROM_URL_HTML:
    progress.markdown('Fetch URL...')
    file_name_from_url = new_uploaded_url \
                                .replace('https://', '')\
                                .replace('http://', '') \
                                .replace('/', '-')\
                                .replace('\\', '-')\
                                .replace('&', '-')\
                                .replace('?', '-')\
                                .strip('-') \
                                + '.html'
    with urllib.request.urlopen(new_uploaded_url) as f:
        html = f.read()
    source_index.save_file(selected_document_set, file_name_from_url, html)
    st.session_state[SESSION_UPLOADED_STATUS] = f'Content loaded into {file_name_from_url} file. {len(html)}  bytes.'
    st.rerun()
