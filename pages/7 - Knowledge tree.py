"""
    Knowledge tree page
"""
# pylint: disable=C0301,C0103,C0303,W0611

import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config


from utils_streamlit import streamlit_hack_remove_top_space
from backend_core import BackEndCore
from core.kt_manager import KnowledgeTree

# ------------------------------- Core

document_set_manager = BackEndCore.get_document_set_manager()
text_extractor = BackEndCore.get_text_extractor()
kt_manager = BackEndCore.get_knowledge_tree_manager()

# ------------------------------- Session

SESSION_KT = 'ktree'
if SESSION_KT not in st.session_state:
    st.session_state[SESSION_KT] = None
# ------------------------------- Consts

MODE_CREATE_NEW = 'Create new'
MODE_EXISTED = 'Existed'

# ------------------------------- UI Setup
PAGE_NAME = "Knowledge tree"
st.set_page_config(page_title= PAGE_NAME, layout="wide")
st.title(PAGE_NAME)
streamlit_hack_remove_top_space()

document_set_manager.load()
selected_document_set = st.selectbox(
    label="Data set:",
    options=document_set_manager.get_all_names(),
    key="selected_document_kt"
)

text_files = text_extractor.get_all_source_files(selected_document_set, True)

file_list = st.expander(label=f'Available {len(text_files)} chunk(s)').empty()
text_files_str = "".join([f'{file_name}<br/>' for file_name in text_files])
file_list.markdown(text_files_str, unsafe_allow_html=True)

st.info('Please note - to build Knowledge Tree GPT-4 will be used.')

create_tree_mode = st.radio(label="Knowledge Tree", options=[MODE_EXISTED, MODE_CREATE_NEW], horizontal=True)

create_new_button = None
new_name = None
if create_tree_mode == MODE_CREATE_NEW:
    col_crn_1, col_crn_2 = st.columns(2)
    new_name  = col_crn_1.text_input(label="Name")
    max_limit = col_crn_2.number_input(label="Count of files to process (0 - all):", min_value=0, max_value=len(text_files), value=10)
    col_run_1, col_run_2 = st.columns(2)
    create_new_button = col_run_1.button(label="Create")
    run_status = col_run_2.empty()

show_existed_button = None
existed_name = None
if create_tree_mode == MODE_EXISTED:
    existed_name = st.selectbox(label="Existed Knowledge Tree", options= kt_manager.get_list())
    show_existed_button = st.button(label="Show")

def show_progress_callback(progress_str : str):
    """Show progress/status"""
    run_status.markdown(progress_str)

def build_agraph(knowledge_tree : KnowledgeTree):
    """Build agraph and save into session"""
    nodes = []
    nodes_list = []
    edges = []
    for knowledge_item in knowledge_tree.triples:
        if knowledge_item.subject not in nodes_list:
            nodes.append(Node(
                id= knowledge_item.subject,
                size= 10,
                color= "red",
                label= knowledge_item.subject[:10]
            ))
            nodes_list.append(knowledge_item.subject)
        for knowledge_obj in knowledge_item.objects:
            if knowledge_obj not in nodes_list:
                nodes.append(Node(
                    id= knowledge_obj, 
                    size= 10,
                    label= knowledge_obj[:10]
                ))
                nodes_list.append(knowledge_obj)
            edges.append(Edge(
                source=knowledge_item.subject, 
                target=knowledge_obj, 
                type="CURVE_SMOOTH", 
                label= knowledge_item.predicate[:10]
            ))

    st.session_state[SESSION_KT] = [nodes, edges]

if create_new_button and new_name:
    new_knowledge_tree = BackEndCore().build_knowledge_tree(
                            new_name,
                            selected_document_set,
                            max_limit,
                            show_progress_callback
                    )
    build_agraph(new_knowledge_tree)


if show_existed_button and existed_name:
    existed_knowledge_tree = kt_manager.load(existed_name)
    build_agraph(existed_knowledge_tree)

saved_tree = st.session_state[SESSION_KT]
if saved_tree:
    config = Config(
            height=500,
            width=1000, 
            nodeHighlightBehavior=False,
            highlightColor="#F7A7A6", 
            directed=True, 
            collapsible=True,
            hierarchical=True, 
            physics=False
    )
    graph = agraph(saved_tree[0], saved_tree[1], config)
