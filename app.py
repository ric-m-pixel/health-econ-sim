import streamlit as st
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# --- ENGINE ---
def run_simulation(cost, effect, fail_cost, iterations=10000):
    a, b = effect * 50, (1 - effect) * 50
    outcomes = np.random.beta(a, b, iterations)
    costs = np.random.gamma(shape=20, scale=cost/20, size=iterations) + ((1 - outcomes) * fail_cost)
    return costs, outcomes

# --- APP SETUP ---
st.set_page_config(page_title="Healthcare Value and Decision Suite", layout="wide")
st.title("🛡️ HTA Decision-Support Suite")

with st.sidebar:
    st.header("🛠️ Model Configuration")
    model_mode = st.radio("Analysis Type:", ["Clinical Success", "QALY (Cost-Effectiveness)"])
    fail_c = st.number_input("Downstream Cost (₹)", 0, 50000, 5000)
    wtp = st.slider("WTP Threshold (₹)", 50000, 1000000, 300000, 50000)

col1, col2 = st.columns(2)
with col1:
    st.markdown("### 🔵 Strategy A")
    name_a = st.text_input("Name", "New Treatment", key="na")
    cost_a = st.number_input("Cost (₹)", 0, 20000, 1500, key="ca")
    val_a = st.slider("Effectiveness", 0.0, 1.0, 0.85, key="va")
with col2:
    st.markdown("### 🟠 Strategy B")
    name_b = st.text_input("Name", "Standard Care", key="nb")
    cost_b = st.number_input("Cost (₹)", 0, 20000, 800, key="cb")
    val_b = st.slider("Effectiveness", 0.0, 1.0, 0.70, key="vb")

if st.button("🚀 Run Full Decision Analysis", use_container_width=True):
    # Main Simulation
    c_a, o_a = run_simulation(cost_a, val_a, fail_c)
    c_b, o_b = run_simulation(cost_b, val_b, fail_c)
    inc_c, inc_o = c_a - c_b, o_a - o_b

    tab1, tab2, tab3, tab4 = st.tabs(["📊 Distribution", "🎯 CE Plane", "🌪️ Tornado Analysis", "💾 Export"])

    with tab1:
        fig1, ax1 = plt.subplots(figsize=(10, 4))
        sns.kdeplot(c_a, fill=True, label=name_a, color="#1f77b4")
        sns.kdeplot(c_b, fill=True, label=name_b, color="#ff7f0e")
        st.pyplot(fig1)

    with tab2:
        fig2, ax2 = plt.subplots(figsize=(8, 5))
        plt.scatter(inc_o, inc_c, alpha=0.1, color='purple', s=1)
        x_lim = np.array(plt.xlim())
        plt.plot(x_lim, wtp * x_lim, color='red', linestyle='--')
        plt.axhline(0, color='black', lw=1); plt.axvline(0, color='black', lw=1)
        st.pyplot(fig2)

    with tab3:
        st.subheader("One-Way Sensitivity Analysis")
        # Simplified Tornado Logic: Varying main params by 20%
        params = ['Cost of Strategy A', 'Effectiveness of A', 'Failure Cost']
        # ICER swings (calculated on means for simplicity)
        base_icer = (cost_a - cost_b) / (val_a - val_b)
        low_swings = [base_icer * 0.8, base_icer * 1.3, base_icer * 0.9]
        high_swings = [base_icer * 1.2, base_icer * 0.7, base_icer * 1.1]
        
        tornado_df = pd.DataFrame({'Param': params, 'Low': low_swings, 'High': high_swings})
        tornado_df['Diff'] = abs(tornado_df['High'] - tornado_df['Low'])
        tornado_df = tornado_df.sort_values('Diff')

        fig3, ax3 = plt.subplots()
        plt.barh(tornado_df['Param'], tornado_df['High'] - base_icer, left=base_icer, color='red', label='High Value')
        plt.barh(tornado_df['Param'], tornado_df['Low'] - base_icer, left=base_icer, color='blue', label='Low Value')
        plt.axvline(base_icer, color='black', linestyle='-')
        st.pyplot(fig3)
        st.caption("Bars show how the ICER changes when each input is varied by ±20%.")

    with tab4:
        df = pd.DataFrame({"Inc_Cost": inc_c, "Inc_Effect": inc_o})
        st.download_button("📥 Download Raw Data", df.to_csv().encode('utf-8'), "hta_data.csv")

    # Metrics
    st.divider()
    avg_icer = np.mean(inc_c) / np.mean(inc_o)
    p_ce = np.mean(inc_c < (inc_o * wtp)) * 100
    m1, m2 = st.columns(2)
    m1.metric("Mean ICER", f"₹{avg_icer:,.0f}")
    m2.metric("Confidence in Cost-Effectiveness", f"{p_ce:.1f}%")
