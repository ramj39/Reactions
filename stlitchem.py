import streamlit as st

st.set_page_config(page_title="Chemical Reactions Dashboard", layout="centered")
st.title("💊 Chemical Dashboard")

# ✅ This is a dictionary, not a set
apps = {
    "Organic Reactions": "https://your-username-organic-rxns.streamlit.app",
    "Chemical Reactions": "https://your-username-chemical-reactions.streamlit.app",
    "ChEMBL Bioactivity": "https://your-username-chembl-bioactivity.streamlit.app",
    "Chemical Tools": "https://your-username-chem-tool.streamlit.app",
}

st.write("Click a button below to open an app (make sure each app is deployed and accessible):")

for app_label, url in apps.items():
    if st.button(f"Launch {app_label}", key=f"btn_{app_label}"):
        st.success(f"{app_label} is ready to launch!")
        st.markdown(f"[Click here to open {app_label}]({url})", unsafe_allow_html=True)

st.info("Developed by Subramanian Ramajayam")
