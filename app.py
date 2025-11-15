import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from collections import Counter

from resonanceX.utils import load_exoplanet_data
from resonanceX.detector import detect_resonances_in_system
from resonanceX.simulator import simulate_orbits
from resonanceX.resonance import detect_resonances
from resonanceX.visualizer import create_orbit_animation, plot_resonances
from resonanceX.trappist_sim import simulate_trappist1, animate_simulation

st.set_page_config(page_title="resonanceX", layout="wide")
st.title("resonanceX: Exoplanet Resonance Explorer")

# Sidebar controls
st.sidebar.header("Configuration")
csv_path = st.sidebar.text_input("CSV Path", "datasets/nasa_exoplanets.csv")
tolerance = st.sidebar.slider("Resonance Tolerance", 0.01, 0.2, 0.05)
uploaded_file = st.sidebar.file_uploader("Upload your own CSV", type="csv")

# Load data
try:
    df = pd.read_csv(uploaded_file) if uploaded_file else load_exoplanet_data(csv_path)
except Exception as e:
    st.error(f"Failed to load dataset: {e}")
    st.stop()

# Tabs
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "Overview", "Dataset Summary", "Resonance Analysis",
    "Discovery Insights", "N-Body Simulation",
    "TRAPPIST-1 Simulator", "Raw Dataset"
])

with tab1:
    st.subheader("What Are Orbital Resonances?")
    st.markdown("""
    Orbital resonances occur when two or more planets orbit their star in near-integer ratios.
    These patterns can reveal gravitational interactions, migration history, and system stability.

    This app helps you explore resonances using real exoplanet data from NASA.
    """)

with tab2:
    st.subheader("Dataset Summary")
    st.metric("Total Planets", len(df))
    st.metric("Total Systems", df['hostname'].nunique())
    st.metric("Discovery Methods", df['discoverymethod'].nunique())
    with st.expander("Preview Dataset"):
        st.dataframe(df[['hostname', 'pl_letter', 'pl_orbper', 'discoverymethod']].head(20))

with tab3:
    st.subheader("Resonance Detection")
    if st.button("Run Resonance Analysis"):
        try:
            results = detect_resonances_in_system(df, tolerance)
            st.success(f"{len(results)} resonance pairs found in {len(set(r[0] for r in results))} systems.")

            top_systems = Counter([r[0] for r in results]).most_common(5)
            st.markdown("Most Resonant Systems")
            for system, count in top_systems:
                st.write(f"{system}: {count} pairs")

            with st.expander("Resonance Pairs"):
                for system, p1, p2, ratio in results:
                    st.write(f"{system}: {p1:.2f} vs {p2:.2f} ~ {ratio}:1")

            if results:
                fig = plot_resonances([(p1, p2, ratio) for _, p1, p2, ratio in results])
                st.pyplot(fig)
            else:
                st.warning("No resonances detected.")
        except Exception as e:
            st.error(f"Error during analysis: {e}")

with tab4:
    st.subheader("Discovery Insights")
    if 'discoverymethod' in df.columns:
        method_counts = df['discoverymethod'].value_counts()
        st.write("Discovery Methods")
        st.bar_chart(method_counts)
    if 'disc_year' in df.columns:
        year_counts = df['disc_year'].value_counts().sort_index()
        st.write("Discoveries Over Time")
        st.line_chart(year_counts)

with tab5:
    st.subheader("N-Body Simulation Demo")

    valid_systems = df.groupby('hostname').filter(
        lambda x: x['pl_orbper'].dropna().shape[0] >= 2
    )['hostname'].unique()

    if len(valid_systems) == 0:
        st.warning("No systems with enough orbital period data available.")
    else:
        selected_system = st.selectbox("Choose a system", sorted(valid_systems))
        system_planets = df[(df['hostname'] == selected_system) & df['pl_orbper'].notna()]
        available_planets = system_planets['pl_letter'].tolist()

        selected_planets = st.multiselect(
            "Select planets to include in the simulation",
            options=available_planets,
            default=available_planets
        )

        use_dynamic_scaling = st.checkbox("Enable dynamic scaling", value=True)
        use_resonance = st.checkbox("Simulate resonant chain (e.g. TRAPPIST-1)", value=False)
        show_trails = st.checkbox("Show orbit trails", value=True)
        show_resonance_plot = st.checkbox("Show resonance plot", value=True)

        if len(selected_planets) < 2:
            st.warning("Please select at least two planets to run the simulation.")
        else:
            filtered_planets = system_planets[system_planets['pl_letter'].isin(selected_planets)]
            periods = filtered_planets['pl_orbper'].tolist()

            if 'pl_bmassj' in filtered_planets.columns:
                masses = filtered_planets['pl_bmassj'].fillna(0.001).tolist()
                masses = [m * 0.0009543 if m > 0 else 0.001 for m in masses]
            else:
                masses = [0.001] * len(periods)

            st.write(f"Simulating {len(periods)} planets in {selected_system}: {', '.join(selected_planets)}")

            duration = st.slider("Simulation Duration (days)", 10, 1000, 300)
            steps = st.slider("Simulation Steps", 100, 5000, 1000)

            if st.button("Run N-Body Simulation"):
                try:
                    positions = simulate_orbits(periods, masses, duration, steps, use_resonant_chain=use_resonance)

                    if not positions or not isinstance(positions, list):
                        st.error("Simulation returned no data.")
                    else:
                        st.write("Sample orbit data:", positions[0][:5])

                        fig_orbit = create_orbit_animation(
                            positions, selected_planets,
                            dynamic_scaling=use_dynamic_scaling,
                            show_trails=show_trails
                        )

                        if isinstance(fig_orbit, go.Figure):
                            st.plotly_chart(fig_orbit)
                        else:
                            st.error("Orbit animation did not return a valid Plotly figure.")

                        if show_resonance_plot:
                            resonance_pairs = detect_resonances(periods)
                            if resonance_pairs:
                                with st.expander("View Resonance Plot"):
                                    fig_resonance = plot_resonances(resonance_pairs)
                                    st.pyplot(fig_resonance)
                            else:
                                st.warning("No resonance pairs found.")

                except Exception as e:
                    import traceback
                    st.error("Simulation error:")
                    st.text(traceback.format_exc())

with tab6:
    st.subheader("TRAPPIST-1 Orbital Simulator")
    if st.button("Run TRAPPIST-1 Simulation"):
        with st.spinner("Simulating orbital dynamics..."):
            sol, masses, periods = simulate_trappist1()
            animate_simulation(sol, masses, periods)

with tab7:
    st.subheader("Raw Dataset")
    st.dataframe(df)
