# HealthEconSim: Healthcare Value and Decision Suite

**HealthEconSim** is an open-source, browser-based health economic modelling and decision-support application developed for health technology assessment (HTA), economic evaluation, research, and teaching.

The application provides an accessible interface for conducting cost-effectiveness analyses without requiring users to directly program the underlying calculations.

## Live Application

**HealthEconSim:**  
https://health-econ-sim.streamlit.app/

## Key Features

- Cost-effectiveness analysis of alternative healthcare strategies
- Clinical-success and QALY-based economic evaluation
- Static decision modelling
- Temporal/Markov modelling
- Probabilistic sensitivity analysis (PSA)
- Monte Carlo simulation
- Cost-effectiveness plane
- Willingness-to-pay (WTP) threshold analysis
- Net monetary benefit calculations
- Probability of cost-effectiveness
- Tornado analysis for identifying influential parameters
- Support for multiple currencies
- Interactive browser-based interface

## Intended Use

HealthEconSim is intended to support:

- Health technology assessment
- Health economic research
- Cost-effectiveness analysis
- Decision-analytic modelling
- Academic teaching and training
- Exploratory evaluation of healthcare interventions

The software is intended for research and educational use. Results should be interpreted in conjunction with appropriate clinical, economic, and methodological expertise.

## Software

HealthEconSim is implemented in Python and deployed using Streamlit.

The source code for the software is available in this repository.

## Installation

To run the application locally:

```bash
git clone https://github.com/ric-m-pixel/health-econ-sim.git
cd health-econ-sim
pip install -r requirements.txt
streamlit run app.py
