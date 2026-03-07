import streamlit as st
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# ---------------------------------------------------------
# 1. THE CALCULATION ENGINE (Monte Carlo Logic)
# ---------------------------------------------------------
def run_hta_simulation(direct_cost, outcome_rate, downstream_cost, iterations=10000):
    # Success/Failure modeling using Beta Distribution
    # We use 50 as a 'certainty' factor for the distribution shape
    a, b = outcome_rate * 50, (1 - outcome_rate) * 50
    sim_outcomes = np.random.beta(a, b, iterations)
    
    # Cost modeling using Gamma Distribution (costs are never negative)
    sim_direct_costs = np.random.gamma(shape=20, scale=direct_cost/20, size=iterations)
    
    # Total Cost = Upfront Cost + (Probability of Failure * Cost of treating failure)
    total_costs = sim_direct_costs + ((1 - sim_outcomes) * downstream_cost)
    return total_costs

# ---------------------------------------------------------
# 2. PAGE CONFIGURATION
# ---------------------------------------------------------
st.set_page_config(page_title="Health Economic Simulator", layout="wide")
st.title("🏥 Universal Health Economic Simulator")
st.subheader("Compare two strategies using Stochastic Monte Carlo Modeling")
st.markdown("---")

# ---------------------------------------------------------
# 3. SIDEBAR PARAMETERS
# ---------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Global Parameters")
    st.write("These costs apply if a strategy fails to achieve a positive outcome.")
    failure_cost = st.number_input("Downstream Cost of Failure (₹)", 0, 50000, 5000)
    
    st.divider()
    st.header("📖 About this Tool")
    st.info("""
    This tool performs a **Probabilistic Cost-Effectiveness Analysis**. 
    Instead of using single averages, it runs **10,000 simulations** 
    to account for clinical uncertainty.
    """)
    st.caption("Developed for Health Technology Assessment (HTA) modeling.")

# ---------------------------------------------------------
# 4. USER INPUTS (Strategy A vs B)
# ---------------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🔵 Strategy A")
    name_a = st.text_input("Intervention Name", "New Treatment", key="na")
    cost_a = st.number_input("Upfront Cost (₹)", 0, 20000, 1500, key="ca")
    success_a = st.slider("Anticipated Success Rate", 0.0, 1.0, 0.90, key="sa")

with col2:
    st.markdown("### 🟠 Strategy B")
    name_b = st.text_input("Intervention Name", "Standard Care", key="nb")
    cost_b = st.number_input("Upfront Cost (₹)", 0, 20000, 800, key="cb")
    success_b = st.slider("Anticipated Success Rate", 0.0, 1.0, 0.75, key="sb")

st.write("") # Spacer

# ---------------------------------------------------------
# 5. EXECUTION & VISUALS
# ---------------------------------------------------------
if st.button("🚀 Run 10,000 Simulations", use_container_width=True):
    # Run the math
    results_a = run_hta_simulation(cost_a, success_a, failure_cost)
    results_b = run_hta_simulation(cost_b, success_b, failure_cost)
    
    # Create the Visual
    fig, ax = plt.subplots(figsize=(10, 4))
    sns.kdeplot(results_a, fill=True, label=name_a, color="#1f77b4", ax=ax)
    sns.kdeplot(results_b, fill=True, label=name_b, color="#ff7f0e", ax=ax)
    
    plt.title("Distribution of Total Expected Costs")
    plt.xlabel("Total Cost per Patient (Including Risk)")
    plt.ylabel("Probability Density")
    plt.legend()
    
    # Show the plot
    st.pyplot(fig)
    
    # Summary Metrics
    avg_a = np.mean(results_a)
    avg_b = np.mean(results_b)
    diff = avg_b - avg_a
    
    m1, m2, m3 = st.columns(3)
    m1.metric(f"Avg Cost ({name_a})", f"₹{avg_a:,.0f}")
    m2.metric(f"Avg Cost ({name_b})", f"₹{avg_b:,.0f}")
    
    if diff > 0:
        m3.metric("Potential Savings", f"₹{diff:,.0f}", delta="Cost Effective")
    else:
        m3.metric("Cost Difference", f"₹{abs(diff):,.0f}", delta="More Expensive", delta_color="inverse")
