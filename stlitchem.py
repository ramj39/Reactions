import streamlit as st
st.set_page_config(page_title="Chemical Reactions Dashboard", layout="centered")
st.title("💊 Chemical Dashboard")

st.title("💊 Chemical_ Dashboard")
# Dictionary with display names and their respective URLs
apps = {
    "streamlit_organic_ rxns.py":"https://app1.example.com",
    "streamlit_chemical_ reactions.py":"https://app2.example.com",
    
}

for app_label, url in apps.items():
    if st.button(f"Launch {app_label}"):
        st.experimental_set_query_params()  # example action
        st.write(f"Launching {app_label} at {url}")
        # Or use st.markdown with a link, or st.write with an anchor tag

}

st.write("Click a button below to open an app (make sure each app is running on its own port):")

# Render buttons for each app
for app_label, url in apps.items():
    if st.button(f"Launch {app_label}"):
       st.link_button(f"Launch {app_label}", url)
 
#st.markdown(f'<meta http -equiv="refresh" content="0; url={url}">', unsafe_allow_html=True)

st.info("Developed by Subramanian Ramajayam")
