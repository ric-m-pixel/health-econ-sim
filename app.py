import streamlit as st
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# ---------------------------------------------------------
# 1. THE CALCULATION ENGINE
# ---------------------------------------------------------
def run_hta_simulation(direct_cost, outcome_rate, downstream_cost, iterations=10000):
    a, b = outcome_rate * 50, (1 - outcome_rate) * 50
    sim_outcomes = np.random.beta(a, b, iterations)
    sim_direct_costs = np.random.gamma(shape=20, scale=direct_cost/20, size=iterations)
    # Total Cost = Direct + ((1 - outcome) * failure_cost)
    total_costs = sim_direct_costs + ((1 - sim_outcomes) * downstream_cost)
    return total_costs, sim_outcomes

# ---------------------------------------------------------
# 2. PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(page_title="Health Econ Simulator", layout="wide")
st.title("🏥 Health Technology Assessment Simulator")

# ---------------------------------------------------------
# 3. SIDEBAR: MODEL SELECTION
# ---------------------------------------------------------
with st.sidebar:
    st.header("🛠️ Model Settings")
    model_mode = st.radio("Choose Analysis Type:", ["Clinical Success Rate", "QALY (Cost-Effectiveness)"])
    
    st.divider()
    failure_cost = st.number_input("Downstream/Failure Cost (₹)", 0, 50000, 5000)
    
    if model_mode == "QALY (Cost-Effectiveness)":
        wtp_threshold = st.slider("Willingness to Pay (WTP) Threshold", 50000, 1000000, 300000, step=50000)
        st.caption("Commonly ₹3,00,000 per QALY in many HTA frameworks.")

# ---------------------------------------------------------
# 4. INPUTS
# ---------------------------------------------------------
label_name = "Success Rate" if model_mode == "Clinical Success Rate" else "Expected QALY"
default_val_a = 0.90 if model_mode == "Clinical Success Rate" else 0.85
default_val_b = 0.75 if model_mode == "Clinical Success Rate" else 0.65

col1, col2 = st.columns(2)
with col1:
    st.markdown("### 🔵 Strategy A")
    name_a = st.text_input("Name", "New Intervention", key="na")
    cost_a = st.number_input("Upfront Cost (₹)", 0, 20000, 1500, key="ca")
    val_a = st.slider(label_name, 0.0, 1.0, default_val_a, key="va")

with col2:
    st.markdown("### 🟠 Strategy B")
    name_b = st.text_input("Name", "Standard Care", key="nb")
    cost_b = st.number_input("Upfront Cost (₹)", 0, 20000, 800, key="cb")
    val_b = st.slider(label_name, 0.0, 1.0, default_val_b, key="vb")

# ---------------------------------------------------------
# 5. RESULTS
# ---------------------------------------------------------
if st.button("🚀 Run 10,000 Simulations", use_container_width=True):
    costs_a, outcomes_a = run_hta_simulation(cost_a, val_a, failure_cost)
    costs_b, outcomes_b = run_hta_simulation(cost_b, val_b, failure_cost)
    
    # Plotting
    fig, ax = plt.subplots(figsize=(10, 4))
    sns.kdeplot(costs_a, fill=True, label=name_a, color="#1f77b4", ax=ax)
    sns.kdeplot(costs_b, fill=True, label=name_b, color="#ff7f0e", ax=ax)
    plt.title("Probabilistic Cost Distribution")
    plt.xlabel("Total Expected Cost (₹)")
    st.pyplot(fig)
    
    avg_c_a, avg_c_b = np.mean(costs_a), np.mean(costs_b)
    
    m1, m2, m3 = st.columns(3)
    
    if model_mode == "Clinical Success Rate":
        m1.metric(f"Avg Cost ({name_a})", f"₹{avg_c_a:,.0f}")
        m2.metric(f"Avg Cost ({name_b})", f"₹{avg_c_b:,.0f}")
        savings = avg_c_b - avg_c_a
        m3.metric("Expected Savings", f"₹{savings:,.0f}", delta="Cost Effective" if savings > 0 else "Pricey")
    
    else: # QALY MODE
        inc_cost = avg_c_a - avg_c_b
        inc_qaly = val_a - val_b
        icer = inc_cost / inc_qaly if inc_qaly != 0 else 0
        
        m1.metric("Incremental Cost", f"₹{inc_cost:,.0f}")
        m2.metric("QALYs Gained", f"{inc_qaly:.2f}")
        m3.metric("ICER (Cost/QALY)", f"₹{icer:,.0f}")
        
        if icer < wtp_threshold:
            st.success(f"✅ Strategy {name_a} is COST-EFFECTIVE (Below threshold of ₹{wtp_threshold:,.0f})")
        else:
            st.warning(f"⚠️ Strategy {name_a} is NOT cost-effective at current threshold.")
