"""
    Summary page
"""
# pylint: disable=C0301,C0103,C0303,W0611

import streamlit as st
from utils_streamlit import streamlit_hack_remove_top_space, hide_footer

from backend_core import BackEndCore
from ui.dialog_storage import DialogStorage, DialogRole

# ------------------------------- Session

SESSION_DIALOG_STORAGE = 'dialog_storage'
if SESSION_DIALOG_STORAGE not in st.session_state:
    st.session_state[SESSION_DIALOG_STORAGE] = DialogStorage()
dialog_storage = st.session_state[SESSION_DIALOG_STORAGE]

# ------------------------------- Core

document_set_manager = BackEndCore.get_document_set_manager()

# ------------------------------- UI Setup
PAGE_NAME = "Summary and Q&A"
st.set_page_config(page_title= PAGE_NAME, layout="wide")
st.title(PAGE_NAME)
streamlit_hack_remove_top_space()
hide_footer()

document_set_manager.load()
selected_document_set = st.selectbox(
    label="Document set:",
    options=document_set_manager.get_all_names(),
    key="selected_document_set_summary"
)

# selected_topic = st.selectbox(
#     label="Topic:",
#     options= topic_manager.get_topic_list(),
#     key="topic_to_edit"
# )

prompt = st.chat_input("Your question")
if prompt:
    dialog_storage.add_message(DialogRole.USER, prompt)
    assistant_message = "LLM answer" #back_end_core.get_answer()
    dialog_storage.add_message(DialogRole.ASSISTANT, assistant_message)

dialog_items = dialog_storage.get_message_list()
for dialog_item in dialog_items:
    with st.chat_message(dialog_item.role):
        st.write(dialog_item.msg)
