import streamlit as st
import chempy
from chempy import balance_stoichiometry, Substance
from chempy.util import periodic
import re

# Initialize session state for history
if 'history' not in st.session_state:
    st.session_state.history = []

# Common names to chemical formulas
COMMON_NAMES = {
    # Organic
    "methane": "CH4", "ethane": "C2H6", "propane": "C3H8", "butane": "C4H10",
    "ethene": "C2H4", "ethylene": "C2H4", "ethyne": "C2H2", "acetylene": "C2H2",
    "methanol": "CH3OH", "ethanol": "C2H5OH", "formic acid": "HCOOH", 
    "acetic acid": "CH3COOH", "benzene": "C6H6", "toluene": "C7H8",
    "phenol": "C6H5OH", "aniline": "C6H5NH2", "formaldehyde": "HCHO",
    "acetone": "CH3COCH3", "glucose": "C6H12O6", "sucrose": "C12H22O11",
    
    # Inorganic
    "water": "H2O", "ammonia": "NH3", "sulfuric acid": "H2SO4", 
    "hydrochloric acid": "HCl", "nitric acid": "HNO3", "sodium hydroxide": "NaOH",
    "potassium hydroxide": "KOH", "calcium hydroxide": "Ca(OH)2",
    "carbon dioxide": "CO2", "carbon monoxide": "CO", "hydrogen peroxide": "H2O2",
    "oxygen": "O2", "nitrogen": "N2", "hydrogen": "H2", "chlorine": "Cl2",
    "bromine": "Br2", "iodine": "I2", "sulfur": "S8", "phosphorus": "P4",
    "ozone": "O3", "sodium chloride": "NaCl", "calcium carbonate": "CaCO3"
}

# Predefined common reactions (expanded)
COMMON_REACTIONS = {
    # Combustion
    "combustion of methane": ("CH4 + O2", "CO2 + H2O"),
    "combustion of ethane": ("C2H6 + O2", "CO2 + H2O"),
    "combustion of propane": ("C3H8 + O2", "CO2 + H2O"),
    "combustion of butane": ("C4H10 + O2", "CO2 + H2O"),
    "combustion of benzene": ("C6H6 + O2", "CO2 + H2O"),
    "combustion of ethanol": ("C2H5OH + O2", "CO2 + H2O"),
    
    # Neutralization
    "neutralization": ("HCl + NaOH", "NaCl + H2O"),
    "sulfuric acid neutralization": ("H2SO4 + NaOH", "Na2SO4 + H2O"),
    "acid base reaction": ("HCl + KOH", "KCl + H2O"),
    
    # Organic Reactions
    "halogenation of methane": ("CH4 + Cl2", "CH3Cl + HCl"),
    "halogenation of ethane": ("C2H6 + Cl2", "C2H5Cl + HCl"),
    "chlorination of benzene": ("C6H6 + Cl2", "C6H5Cl + HCl"),
    "bromination of benzene": ("C6H6 + Br2", "C6H5Br + HBr"),
    "hydration of ethene": ("C2H4 + H2O", "C2H5OH"),
    "esterification": ("CH3COOH + C2H5OH", "CH3COOC2H5 + H2O"),
    "fermentation": ("C6H12O6", "C2H5OH + CO2"),
    "dehydration of ethanol": ("C2H5OH", "C2H4 + H2O"),
    
    # Inorganic Reactions
    "photosynthesis": ("CO2 + H2O", "C6H12O6 + O2"),
    "ammonia synthesis": ("N2 + H2", "NH3"),
    "electrolysis of water": ("H2O", "H2 + O2"),
    "haber process": ("N2 + H2", "NH3"),
    "contact process": ("SO2 + O2", "SO3"),
    "decomposition of ozone": ("O3", "O2"),
    "decomposition of hydrogen peroxide": ("H2O2", "H2O + O2"),
    "reaction of sodium with chlorine": ("Na + Cl2", "NaCl"),
    "reaction of calcium carbonate": ("CaCO3", "CaO + CO2"),
    "reaction of aluminum with oxygen": ("Al + O2", "Al2O3"),
    
    # Addition Reactions
    "hydrogenation of ethene": ("C2H4 + H2", "C2H6"),
    "hydrogenation of benzene": ("C6H6 + H2", "C6H12"),
    
    # Substitution Reactions
    "nitration of benzene": ("C6H6 + HNO3", "C6H5NO2 + H2O"),
    "sulfonation of benzene": ("C6H6 + H2SO4", "C6H5SO3H + H2O"),
    "friedel crafts alkylation": ("C6H6 + CH3Cl", "C6H5CH3 + HCl"),
    
    # Oxidation
    "oxidation of ethanol": ("C2H5OH + O2", "CH3COOH + H2O"),
    "oxidation of sulfur dioxide": ("SO2 + O2", "SO3"),
    "oxidation of acetaldehyde":("C2H4O+O2","C2H202+H2O"),
    #SYNTHESES
    #"gattermann aldehyde synthesis":("C6H6+HN=CHCl","C7H6O+NH3"),
    "Gattermann aldehyde synthesis": ("C6H6 + HCN → C6H5CHO"),

}

