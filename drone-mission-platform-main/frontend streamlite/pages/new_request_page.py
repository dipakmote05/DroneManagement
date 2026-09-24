import streamlit as st
import requests

API = "http://127.0.0.1:5000/api"

st.set_page_config(
    page_title="Create Drone Request",
    layout="centered"
)

# -------------------------
# 🔐 CLIENT GUARD
# -------------------------
if "token" not in st.session_state or st.session_state.get("role") != "client":
    st.session_state.clear()
    st.switch_page("pages/login_app.py")

token = st.session_state.token

st.title("➕ Create Drone Request")

# -------------------------
# LOAD OPERATORS
# -------------------------
@st.cache_data(show_spinner=False)
def load_operators(token):
    try:
        res = requests.get(
            API + "/users/operators",
            headers={"Authorization": f"Bearer {token}"}
        )
        return res.json()
    except Exception:
        return []


operators = load_operators(token)

operator_options = {
    f"{op['name']} ({op['email']})": op["id"]
    for op in operators
}

# -------------------------
# FORM
# -------------------------
with st.form("request_form"):
    service = st.selectbox(
        "Select Service",
        ["", "mapping", "surveillance", "healthcare"]
    )

    lat = st.text_input("Latitude")
    lng = st.text_input("Longitude")

    operator_label = st.selectbox(
        "Select Operator",
        [""] + list(operator_options.keys())
    )

    submit = st.form_submit_button("Send Request 🚀")

# -------------------------
# SUBMIT LOGIC
# -------------------------
if submit:
    if not service or not lat or not lng or not operator_label:
        st.error("All fields including operator selection are required")

    else:
        payload = {
            "service_type": service,
            "lat": lat,
            "lng": lng,
            "operator_id": operator_options[operator_label]
        }

        with st.spinner("Sending request..."):
            try:
                res = requests.post(
                    API + "/orders/create",
                    json=payload,
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {token}"
                    }
                ).json()
            except Exception:
                st.error("Request failed")
                st.stop()

        if "error" in res:
            st.error(res["error"])
        else:
            st.success(res.get("message", "Request created successfully ✅"))

            # 🔁 Redirect to Track page
            st.switch_page("pages/track_drone.py")


# -------------------------
# BACK BUTTON
# -------------------------
st.markdown("---")
if st.button("⬅️ Back to Dashboard"):
    st.switch_page("pages/client_dashboard.py")
