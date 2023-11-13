"""
    Main APP and UI
"""
# pylint: disable=C0301,C0103,C0303,C0411

import streamlit as st

from utils_streamlit import streamlit_hack_remove_top_space
from utils.doc_helper import DocHelper
from utils.app_logger import init_streamlit_logger

init_streamlit_logger()

# ------------------------------- UI
st.set_page_config(page_title= "Demo POC", layout="wide")
streamlit_hack_remove_top_space()

st.markdown(DocHelper().get_md("main"), unsafe_allow_html=False)