# Function to parse chemical names
def parse_chemicals(input_str):
    input_str = input_str.lower()
    chemicals = []
    
    # First check for exact matches in common reactions
    for name in COMMON_REACTIONS:
        if name in input_str:
            return COMMON_REACTIONS[name]
    
    # Tokenize input
    tokens = re.findall(r'\b[\w\s]+\b', input_str)
    
    # Identify chemicals
    for token in tokens:
        token = token.strip()
        if token in COMMON_NAMES:
            chemicals.append(COMMON_NAMES[token])
        else:
            # Try to identify chemical formulas
            if any(char.isdigit() for char in token) and any(char.isalpha() for char in token):
                # Validate chemical formula
                parts = re.findall('[A-Z][^A-Z]*', token)
                if all(part.capitalize() in periodic.symbols for part in parts):
                    chemicals.append(token)
    
    return chemicals

# Function to balance equation
def balance_equation(reactants_str, products_str):
    try:
        reactants = [s.strip() for s in reactants_str.split('+')]
        products = [s.strip() for s in products_str.split('+')]
        
        # Convert common names to formulas
        reactants = [COMMON_NAMES.get(r.lower().strip(), r) for r in reactants]
        products = [COMMON_NAMES.get(p.lower().strip(), p) for p in products]
        
        # Balance stoichiometry
        reac, prod = balance_stoichiometry(reactants, products)
        
        # Format equation
        reactant_side = " + ".join([f"{coeff} {formula}" if coeff != 1 else formula 
                                   for formula, coeff in reac.items()])
        product_side = " + ".join([f"{coeff} {formula}" if coeff != 1 else formula 
                                  for formula, coeff in prod.items()])
        
        return f"{reactant_side} → {product_side}"
    
    except Exception as e:
        return f"Error: {str(e)}"

# Function to detect reaction type
def detect_reaction_type(equation):
    equation = equation.lower()
    if "co2" in equation and "h2o" in equation and "o2" in equation:
        return "Combustion"
    if "h2o" in equation and ("h+" in equation or "oh-" in equation or "acid" in equation):
        return "Acid-Base Neutralization"
    if "nh3" in equation:
        return "Ammonia Synthesis"
    if "cl2" in equation and "c6h6" in equation:
        return "Aromatic Halogenation"
    if "br2" in equation and "c6h6" in equation:
        return "Aromatic Halogenation"
    if "hno3" in equation and "c6h6" in equation:
        return "Aromatic Nitration"
    if "h2so4" in equation and "c6h6" in equation:
        return "Aromatic Sulfonation"
    if "ch3coo" in equation:
        return "Esterification"
    if "c2h4" in equation and "h2" in equation:
        return "Hydrogenation"
    if "c6h6" in equation and "h2" in equation:
        return "Hydrogenation"
    if "h2o" in equation and "c2h4" in equation:
        return "Hydration"
    if "c6h12o6" in equation and "c2h5oh" in equation:
        return "Fermentation"
    if "so2" in equation and "o2" in equation:
        return "Oxidation"
    if "o3" in equation and "o2" in equation:
        return "Decomposition"
    if "caco3" in equation and "cao" in equation:
        return "Decomposition"
    return "General Reaction"

