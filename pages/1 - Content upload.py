"""
    Upload content
"""
# pylint: disable=C0301,C0103,C0304,C0303,W0611

import requests
import streamlit as st

from utils_streamlit import streamlit_hack_remove_top_space, hide_footer
from backend_core import BackEndCore
from ui.shared_session import set_selected_document_set, get_selected_document_set_index

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

selected_document_set_data  = [''] + document_set_manager.get_all_names()
selected_document_set_index = get_selected_document_set_index(selected_document_set_data)
selected_document_set = st.selectbox(
    label="Document set:",
    options= selected_document_set_data,
    key="selected_document_set_content_upload",
    index= selected_document_set_index
)
set_selected_document_set(selected_document_set)

if not selected_document_set:
    st.stop()

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
            st.rerun()
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
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }    

    response = requests.get(new_uploaded_url, headers=headers, timeout=100)
    if response.status_code == 200:
        html = response.text
        source_index.save_file(selected_document_set, file_name_from_url, html)
        st.session_state[SESSION_UPLOADED_STATUS] = f'Content loaded into {file_name_from_url} file. {len(html)}  bytes.'
    else:
        st.session_state[SESSION_UPLOADED_STATUS] = f'Error loading content. Code: {response.status_code}.'
    st.rerun()
