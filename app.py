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
st.title("🛡️ Healthcare Value and Decision Suite")

with st.sidebar:
    # --- Currency Selector ---
    currency_symbol = st.selectbox(
    "Select Currency",
    options=["$", "€", "£", "₹", "¥"],
    index=0  # Defaults to USD ($) for international reviewers
    )
    st.header("🛠️ Model Configuration")
    st.header("🛠️ Model Configuration")
    
    # 1. The Global Switcher
    analysis_level = st.radio(
        "Select Model Complexity",
        ["Standard (Static)", "Advanced (Temporal/Markov)"]
    )

# 3. Model-Specific Inputs
# --- Universal Inputs (Visible in BOTH modes) ---
fail_c = st.number_input(f"Downstream Failure Cost ({currency_symbol})", 0, 50000, 5000)
wtp = st.number_input("Willingness-to-Pay threshold (₹)", min_value=0, value=1000, step=100)
st.info("The WTP threshold represents the maximum price a system is willing to pay for 1 unit of benefit.")

st.divider()

# --- Model-Specific Inputs ---
if analysis_level == "Standard (Static)":
    st.subheader("📍 Static Parameters")
    model_mode = st.radio("Analysis Type:", ["Clinical Success", "QALY (Cost-Effectiveness)"], key="static_mode")
    
    # (Your Strategy A and Strategy B success sliders will go right here, underneath this line)

else:
    st.subheader("⏳ Markov Parameters")
    # (We will build the Matrix and State names right here later)
    # This must be OUTSIDE any buttons to show all the time
st.divider()
st.markdown("### 👨‍💻 Developed By")
st.markdown("**Richa Mishra**")

col1, col2 = st.columns(2)
with col1:
    st.markdown("### 🔵 Strategy A")
    name_a = st.text_input("Name", "New Treatment", key="na")
    cost_a = st.number_input(f"Cost ({currency_symbol})", 0, 20000, 1500, key="ca")
    val_a = st.slider("Effectiveness", 0.0, 1.0, 0.85, key="va")
with col2:
    st.markdown("### 🟠 Strategy B")
    name_b = st.text_input("Name", "Standard Care", key="nb")
    cost_b = st.number_input(f"Cost ({currency_symbol})", 0, 20000, 800, key="cb")
    val_b = st.slider("Effectiveness", 0.0, 1.0, 0.70, key="vb")
