import streamlit as st
import pandas as pd
import plotly.express as px
from data_manager import initialize_data, get_df

# --- INITIALIZE DATABASE ---
initialize_data()


st.set_page_config(page_title="AI Security & Governance Assurance", layout="wide")

df_inventory = get_df("inventory.json")
df_risks = get_df("risks.json")
df_controls = get_df("controls.json")
df_evidence = get_df("evidence.json")

# --- SIDEBAR ---
st.sidebar.title("🛡️ AI Security Lab")
menu = st.sidebar.radio("Navigate", ["Executive Dashboard", "AI Inventory", "Risk & Controls", "Traceability Thread"])

# --- 1. EXECUTIVE DASHBOARD ---
if menu == "Executive Dashboard":
    st.title("Executive Governance Dashboard")
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Total AI Systems", len(df_inventory))
    c2.metric("Open Risks", len(df_risks[df_risks['status'] == 'Open']))
    c3.metric("Critical Systems", len(df_inventory[df_inventory['risk_tier'] == 'Critical']))

    st.subheader("Risk Heatmap (Impact vs Likelihood)")
    fig = px.scatter(df_risks, x="likelihood", y="impact", color="status", 
                     hover_name="risk", size_max=40, height=400)
    st.plotly_chart(fig, use_container_width=True)

# --- 2. AI INVENTORY ---
elif menu == "AI Inventory":
    st.title("AI Asset Inventory")
    st.dataframe(df_inventory, use_container_width=True)

# --- 3. RISK & CONTROLS ---
elif menu == "Risk & Controls":
    st.title("Risk Register & Framework Mapping")
    
    st.subheader("Active Risks")
    st.table(df_risks)
    
    st.subheader("Control Mapping (NIST / OWASP / MITRE)")
    st.dataframe(df_controls, use_container_width=True)

# --- 4. TRACEABILITY THREAD ---
elif menu == "Traceability Thread":
    st.title("End-to-End Governance Traceability")
    
    # Selecting the specific thread from Project 1
    finding = df_risks[df_risks['id'] == 'R-001'].iloc[0]
    control = df_controls[df_controls['cid'] == 'C-001'].iloc[0]
    evidence = df_evidence[df_evidence['eid'] == 'EV-102'].iloc[0]

    st.info(f"👉 **Tracing Risk ID:** {finding['id']} - {finding['risk']}")

    # The Flow
    t1, t2, t3, t4 = st.tabs(["1. Technical Finding", "2. Risk Management", "3. Control Mapping", "4. Evidence & Retest"])

    with t1:
        st.error("**Red-Team Discovery:** Indirect Prompt Injection via email integration on AI-002.")
        st.markdown(f"**MITRE ATLAS Technique:** `{finding['mitre']}`")
    
    with t2:
        st.write(f"**Impact Assessment:** {finding['impact']}")
        st.write(f"**Treatment Strategy:** Mitigate via technical guardrails.")
    
    with t3:
        st.write(f"**Mapped Control:** {control['name']}")
        st.json({
            "NIST AI RMF": control['nist'],
            "OWASP LLM Top 10": control['owasp'],
            "MITRE ATLAS": control['mitre']
        })
    
    with t4:
        st.success(f"**Retest Result:** {evidence['result']}")
        st.write(f"**Proof/Artifact:** {evidence['test']} on {evidence['date']}")
        st.button("Download Executive Summary (PDF)")