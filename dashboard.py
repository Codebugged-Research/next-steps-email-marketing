import streamlit as st
import pandas as pd
from tracker import send_mail_and_record, get_all_events

st.set_page_config(page_title="NextSteps USMLE Email Marketing", layout="wide")
st.title("NextSteps USMLE Email Marketing Platform")

page = st.sidebar.selectbox("Navigation", ["Send Emails", "Deliverability Dashboard"])

if page == "Send Emails":
    st.subheader("Send Email Campaign")
    subject = st.text_input("Subject")
    from_email = st.text_input("From Email (verified in SES)")
    body = st.text_area("Email Body (HTML allowed)", height=250)
    file = st.file_uploader("Upload CSV with 'email' column", type=["csv"])

    if file:
        df = pd.read_csv(file)
        if st.button("Send Emails"):
            for _, row in df.iterrows():
                send_mail_and_record(row["email"], subject, body, from_email)
            st.success("Emails sent successfully")

if page == "Deliverability Dashboard":
    st.subheader("Email Performance Overview")

    if st.button("Refresh Data"):
        st.session_state["events"] = get_all_events()

    if "events" not in st.session_state:
        st.info("Click Refresh Data to load metrics.")
        st.stop()

    items = st.session_state["events"]

    if not items:
        st.info("No email events found.")
        st.stop()

    total_sent = sum(int(i.get("sent", 0)) for i in items)
    delivered = sum(int(i.get("delivered", 0)) for i in items)
    opened = sum(1 for i in items if int(i.get("opened", 0)) > 0)
    clicked = sum(1 for i in items if int(i.get("clicked", 0)) > 0)
    complaints = sum(int(i.get("complaint", 0)) for i in items)
    permanent_bounces = sum(1 for i in items if str(i.get("bounce", "")).lower() == "permanent")
    transient_bounces = sum(1 for i in items if str(i.get("bounce", "")).lower() == "transient")

    def pct(a, b):
        return round((a / b * 100), 2) if b else 0

    c1, c2, c3 = st.columns(3)
    c4, c5, c6 = st.columns(3)

    c1.metric("Delivery Rate", f"{pct(delivered, total_sent)}%", f"{delivered}/{total_sent}")
    c2.metric("Open Rate", f"{pct(opened, delivered)}%", f"{opened}/{delivered}")
    c3.metric("Click Rate", f"{pct(clicked, delivered)}%", f"{clicked}/{delivered}")
    c4.metric("Permanent Bounces", f"{pct(permanent_bounces, total_sent)}%", permanent_bounces)
    c5.metric("Transient Bounces", f"{pct(transient_bounces, total_sent)}%", transient_bounces)
    c6.metric("Complaints", f"{pct(complaints, delivered)}%", complaints)

    st.markdown("Detailed Email Event Log")
    st.dataframe(pd.DataFrame(items))
