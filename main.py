"""
    Main APP and UI
"""
# pylint: disable=C0301,C0103,C0303

import os
import json
import pandas as pd

import streamlit as st

from strings import APP_HEADER
from utils_streamlit import streamlit_hack_remove_top_space

# ------------------------------- UI
st.set_page_config(page_title= APP_HEADER, layout="wide")
st.title(APP_HEADER)
streamlit_hack_remove_top_space()