if st.button("🚀 Run Full Decision Analysis", use_container_width=True):
    # Main Simulation
    c_a, o_a = run_simulation(cost_a, val_a, fail_c)
    c_b, o_b = run_simulation(cost_b, val_b, fail_c)
    inc_c, inc_o = c_a - c_b, o_a - o_b
    # --- EXECUTIVE SUMMARY SECTION ---
    st.divider()
    st.subheader("📝 Executive Summary & Verdict") 
    # 1. Define the math for the app to recognize
    avg_diff_cost = inc_c.mean()
    avg_diff_effect = inc_o.mean()
    # Avoid division by zero
    avg_icer = avg_diff_cost / avg_diff_effect if avg_diff_effect != 0 else 0
    # Assuming threshold from your sidebar slider or 300,000 as seen in your screenshot
    # Ensure we are using the dynamic wtp from your sidebar, not a hardcoded number
    # Calculate probability of cost-effectiveness using Net Monetary Benefit (NMB)
    # NMB = (Effectiveness * WTP) - Cost. If NMB > 0, it's cost-effective!
    p_ce = (((inc_o * wtp) - inc_c) > 0).mean() * 100
    
    # 2. Logic for the Verdict
    nmb_avg = (avg_diff_effect * wtp) - avg_diff_cost

    # --- INSERT NEW CHECK HERE ---
    if avg_diff_effect == 0 and avg_diff_cost == 0:
        verdict = "Strategies are Equivalent"
        verdict_color = "gray"
        reason = "Both strategies have identical costs and clinical outcomes."
    
    # --- CHANGE THIS TO 'elif' ---
    elif avg_diff_effect <= 0 and avg_diff_cost >= 0:
        verdict = f"Strategy '{name_a}' is Strictly Dominated"
        verdict_color = "red"
        reason = "The new strategy is more expensive and less effective. Reject immediately."
    
    elif avg_diff_effect >= 0 and avg_diff_cost <= 0:
                verdict = f"Strategy '{name_a}' is Strictly Dominant"
                verdict_color = "green"
                reason = f"The new strategy is cheaper and more effective. Highly recommended."
    
    elif nmb_avg > 0:
                verdict = f"Strategy '{name_a}' is Cost-Effective"
                verdict_color = "blue"
                reason = f"The clinical gains justify the investment based on the {currency_symbol}{wtp} threshold."
    
    else:
                verdict = f"Strategy '{name_a}' is Not Cost-Effective"
                verdict_color = "orange"
                reason = f"The clinical gains do NOT justify the investment at the {currency_symbol}{wtp} threshold."
        # 3. Displaying the Verdict Card
    st.info(f"### {verdict}\n{reason}")
    
    # 4. Key Metrics at a Glance
    m1, m2, m3 = st.columns(3)
    m1.metric("Average ICER", f"{currency_symbol}{avg_icer:,.0f}")
    m2.metric("Confidence Level", f"{p_ce:.1f}%")
    m3.metric("Decision Status", "High Value" if p_ce > 80 else "Review Required")
    # Displaying the Verdict Card
    st.info(f"### {verdict}\n{reason}")
    
    # Key Metrics at a Glance
    m1, m2, m3 = st.columns(3)
    m1.metric("Average ICER", f"₹{avg_icer:,.0f}")
    m2.metric("Confidence Level", f"{p_ce:.1f}%")
    m3.metric("Decision Status", "High Value" if p_ce > 80 else "Review Required")
    st.divider()
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Distribution", "🎯 CE Plane", "🌪️ Tornado Analysis", "💾 Export"])
    with tab1:
            fig1, ax1 = plt.subplots(figsize=(10, 4))
            sns.kdeplot(c_a, fill=True, label=name_a, color="#1f77b4")
            sns.kdeplot(c_b, fill=True, label=name_b, color="#ff7f0e")
            st.pyplot(fig1)
            # --- Interpretation for the Distribution Chart ---
            with st.expander("💡 How to interpret this distribution"):
                st.markdown("""
                **What is this showing?**  
                 This chart displays the probability distribution of our 10,000 simulated iterations. Because healthcare data is rarely exact, this shows us the *range* of likely outcomes rather than just a single average number.
                
                * **The Peak:** The highest point of the curve is the most likely expected value.
                * **The Width:** This represents uncertainty. A wider, flatter curve means the data is highly variable and unpredictable. A narrow, tall curve means we are very confident in the outcome.
                * **The Overlap:** If the curves for Strategy A and Strategy B heavily overlap, it indicates a high probability that they will perform identically in the real world.
                """)
    
    with tab2:
            fig2, ax2 = plt.subplots(figsize=(8, 5))
            plt.scatter(inc_o, inc_c, alpha=0.1, color='purple', s=1)
            x_lim = np.array(plt.xlim())
            plt.plot(x_lim, wtp * x_lim, color='red', linestyle='--')
            plt.axhline(0, color='black', lw=1); plt.axvline(0, color='black', lw=1)
            st.pyplot(fig2)
            # --- Interpretation for the CE Plane Chart ---
            with st.expander("💡 How to interpret the CE Plane"):
                st.markdown("""
                **What is this showing?**  
                The Cost-Effectiveness (CE) Plane plots the *difference* in cost against the *difference* in effectiveness for all 10,000 simulations. Each purple dot represents one simulated patient population.
            
                * **The 4 Quadrants:**
                * **Bottom-Right (South-East):** The new strategy is cheaper *and* more effective. (This is a "no-brainer" win!)
                * **Top-Left (North-West):** The new strategy is more expensive *and* less effective. (Reject immediately!)
                * **Top-Right (North-East):** The new strategy is more effective but costs more. (Trade-off zone).
                * **Bottom-Left (South-West):** The new strategy is less effective but saves money.
                * **The Red Dashed Line:** This represents your Willingness-to-Pay (WTP) threshold. Any purple dot that falls *below and to the right* of this line is a scenario where the new strategy is officially Cost-Effective!
                """)
    
    with tab3:
            st.subheader("One-Way Sensitivity Analysis")
            # Simplified Tornado Logic: Varying main params by 20%
            params = ['Cost of Strategy A', 'Effectiveness of A', 'Failure Cost']
            # ICER swings (calculated on means for simplicity)
            # Check to avoid dividing by zero if effectiveness is identical
            diff_val = val_a - val_b
            if diff_val == 0:
                base_icer = 0
            else:
                base_icer = (cost_a - cost_b) / diff_val
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
            # --- Interpretation for the CE Plane Chart ---
            with st.expander("💡 How to interpret the CE Plane"):
                st.markdown("""
                **What is this showing?**  
                The Cost-Effectiveness (CE) Plane plots the *difference* in cost against the *difference* in effectiveness for all 10,000 simulations. Each purple dot represents one simulated patient population.
            
                * **The 4 Quadrants:**
                * **Bottom-Right (South-East):** The new strategy is cheaper *and* more effective. (This is a "no-brainer" win!)
                * **Top-Left (North-West):** The new strategy is more expensive *and* less effective. (Reject immediately!)
                * **Top-Right (North-East):** The new strategy is more effective but costs more. (Trade-off zone).
                * **Bottom-Left (South-West):** The new strategy is less effective but saves money.
                * **The Red Dashed Line:** This represents your Willingness-to-Pay (WTP) threshold. Any purple dot that falls *below and to the right* of this line is a scenario where the new strategy is officially Cost-Effective!
                """)

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
