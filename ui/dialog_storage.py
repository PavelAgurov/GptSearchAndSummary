""""
    Dialog storage
"""

# pylint: disable=C0301,C0103,C0303,C0411

import enum
from datetime import datetime
from dataclasses import dataclass
import streamlit as st

class DialogRole(enum.StrEnum):
    """Role enum"""
    USER = 'user'
    ASSISTANT = 'assistant'

@dataclass
class DialogItem:
    """Dialog item"""
    created : datetime
    role    : DialogRole
    msg     : str


class DialogStorage:
    """Class dialog storage"""

    __SESSION_DIALOG_ITEMS = 'dialog_items'

    def __init__(self) -> None:
        if self.__SESSION_DIALOG_ITEMS not in st.session_state:
            st.session_state[self.__SESSION_DIALOG_ITEMS] = []

    def add_message(self, role: DialogRole, msg : str) -> None:
        """Add message"""
        dialog_items : list[DialogItem] = st.session_state[self.__SESSION_DIALOG_ITEMS]
        dialog_items.append(DialogItem(datetime.now(), role, msg))
        st.session_state[self.__SESSION_DIALOG_ITEMS] = dialog_items

    def get_message_list(self) -> list[DialogItem]:
        """Get all stored messages"""
        return st.session_state[self.__SESSION_DIALOG_ITEMS]