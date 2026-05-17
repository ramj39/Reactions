import streamlit as st
from rdkit import Chem
from rdkit.Chem import Draw, AllChem
from rdkit.Chem.Draw import MolDraw2DCairo
import io
from PIL import Image

# Set page configuration
st.set_page_config(
    page_title="Organic Chemistry Reaction Visualizer",
    page_icon="🧪",
    layout="wide"
)

# Custom CSS for styling
st.markdown("""<style>
    .main-header {
        font-size: 2.5rem;
        color: #2E86AB;
        text-align: center;
        margin-bottom: 2rem;
    }
    .reaction-section {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .compound-card {
        background-color: white;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 10px 0;
    }
</style>""", unsafe_allow_html=True)

def mol_to_image(mol, width=300, height=200):
    """Convert RDKit molecule to PIL Image"""
    if mol is None:
        return None
    drawer = MolDraw2DCairo(width, height)
    drawer.DrawMolecule(mol)
    drawer.FinishDrawing()
    png_data = drawer.GetDrawingText()
    return Image.open(io.BytesIO(png_data))

def display_compound(comp_name, smiles, description=""):
    """Display compound with name, structure, and description"""
    mol = Chem.MolFromSmiles(smiles)
    if mol:
        img = mol_to_image(mol)
        col1, col2 = st.columns([1, 2])
        with col1:
            st.image(img, caption=comp_name, use_column_width=True)
        with col2:
            st.write(f"{comp_name}")
            st.write(f"SMILES: {smiles}")
            if description:
                st.write(description)
    else:
        st.error(f"Invalid SMILES for {comp_name}: {smiles}")

def main():
    st.markdown('<h1 class="main-header">🧪 Organic Chemistry Reaction Visualizer</h1>', unsafe_allow_html=True)
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    reaction_type = st.sidebar.selectbox(
        "Select Reaction Type",
        ["Oxidation", "Reduction", "Rearrangement", "Substitution", "Elimination", "Addition"]
    )
    
    # Compound A input
    st.sidebar.header("Compound A Input")
    custom_mode = st.sidebar.checkbox("Use custom compound")
    
    if custom_mode:
        compound_a_smiles = st.sidebar.text_input("Enter SMILES for Compound A", "CCO")
        compound_a_name = st.sidebar.text_input("Compound A Name", "Ethanol")
    else:
        predefined_compounds = {
            "Ethanol": "CCO",
            "Methanol": "CO",
            "Acetaldehyde": "CC=O",
            "Acetic Acid": "CC(=O)O",
            "Cyclohexanol": "C1CCC(CC1)O",
            "Benzaldehyde": "c1ccc(cc1)C=O",
            "2-Propanol": "CC(O)C",
            "1-Butanol": "CCCCO"
        }
        selected_compound = st.sidebar.selectbox("Select Compound A", list(predefined_compounds.keys()))
        compound_a_name = selected_compound
        compound_a_smiles = predefined_compounds[selected_compound]
    
    # Main content area
    st.header(f"{reaction_type} Reactions")
    st.subheader("Starting Compound")
    display_compound(compound_a_name, compound_a_smiles)
    
    # Call relevant functions based on reaction type
    if reaction_type == "Oxidation":
        show_oxidation_reactions(compound_a_name, compound_a_smiles)
    elif reaction_type == "Reduction":
        show_reduction_reactions(compound_a_name, compound_a_smiles)
    elif reaction_type == "Rearrangement":
        show_rearrangement_reactions(compound_a_name, compound_a_smiles)
    elif reaction_type == "Substitution":
        show_substitution_reactions(compound_a_name, compound_a_smiles)
    elif reaction_type == "Elimination":
        show_elimination_reactions(compound_a_name, compound_a_smiles)
    elif reaction_type == "Addition":
        show_addition_reactions(compound_a_name, compound_a_smiles)

# Example corrected function for oxidation reactions
def show_oxidation_reactions(compound_name, smiles):
    """Display oxidation reactions with proper data structure"""
    st.markdown('<div class="reaction-section">', unsafe_allow_html=True)
    oxidation_reactions = {
        "Alcohol to Aldehyde": {
            "reactant_smiles": "CCO",
            "product_smiles": "CC=O",
            "reagents": "PCC, CrO₃, or KMnO₄",
            "conditions": "Mild oxidation, anhydrous conditions",
            "description": "Oxidation of primary alcohols to aldehydes"
        },
        "Alcohol to Carboxylic Acid": {
            "reactant_smiles": "CCO",
            "product_smiles": "C(=O)O",
            "reagents": "KMnO₄, K₂Cr₂O₇/H₂SO₄",
            "conditions": "Strong oxidation, acidic conditions",
            "description": "Oxidation of primary alcohols to acids"
        },
        "Aldehyde to Carboxylic Acid": {
            "reactant_smiles": "CC=O",
            "product_smiles": "CC(=O)O",
            "reagents": "Tollens' reagent, KMnO₄",
            "conditions": "Mild conditions",
            "description": "Oxidation of aldehydes to acids"
        }
    }
    # Use the molecule to identify applicable reactions
    mol = Chem.MolFromSmiles(smiles)
    if mol:
        # Example check for alcohol or aldehyde
        alcohol_pattern = Chem.MolFromSmarts("[OX2H]")
        aldehyde_pattern = Chem.MolFromSmarts("[CX3H1](=O)[#6]")
        if mol.HasSubstructMatch(alcohol_pattern):
            show_reaction_example("Alcohol to Aldehyde", oxidation_reactions["Alcohol to Aldehyde"], compound_name, smiles)
            show_reaction_example("Alcohol to Carboxylic Acid", oxidation_reactions["Alcohol to Carboxylic Acid"], compound_name, smiles)
        elif mol.HasSubstructMatch(aldehyde_pattern):
            show_reaction_example("Aldehyde to Carboxylic Acid", oxidation_reactions["Aldehyde to Carboxylic Acid"], compound_name, smiles)
        else:
            st.info("Try compounds like ethanol (CCO) or acetaldehyde (CC=O) for oxidation examples")
    st.markdown('</div>', unsafe_allow_html=True)

# Similar structure for other reaction types
# Define each show_*_reactions with proper data and calls to display_compound

# Run the app
if __name__ == "__main__":
    main()
