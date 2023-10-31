"""
    Shared session for streamlit
"""

import streamlit as st

SESSION_SELECTED_DOCUMENT_SET = 'saved_selected_document_set'

def set_selected_document_set(selected_document_set : str):
    """Set selected document set"""
    st.session_state[SESSION_SELECTED_DOCUMENT_SET] = selected_document_set

def get_selected_document_set_index(selected_document_set_list : list[str])-> int:
    """Find index of saved selected document str"""
    if SESSION_SELECTED_DOCUMENT_SET not in st.session_state:
        st.session_state[SESSION_SELECTED_DOCUMENT_SET] = None
    saved_selected_document_set = st.session_state[SESSION_SELECTED_DOCUMENT_SET]
    selected_document_set_index = 0
    if saved_selected_document_set:
        if saved_selected_document_set in selected_document_set_list:
            selected_document_set_index = selected_document_set_list.index(saved_selected_document_set)
    return selected_document_set_index