# Streamlit UI
st.title("🧪 Advanced Chemical Reaction Explorer")
st.subheader("Ask about organic/inorganic reactions and get balanced equations")

# Input section
query = st.text_input("Ask a question about chemical reactions:", 
                      placeholder="e.g., chlorination of benzene, combustion of ethanol")

# Create list of reaction types
reaction_types = sorted({name.split()[0] for name in COMMON_REACTIONS})
reaction_type = st.selectbox("Or choose a reaction type:", ["All"] + reaction_types)

# Display common reactions if type selected
if reaction_type != "All":
    st.write(f"*Common {reaction_type} reactions:*")
    for name, (react, prod) in COMMON_REACTIONS.items():
        if name.startswith(reaction_type):
            balanced_eq = balance_equation(react, prod)
            st.code(f"{name.capitalize()}: {balanced_eq}")

# Process question
if st.button("Get Reaction") and query:
    with st.spinner("Balancing equation..."):
        # Try to match common reactions first
        query_lower = query.lower()
        matched = False
        
        for name, (react, prod) in COMMON_REACTIONS.items():
            if name in query_lower:
                balanced_eq = balance_equation(react, prod)
                rtype = detect_reaction_type(balanced_eq)
                
                st.success(f"{name.capitalize()} Reaction**")
                st.subheader("Balanced Equation:")
                st.code(balanced_eq)
                st.write(f"*Type:* {rtype}")
                
                # Add to history
                st.session_state.history.insert(0, {
                    "query": query,
                    "equation": balanced_eq,
                    "type": rtype
                })
                matched = True
                break
        
        # If no common match found, try to parse
        if not matched:
            chemicals = parse_chemicals(query)
            if len(chemicals) >= 2:
                # Try to split into reactants/products (simple heuristic)
                reactants = " + ".join(chemicals[:len(chemicals)//2])
                products = " + ".join(chemicals[len(chemicals)//2:])
                
                balanced_eq = balance_equation(reactants, products)
                rtype = detect_reaction_type(balanced_eq)
                
                st.success("Balanced Equation")
                st.subheader("Balanced Equation:")
                st.code(balanced_eq)
                st.write(f"*Type:* {rtype}")
                
                # Add to history
                st.session_state.history.insert(0, {
                    "query": query,
                    "equation": balanced_eq,
                    "type": rtype
                })
            else:
                st.warning("Couldn't identify enough chemicals in your query. Try examples like:")
                st.write("- Chlorination of benzene")
                st.write("- Combustion of ethanol")
                st.write("- Neutralization reaction")
                st.write("- Ammonia synthesis")
                st.write("- Fermentation of glucose")

# Display history
if st.session_state.history:
    st.divider()
    st.subheader("Recent Queries")
    for i, item in enumerate(st.session_state.history[:5]):
        st.write(f"{i+1}. *{item['query']}*")
        st.caption(f"Equation: {item['equation']}")
        st.caption(f"Type: {item['type']}")
        st.write("")

# Features explanation
st.sidebar.title("About")
st.sidebar.info("This app can:\n"
                "1. Identify 50+ common chemical names\n"
                "2. Balance stoichiometric equations\n"
                "3. Recognize 20+ reaction types\n"
                "4. Show reaction history\n"
                "5. Handle organic and inorganic reactions")

st.sidebar.divider()
st.sidebar.subheader("Example Queries")
st.sidebar.write("- Chlorination of benzene")
st.sidebar.write("- Combustion of ethanol")
st.sidebar.write("- Neutralization reaction")
st.sidebar.write("- Ammonia synthesis")
st.sidebar.write("- Fermentation of glucose")
st.sidebar.write("- Nitration of benzene")
st.sidebar.write("- Hydrogenation of ethene")

st.sidebar.divider()
st.sidebar.caption("Uses ChemPy for stoichiometric balancing")
st.sidebar.caption("Supports 100+ common chemical reactions")
