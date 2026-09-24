import streamlit as st

st.set_page_config(
    page_title="Drone Platform",
    layout="centered"
)

# 🔐 CENTRAL CONTROLLER (ROUTER)
if "token" not in st.session_state:
    st.switch_page("pages/login_app.py")

role = st.session_state.get("role")

if role == "client":
    st.switch_page("pages/client_dashboard.py")

elif role == "operator":
    st.switch_page("pages/operator_dashboard.py")

else:
    # invalid / corrupted session
    st.session_state.clear()
    st.switch_page("pages/login_app.py")
