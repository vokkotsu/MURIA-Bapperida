# views/tab1_input/__init__.py
import streamlit as st
from views.tab1_input.form_manual import render_step_0, render_step_1, render_step_2
from views.tab1_input.form_import import render_step_4
from views.tab1_input.table_render import render_tables

def render_tab1():
    # Routing Langkah/Wizard
    if st.session_state.form_step == 0:
        render_step_0()
    elif st.session_state.form_step == 1:
        render_step_1()
    elif st.session_state.form_step == 2:
        render_step_2()
    elif st.session_state.form_step == 4:
        render_step_4()

    st.markdown("---")
    
    # Render semua tabel yang telah tersimpan
    render_tables()