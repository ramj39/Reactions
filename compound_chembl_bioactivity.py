import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="ChEMBL Bioactivity Explorer", layout="wide")
st.title("🧬 ChEMBL Bioactivity Explorer (with Target Info)")

# 🔍 Resolve compound name to ChEMBL ID
def get_chembl_id(compound_name):
    url = f"https://www.ebi.ac.uk/chembl/api/data/molecule/search.json?q={compound_name}"
    r = requests.get(url)
    if r.status_code == 200:
        data = r.json()
        molecules = data.get("molecules", [])
        if molecules:
            return molecules[0]["molecule_chembl_id"]
    return None

# 🌐 Get target name and organism
def get_target_info(target_id):
    url = f"https://www.ebi.ac.uk/chembl/api/data/target/{target_id}.json"
    r = requests.get(url)
    if r.status_code == 200:
        info = r.json()
        return {
            "Target Name": info.get("pref_name", "N/A"),
            "Organism": info.get("organism", "N/A"),
            "Target Type": info.get("target_type", "N/A")
        }
    return {"Target Name": "N/A", "Organism": "N/A", "Target Type": "N/A"}

# 🌐 Fetch bioactivity data with target enrichment
def get_bioactivity_data(chembl_id, max_results=50):
    url = f"https://www.ebi.ac.uk/chembl/api/data/activity.json?molecule_chembl_id={chembl_id}&limit={max_results}"
    r = requests.get(url)
    results = []
    if r.status_code == 200:
        for act in r.json().get("activities", []):
            tgt_id = act.get("target_chembl_id")
            tgt_info = get_target_info(tgt_id) if tgt_id else {}
            results.append({
                "Target Name": tgt_info.get("Target Name"),
                "Organism": tgt_info.get("Organism"),
                "Target Type": tgt_info.get("Target Type"),
                "Assay ChEMBL ID": act.get("assay_chembl_id"),
                "Target ChEMBL ID": tgt_id,
                "Type": act.get("standard_type"),
                "Value": act.get("standard_value"),
                "Units": act.get("standard_units"),
                "Relation": act.get("standard_relation"),
                "Activity Comment": act.get("activity_comment"),
                "Assay Description": act.get("assay_description")
            })
    return results

# 🧪 Sidebar input
with st.sidebar:
    st.header("🔬 ChEMBL Bioactivity Search")
    compound_name = st.text_input("Enter compound name", "aspirin")
    max_results = st.slider("Max results", 10, 100, 50)
    search_button = st.button("Search ChEMBL")

# 🚀 Main logic
if search_button:
    chembl_id = get_chembl_id(compound_name)
    if not chembl_id:
        st.error(f"❌ Could not find ChEMBL ID for '{compound_name}'")
    else:
        st.success(f"✅ Found ChEMBL ID: {chembl_id}")
        with st.spinner("Fetching bioactivity data..."):
            data = get_bioactivity_data(chembl_id, max_results)

        if data:
            df = pd.DataFrame(data)
            st.subheader("📋 Bioactivity Data (with Target Info)")
            st.dataframe(df)
            st.download_button("📥 Download CSV", df.to_csv(index=False), file_name=f"{compound_name}_chembl_bioactivity.csv", mime="text/csv")
        else:
            st.warning("No bioactivity data found in ChEMBL.")
