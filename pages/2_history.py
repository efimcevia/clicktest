import streamlit as st
from app import ui,state, logic

state.init_state()
ui.history_render()