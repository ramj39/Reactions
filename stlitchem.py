import streamlit as st
st.set_page_config(page_title="Chemical Reactions Dashboard", layout="centered")
st.title("💊 Chemical Dashboard")

st.title("💊 Chemical_ Dashboard")
# Dictionary with display names and their respective URLs
apps = {
    #"pages/streamlit_chemical_reactions.py": "http://localhost:8501",
    #"pages/Streamlit_organic_rxns.py": "http://localhost:8502",
    "pages/Reactions/streamlit_chemical_reactions.py at main.ramj39/Reactions"
    "pages/Reactions/streamlit_organic_rxns.py at main.ramj39/Reactions",

    
}

st.write("Click a button below to open an app (make sure each app is running on its own port):")

# Render buttons for each app
for app_label, url in apps.items():
    if st.button(f"Launch {app_label}"):
        st.markdown(f'<meta http-equiv="refresh" content="0; url={url}">', unsafe_allow_html=True)

st.info("Developed by Subramanian Ramajayam")
