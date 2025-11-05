import streamlit as st
import pandas as pd
from rdkit import Chem
from rdkit.Chem import Draw, Descriptors, Crippen, QED, Lipinski, AllChem, DataStructs
import matplotlib.pyplot as plt

st.set_page_config(page_title="Molecular Chemistry Tool", layout="wide")
st.title("🔬 Molecular Structure & Drug-Likeness Explorer")

# 🧠 Helper functions
def smiles_to_mol(smiles):
    mol = Chem.MolFromSmiles(smiles)
    if mol:
        AllChem.Compute2DCoords(mol)
    return mol

def draw_structure(mol):
    return Draw.MolToImage(mol, size=(300, 300))

def compute_properties(mol):
    return {
        "Molecular Weight": Descriptors.MolWt(mol),
        "TPSA": Descriptors.TPSA(mol),
        "XLogP": Crippen.MolLogP(mol),
        "H-Bond Donors": Lipinski.NumHDonors(mol),
        "H-Bond Acceptors": Lipinski.NumHAcceptors(mol),
        "Rotatable Bonds": Lipinski.NumRotatableBonds(mol),
        "QED": QED.qed(mol)
    }

def is_lipinski_compliant(mol):
    return (
        Descriptors.MolWt(mol) <= 500 and
        Crippen.MolLogP(mol) <= 5 and
        Lipinski.NumHDonors(mol) <= 5 and
        Lipinski.NumHAcceptors(mol) <= 10
    )

def tanimoto_similarity(mol1, mol2):
    fp1 = AllChem.GetMorganFingerprintAsBitVect(mol1, 2)
    fp2 = AllChem.GetMorganFingerprintAsBitVect(mol2, 2)
    return DataStructs.TanimotoSimilarity(fp1, fp2)

# 🧾 Sidebar Inputs
with st.sidebar:
    st.header("🔢 Input SMILES or Compound Names")
    user_input = st.text_area("Enter one SMILES string per line", "CCO\nCC(C)O\nc1ccccc1O")
    analyze_btn = st.button("Analyze Molecules")
uploaded_file = st.file_uploader("Upload your CSV", type=["csv"])
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.write("📋 Columns in uploaded CSV:", df.columns.tolist())

# 📁 Recommended single uploader (keep in sidebar or main, not both)
uploaded_file = st.sidebar.file_uploader("📁 Upload CSV with SMILES or Names", type="csv")
df = None
smiles_list = []

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.write("📋 Columns in uploaded CSV:", df.columns.tolist())

    # Handle the column gracefully
    if "smiles" in df.columns:
        smiles_list = df["smiles"].dropna().tolist()
    else:
        st.error("❌ 'smiles' column not found in uploaded CSV.")

#uploaded_file = st.sidebar.file_uploader("📁 Upload CSV with SMILES or Names", type="csv")
#if uploaded_file:
#    df = pd.read_csv(uploaded_file)
#    # Change 'smiles' to whatever your column is named
#    smiles_list = df["smiles"].dropna().tolist()
#st.write("📋 Columns in uploaded CSV:", df.columns.tolist())

# 🧪 Core Logic
if analyze_btn:
    smiles_list = [s.strip() for s in user_input.splitlines() if s.strip()]
    molecules = [smiles_to_mol(sm) for sm in smiles_list]
    valid = [(smi, mol) for smi, mol in zip(smiles_list, molecules) if mol is not None]

    if not valid:
        st.error("❌ No valid SMILES strings found.")
    else:
        data = []
        st.subheader("🖼️ Structures & Properties")
        cols = st.columns(3)

        for i, (smi, mol) in enumerate(valid):
            props = compute_properties(mol)
            lipinski = is_lipinski_compliant(mol)
            with cols[i % 3]:
                st.image(draw_structure(mol), caption=f"SMILES: {smi}")
                st.write(f"**Lipinski Compliant:** {'✅ Yes' if lipinski else '❌ No'}")
                st.dataframe(pd.DataFrame(props, index=[0]).T.rename(columns={0: "Value"}))

        # 🔁 Similarity Matrix
        st.subheader("🧬 Tanimoto Similarity Matrix")
        sim_matrix = pd.DataFrame(index=smiles_list, columns=smiles_list)
        for i in range(len(valid)):
            for j in range(len(valid)):
                sim = tanimoto_similarity(valid[i][1], valid[j][1])
                sim_matrix.iloc[i, j] = round(sim, 3)

        st.dataframe(sim_matrix)

        # 📈 Optional Heatmap
        st.markdown("**Visual Similarity (Heatmap)**")
        fig, ax = plt.subplots()
        cax = ax.matshow(sim_matrix.astype(float), cmap="Blues")
        plt.xticks(range(len(smiles_list)), smiles_list, rotation=90)
        plt.yticks(range(len(smiles_list)), smiles_list)
        fig.colorbar(cax)
        st.pyplot(fig)
        st.markdown("[ref resource](https://en.wikipedia.org/wiki/Lipinski%27s_rule_of_five)")
        st.text("thanks for using the app by Subramanian Ramajayam")