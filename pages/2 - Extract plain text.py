"""
    Extract plain text page
"""
# pylint: disable=C0301,C0103,C0304,C0303,W0611

import streamlit as st

from utils_streamlit import streamlit_hack_remove_top_space, hide_footer
from backend_core import BackEndCore, BackendTextExtractionParams

# ------------------------------- Core

source_index = BackEndCore.get_source_storage()
text_extractor = BackEndCore.get_text_extractor()
document_set_manager = BackEndCore.get_document_set_manager()

# ------------------------------- UI Setup
PAGE_NAME = "Extract plain text"
st.set_page_config(page_title= PAGE_NAME, layout="wide")
st.title(PAGE_NAME)
streamlit_hack_remove_top_space()
hide_footer()

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

text_files = text_extractor.get_all_source_file_names(selected_document_set, True)

override_all = st.checkbox(label="Override all")
if override_all:
    st.info(f'There are {len(text_files)} chunks for selected document set. They will be re-created.')
else:
    st.info(f'There are {len(text_files)} chunks for selected document set.')
run_llm_formatter = st.checkbox(label="Pre-processing: format documents with LLM")
run_table_extraction = st.checkbox(label="Extract tables")
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

progress.markdown('Start converting...')
extraction_result = BackEndCore().run_text_extraction(
    selected_document_set,
    BackendTextExtractionParams(
        override_all,
        run_llm_formatter,
        run_table_extraction,
        show_progress_callback
    )
)
progress.markdown('Done')

extraction_result_str = '<br/>'.join(extraction_result)
extraction_log.markdown(extraction_result_str, unsafe_allow_html= True)
