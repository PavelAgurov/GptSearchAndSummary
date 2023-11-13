"""
    Tables page
"""
# pylint: disable=C0301,C0103,C0303,W0611,C0305

import streamlit as st


from utils_streamlit import streamlit_hack_remove_top_space, hide_footer
from backend_core import BackEndCore
from ui.shared_session import set_selected_document_set, get_selected_document_set_index
from utils.app_logger import init_streamlit_logger

# ------------------------------- Core

document_set_manager = BackEndCore.get_document_set_manager()
text_extractor = BackEndCore.get_text_extractor()
table_extractor = BackEndCore.get_table_extractor()

init_streamlit_logger()
# ------------------------------- UI Setup
PAGE_NAME = "Tables"
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
    key="selected_document_tables",
    index= selected_document_set_index
)
set_selected_document_set(selected_document_set)

if not selected_document_set:
    st.stop()

table_files = text_extractor.get_table_file_list(selected_document_set, True)
selected_table_file = st.selectbox(label="Table(s) file:", options=table_files)

if not selected_table_file:
    st.stop()

table_extractor_result = BackEndCore().get_tables_from_file(selected_document_set, selected_table_file)
if table_extractor_result.error:
    st.error(table_extractor_result.error)
    st.stop()

table_names = [t.table_name for t in table_extractor_result.table_list]
selected_table_name = st.selectbox(label="Table(s):", options=table_names)

selected_table_data = [t.table_data for t in table_extractor_result.table_list if t.table_name == selected_table_name][0]

st.dataframe(selected_table_data, use_container_width=True, hide_index=True)
