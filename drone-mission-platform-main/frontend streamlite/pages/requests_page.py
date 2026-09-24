import streamlit as st
import requests

API = "http://127.0.0.1:5000/api/orders"

st.set_page_config(
    page_title="Pending Requests",
    layout="centered"
)

# -------------------------
# 🔐 OPERATOR GUARD
# -------------------------
if "token" not in st.session_state or st.session_state.get("role") != "operator":
    st.session_state.clear()
    st.switch_page("pages/login_app.py")

token = st.session_state.token

st.title("📋 Pending Requests")

# -------------------------
# NAV BUTTON
# -------------------------
if st.button("⬅️ Back to Dashboard"):
    st.switch_page("pages/operator_dashboard.py")

st.markdown("---")

# -------------------------
# LOAD REQUESTS
# -------------------------
def load_requests():
    try:
        res = requests.get(
            API + "/pending",
            headers={"Authorization": f"Bearer {token}"}
        )
        return res.json()
    except Exception:
        st.error("Failed to load requests")
        return []


# -------------------------
# ACTIONS
# -------------------------
def accept_request(order_id):
    requests.post(
        API + f"/accept/{order_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    st.success(f"Order {order_id} accepted ✅")
    st.rerun()


def reject_request(order_id):
    requests.post(
        API + f"/reject/{order_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    st.warning(f"Order {order_id} rejected ❌")
    st.rerun()


# -------------------------
# UI RENDER
# -------------------------
orders = load_requests()

if not orders:
    st.info("No pending requests")
else:
    for o in orders:
        with st.container():
            st.markdown(
                """
                <div style="
                    background:white;
                    color:#020617;
                    padding:20px;
                    margin:15px auto;
                    width:420px;
                    border-radius:12px;
                    box-shadow:0 10px 25px rgba(0,0,0,0.25);
                ">
                """,
                unsafe_allow_html=True
            )

            st.markdown(f"**Order ID:** {o['order_id']}")
            st.markdown(f"**Service:** {o['service']}")
            st.markdown(f"**Location:** {o['lat']}, {o['lng']}")

            col1, col2 = st.columns(2)

            with col1:
                if st.button("Accept ✅", key=f"accept_{o['order_id']}"):
                    accept_request(o["order_id"])

            with col2:
                if st.button("Reject ❌", key=f"reject_{o['order_id']}"):
                    reject_request(o["order_id"])

            st.markdown("</div>", unsafe_allow_html=True)
