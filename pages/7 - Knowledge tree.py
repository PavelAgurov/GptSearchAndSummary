"""
    Knowledge tree page
"""
# pylint: disable=C0301,C0103,C0303,W0611

import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config


from utils_streamlit import streamlit_hack_remove_top_space, hide_footer
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

MODE_DRAW_EXISTED = 'Draw existed'
MODE_REBUILD      = 'Re-build'
MODE_APPEND       = 'Extend existed'
MODE_CREATE_NEW   = 'Create new'

MODE_BUILD_ALL = 'Build all'
MODE_BUILD_SELECTED = 'Selected'

# ------------------------------- UI Setup
PAGE_NAME = "Knowledge tree"
st.set_page_config(page_title= PAGE_NAME, layout="wide")
st.title(PAGE_NAME)
streamlit_hack_remove_top_space()
hide_footer()

document_set_manager.load()
selected_document_set = st.selectbox(
    label="Document set:",
    options=document_set_manager.get_all_names(),
    key="selected_document_kt"
)

input_text_files = text_extractor.get_all_source_file_names(selected_document_set, True)

file_list = st.expander(label=f'Available {len(input_text_files)} chunk(s)').empty()
text_files_str = "".join([f'{file_name}<br/>' for file_name in input_text_files])
file_list.markdown(text_files_str, unsafe_allow_html=True)

st.info('Please note - to build Knowledge Tree GPT-4 will be used.')

create_tree_mode = st.radio(label="Knowledge Tree", options=[MODE_DRAW_EXISTED, MODE_REBUILD, MODE_APPEND, MODE_CREATE_NEW], horizontal=True)

create_new_button = None
new_name = None
show_existed_button = None
existed_name = None
rebuild_button = None
build_tree_mode = None

if create_tree_mode in [MODE_DRAW_EXISTED, MODE_REBUILD, MODE_APPEND]:
    existed_name = st.selectbox(label="Existed Knowledge Tree:", options= kt_manager.get_list())

if create_tree_mode == MODE_CREATE_NEW:
    new_name  = st.text_input(label="New Knowledge Tree:")

if create_tree_mode in [MODE_CREATE_NEW, MODE_REBUILD, MODE_APPEND]:
    col_b_1, col_b_2 = st.columns([30, 80])
    build_tree_mode = col_b_1.radio(label="Build mode", options=[MODE_BUILD_ALL, MODE_BUILD_SELECTED], horizontal=True)
    if build_tree_mode == MODE_BUILD_ALL:
        max_limit = col_b_2.number_input(label="Count of files to process (0 - all):", min_value=0, max_value=len(input_text_files), value=10)
    if build_tree_mode == MODE_BUILD_SELECTED:
        selected_input = col_b_2.text_input(label="File list (separated by ';'):")

col_run_1, col_run_2 = st.columns(2)
if create_tree_mode == MODE_CREATE_NEW:
    create_new_button = col_run_1.button(label="Create")
    run_status = col_run_2.empty()

if create_tree_mode == MODE_DRAW_EXISTED:
    show_existed_button = col_run_1.button(label="Show")
    run_status = col_run_2.empty()
if create_tree_mode == MODE_REBUILD:
    rebuild_button = col_run_1.button(label="Rebuild existed")
    run_status = col_run_2.empty()
if create_tree_mode == MODE_APPEND:
    rebuild_button = col_run_1.button(label="Extend existed")
    run_status = col_run_2.empty()

status_container = st.empty()

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

    return [nodes, edges]

build_mode  = None
append_mode = False

if show_existed_button and existed_name:
    existed_knowledge_tree = kt_manager.load(existed_name)
    st.session_state[SESSION_KT] = build_agraph(existed_knowledge_tree)
    build_mode = False

kt_name_to_build = ''
if rebuild_button:
    kt_name_to_build = existed_name
    st.session_state[SESSION_KT] = None
    append_mode = (create_tree_mode == MODE_APPEND)
    build_mode = True
if create_new_button:
    kt_name_to_build = new_name
    st.session_state[SESSION_KT] = None
    build_mode = True

kt_input_files = []
if build_tree_mode == MODE_BUILD_ALL:
    if max_limit == 0:
        kt_input_files = input_text_files
    else:
        kt_input_files = input_text_files[:max_limit]
if build_tree_mode == MODE_BUILD_SELECTED:
    kt_input_files = [f.strip() for f in selected_input.strip().split(';') if len(f.strip()) > 0]

if build_mode:
    if not selected_document_set:
        status_container.markdown('Document set is required')
        st.stop()
    if not kt_name_to_build:
        status_container.markdown('Knowledge Tree name is required')
        st.stop()
    if not kt_input_files or len(kt_input_files) == 0:
        status_container.markdown('Select files for processing')
        st.stop()

    new_knowledge_tree = BackEndCore().build_knowledge_tree(
                            selected_document_set,
                            kt_name_to_build,
                            kt_input_files,
                            append_mode,
                            show_progress_callback
                    )
    st.session_state[SESSION_KT] = build_agraph(new_knowledge_tree)

tree_from_session = st.session_state[SESSION_KT]
if tree_from_session:
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
    graph = agraph(tree_from_session[0], tree_from_session[1], config)
