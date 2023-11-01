"""
    Extract plain text page as set of pages
"""
# pylint: disable=C0301,C0103,C0304,C0303,W0611

import streamlit as st

from utils_streamlit import streamlit_hack_remove_top_space, hide_footer
from backend_core import BackEndCore, BackendTextExtractionParams
from ui.shared_session import set_selected_document_set, get_selected_document_set_index

# ------------------------------- Core

source_index = BackEndCore.get_source_storage()
text_extractor = BackEndCore.get_text_extractor()
document_set_manager = BackEndCore.get_document_set_manager()

# ------------------------------- UI Setup
PAGE_NAME = "Extract plain text as set of pages"
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
    key="selected_document_set_extract",
    index= selected_document_set_index
)
set_selected_document_set(selected_document_set)

if not selected_document_set:
    st.stop()

uploaded_files = source_index.get_all_files(selected_document_set, True)

file_list = st.expander(label=f"Available {len(uploaded_files)} source file(s)").empty()

uploaded_files_str = "".join([f'{file_name}<br/>' for file_name in uploaded_files])
file_list.markdown(uploaded_files_str, unsafe_allow_html=True)

text_files = text_extractor.get_all_source_file_names(selected_document_set, True)

override_all = st.checkbox(label="Override all")
text_files_count = len(text_files)
if text_files_count > 0:
    pages_message = f'There are already {text_files_count} pages for selected document set.'
else:
    pages_message = 'There are no pages yet for selected document set.'
if override_all:
    pages_message+= ' They will be re-created.'
st.info(pages_message)

run_html_llm_formatter = st.checkbox(label="Format text into HTML with LLM")
run_table_extraction   = st.checkbox(label="Extract tables")

col_f1, col_f2 = st.columns([10, 40])
col_f1.markdown('<br/>', unsafe_allow_html=True) # need to center checkbox
store_as_facts_list = col_f1.checkbox(label="Store as fact list")
fact_context        = col_f2.text_input(label="Context of facts:", disabled= not store_as_facts_list)

if run_table_extraction:
    st.info('Tables will be extracted from formatted documents if they were created.')

extraction_log = st.expander(label="Log").empty()

progress = st.empty()

def show_progress_callback(progress_str : str):
    """Show progress/status"""
    progress.markdown(progress_str)


if not uploaded_files:
    progress.markdown('Please load at least one file')
    st.stop()

run_button = st.button(label="Run extraction")
if not run_button:
    st.stop()

if store_as_facts_list and not fact_context:
    progress.markdown('Context is requred for fact extractor')
    st.stop()

progress.markdown('Start converting...')
extraction_result = BackEndCore().run_text_extraction(
    selected_document_set,
    BackendTextExtractionParams(
        override_all,
        run_html_llm_formatter,
        run_table_extraction,
        store_as_facts_list,
        fact_context,
        show_progress_callback
    )
)
progress.markdown('Done')

extraction_result_str = '<br/>'.join(extraction_result)
extraction_log.markdown(extraction_result_str, unsafe_allow_html= True)
