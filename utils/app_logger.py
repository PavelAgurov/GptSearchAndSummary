"""
    Custom logger for application
"""
# pylint: disable=C0301,C0103,C0303,C0304,C0305,C0411,E1121

import os
import logging
from datetime import datetime

import streamlit as st

from utils.colored_console_formatter import ColoredConsoleFormatter

LOG_FOLDER = '.logs'

def init_streamlit_logger():
    """Init logger for streamlit"""
    SESSION_LOGGER   = 'logger'
    if SESSION_LOGGER not in st.session_state:
        st.session_state[SESSION_LOGGER] = None

    logger : logging.Logger = st.session_state[SESSION_LOGGER]
    if not logger:
        logger = init_root_logger()
        st.session_state[SESSION_LOGGER] = logger


def init_root_logger():
    """Init root logger"""

    logger = logging.getLogger()
    logger.handlers.clear()
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(ColoredConsoleFormatter())
    logger.addHandler(stream_handler)
    os.makedirs(LOG_FOLDER, exist_ok=True)
    file_handler = logging.FileHandler(rf'{LOG_FOLDER}\log{datetime.now().strftime("%Y-%m-%d")}.log')
    logger.addHandler(file_handler)
    logger.setLevel(logging.DEBUG)

    return logger
