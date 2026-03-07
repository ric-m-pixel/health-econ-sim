import streamlit as st
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# ---------------------------------------------------------
# 1. ENGINE
# ---------------------------------------------------------
def run_hta_simulation(direct_cost, outcome_rate, downstream_cost, iterations=10000):
    a, b = outcome_rate * 50, (1 - outcome_rate) * 50
    sim_outcomes = np.random.beta(a, b, iterations)
    sim_direct_costs = np.random.gamma(shape=20, scale=direct_cost/20, size=iterations)
    total_costs = sim_direct_costs + ((1 - sim_outcomes) * downstream_cost)
    return total_costs, sim_outcomes

# ---------------------------------------------------------
# 2. APP SETUP
# ---------------------------------------------------------
st.set_page_config(page_title="HTA Pro Simulator", layout="wide")
st.title("🛡️ HTA Decision-Support Suite")

with st.sidebar:
    st.header("🛠️ Model Configuration")
    model_mode = st.radio("Analysis Type:", ["Clinical Success", "QALY (Cost-Effectiveness)"])
    failure_cost = st.number_input("Downstream/Failure Cost (₹)", 0, 50000, 5000)
    wtp_threshold = st.slider("WTP Threshold (₹)", 50000, 1000000, 300000, 50000)

# ---------------------------------------------------------
# 3. INPUTS
# ---------------------------------------------------------
col1, col2 = st.columns(2)
with col1:
    st.markdown("### 🔵 Strategy A")
    name_a = st.text_input("Name", "New Treatment", key="na")
    cost_a = st.number_input("Cost (₹)", 0, 20000, 1500, key="ca")
    val_a = st.slider("Success/QALY", 0.0, 1.0, 0.85, key="va")

with col2:
    st.markdown("### 🟠 Strategy B")
    name_b = st.text_input("Name", "Standard Care", key="nb")
    cost_b = st.number_input("Cost (₹)", 0, 20000, 800, key="cb")
    val_b = st.slider("Success/QALY", 0.0, 1.0, 0.70, key="vb")

# ---------------------------------------------------------
# 4. RUN SIMULATION
# ---------------------------------------------------------
if st.button("🚀 Run Full Probabilistic Analysis", use_container_width=True):
    costs_a, out_a = run_hta_simulation(cost_a, val_a, failure_cost)
    costs_b, out_b = run_hta_simulation(cost_b, val_b, failure_cost)
    
    inc_costs = costs_a - costs_b
    inc_effects = out_a - out_b

    # TABS FOR CLEAN UI
    tab1, tab2, tab3 = st.tabs(["📊 Distribution", "🎯 CE Plane", "💾 Export Data"])

    with tab1:
        fig1, ax1 = plt.subplots(figsize=(10, 4))
        sns.kdeplot(costs_a, fill=True, label=name_a, color="#1f77b4")
        sns.kdeplot(costs_b, fill=True, label=name_b, color="#ff7f0e")
        plt.title("Total Cost Probability Density")
        st.pyplot(fig1)

    with tab2:
        fig2, ax2 = plt.subplots(figsize=(8, 6))
        # Plot 10,000 dots
        plt.scatter(inc_effects, inc_costs, alpha=0.1, color='purple', s=1)
        # Threshold Line
        x_vals = np.array([plt.xlim()[0], plt.xlim()[1]])
        plt.plot(x_vals, wtp_threshold * x_vals, color='red', linestyle='--', label='WTP Threshold')
        
        plt.axhline(0, color='black', lw=1)
        plt.axvline(0, color='black', lw=1)
        plt.xlabel("Incremental Effectiveness (QALY Gained)")
        plt.ylabel("Incremental Cost (₹)")
        plt.title("Cost-Effectiveness Plane (Uncertainty Cloud)")
        plt.legend()
        st.pyplot(fig2)
        st.info("Dots below the red dashed line represent cost-effective simulations.")

    with tab3:
        df_results = pd.DataFrame({
            f"Cost_{name_a}": costs_a,
            f"Cost_{name_b}": costs_b,
            "Incremental_Cost": inc_costs,
            "Incremental_Effect": inc_effects
        })
        csv = df_results.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Simulation Raw Data (CSV)", data=csv, file_name="hta_results.csv", mime="text/csv")

    # KEY METRICS
    avg_icer = np.mean(inc_costs) / np.mean(inc_effects) if np.mean(inc_effects) != 0 else 0
    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric("Mean ICER", f"₹{avg_icer:,.0f}")
    
    # CE Probability
    prob_ce = np.mean(inc_costs < (inc_effects * wtp_threshold)) * 100
    c2.metric("Probability Cost-Effective", f"{prob_ce:.1f}%")
    c3.metric("WTP Threshold", f"₹{wtp_threshold:,.0f}")
