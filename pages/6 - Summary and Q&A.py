"""
    Summary page
"""
# pylint: disable=C0301,C0103,C0303,W0611

import streamlit as st
from utils_streamlit import streamlit_hack_remove_top_space

PAGE_NAME = "Summary and Q&A"

# ------------------------------- UI Setup
st.set_page_config(page_title= PAGE_NAME, layout="wide")
st.title(PAGE_NAME)
streamlit_hack_remove_top_space()
