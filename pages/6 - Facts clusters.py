"""
    Fact page
"""
# pylint: disable=C0301,C0103,C0303,W0611

import pandas as pd
import streamlit as st
from utils_streamlit import streamlit_hack_remove_top_space, hide_footer

from backend_core import BackEndCore
from ui.shared_session import set_selected_document_set, get_selected_document_set_index
from utils.app_logger import init_streamlit_logger

# ------------------------------- Core

document_set_manager = BackEndCore.get_document_set_manager()
text_extractor = BackEndCore.get_text_extractor()
embedding_manager = BackEndCore.get_embedding_manager()

init_streamlit_logger()
# ------------------------------- UI Setup
PAGE_NAME = "Fact page"
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
    key="selected_document_facts",
    index= selected_document_set_index
)
set_selected_document_set(selected_document_set)

embedding_item = st.selectbox(
    "Select embedding:",
    key="embedding_name",
    options= embedding_manager.get_embedding_information_list(),
    index=0
)

st.info(f'{embedding_item.description}.')

cluster_count = st.number_input(label="Combine into clusters", min_value=2, max_value=100, value= 4)

run_button = st.button(label="Show")

if not selected_document_set or not run_button:
    st.stop()

cluster_list = BackEndCore().get_fact_clusters(selected_document_set, cluster_count, embedding_item)
for cluster in cluster_list:
    data = {'Fact': cluster.fact_list}
    df = pd.DataFrame(data)
    df = df.applymap(lambda x: x.replace('\n', '<br>'))
    fact_expander = st.expander(label= cluster.name, expanded=False)
    fact_expander.markdown(df.to_html(escape=False, index=False, header=False), unsafe_allow_html=True)
    fact_expander.markdown('\n')


