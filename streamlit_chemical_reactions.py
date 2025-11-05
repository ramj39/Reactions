import streamlit as st
import chempy
from chempy import balance_stoichiometry
from chempy.util import periodic
import re

# Session state for history
if 'history' not in st.session_state:
    st.session_state.history = []

COMMON_NAMES = {
    # Your common names here (same as given)
    "methane": "CH4", "ethane": "C2H6", # ...
    "water": "H2O", "ammonia": "NH3", # ...
}

COMMON_REACTIONS = {
    "combustion of methane": ("CH4 + O2", "CO2 + H2O"),
    "neutralization": ("HCl + NaOH", "NaCl + H2O"),
    # More as defined
}

def parse_chemicals(input_str):
    input_str = input_str.lower()
    chemicals = []
    for name in COMMON_REACTIONS:
        if name in input_str:
            return COMMON_REACTIONS[name]
    tokens = re.findall(r'\b[\w\d\(\)]+\b', input_str)
    for token in tokens:
        token = token.strip()
        # Map common names
        if token in COMMON_NAMES:
            chemicals.append(COMMON_NAMES[token])
        else:
            # Validate chemical formulas
            parts = re.findall(r'[A-Z][a-z]?', token)
            if all(part in periodic.symbols for part in parts):
                chemicals.append(token)
    return chemicals

def balance_equation(reactants_str, products_str):
    try:
        reactants = [r.strip() for r in reactants_str.split('+')]
        products = [p.strip() for p in products_str.split('+')]
        reactants = [COMMON_NAMES.get(r.lower(), r) for r in reactants]
        products = [COMMON_NAMES.get(p.lower(), p) for p in products]
        reac, prod = balance_stoichiometry(reactants, products)
        reactant_side = " + ".join(f"{coeff} {formula}" if coeff != 1 else formula for formula, coeff in reac.items())
        product_side = " + ".join(f"{coeff} {formula}" if coeff != 1 else formula for formula, coeff in prod.items())
        return f"{reactant_side} → {product_side}"
    except Exception as e:
        return f"Error balancing equation: {e}"

def detect_reaction_type(equation):
    eq = equation.lower()
    if "co2" in eq and "h2o" in eq and "o2" in eq:
        return "Combustion"
    if "h2o" in eq and ("h+" in eq or "oh-" in eq or "acid" in eq):
        return "Acid-Base Neutralization"
    # Other detection rules...
    return "General Reaction"

st.title("🧪 Advanced Chemical Reaction Explorer")
query = st.text_input("Enter a chemical reaction or reaction name:", placeholder="e.g., combustion of methane")

if st.button("Get Reaction") and query:
    matched = False
    qlow = query.lower()
    for name, (react, prod) in COMMON_REACTIONS.items():
        if name == qlow:
            balanced = balance_equation(react, prod)
            st.success(f"{name.capitalize()} Reaction")
            st.code(balanced)
            st.write(f"Type: {detect_reaction_type(balanced)}")
            st.session_state.history.insert(0, {"query": query, "equation": balanced, "type": detect_reaction_type(balanced)})
            matched = True
            break
    if not matched:
        chemicals = parse_chemicals(query)
        if len(chemicals) >= 2:
            mid = len(chemicals) // 2
            balanced = balance_equation(" + ".join(chemicals[:mid]), " + ".join(chemicals[mid:]))
            st.success("Balanced Equation")
            st.code(balanced)
            st.write(f"Type: {detect_reaction_type(balanced)}")
            st.session_state.history.insert(0, {"query": query, "equation": balanced, "type": detect_reaction_type(balanced)})
        else:
            st.warning("Couldn't identify enough chemicals in your query. Try examples like combustion of methane, neutralization.")

if st.session_state.history:
    st.divider()
    st.subheader("Recent Queries")
    for i, h in enumerate(st.session_state.history[:5]):
        st.write(f"{i+1}. {h['query']}")
        st.caption(f"Equation: {h['equation']}")
        st.caption(f"Type: {h['type']}")
        st.write("")
