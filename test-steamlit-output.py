from datetime import datetime
import pandas as pd
import streamlit as st
import plots
import json



with open('config.json') as f:
    config = json.load(f)

default_tariff_rate = config.get("default_tariff_rate", 3.2)  # Default to 3.2 if not found

# --- Sample Data ---
machinery = {
    "Condenser Tube Cleaning of Chillers":  {
        "NP": [
            "WCC-N-1-1",
            "WCC-N-1-2",
            "WCC-N-1-3",
            "WCC-N-1-4",
            "WCC-N-2-1",
            "WCC-N-2-2",
            "WCC-N-2-3",
            "WCC-N-2-4",
            "WCC-N-2-5",
            "WCC-N-2-6",
            "WCC-N-2-7",
            "WCC-N-2-8",
            "WCC-N-3-1",
            "WCC-N-3-2",
            "WCC-N-3-3",
        ],
        "SP": [
            "WCC-S-1-1",
            "WCC-S-1-2",
            "WCC-S-1-3",
            "WCC-S-1-4",
            "WCC-S-1-5",
            "WCC-S-2-2",
            "WCC-S-2-3",
            "WCC-S-3-2",
            "WCC-S-3-3",
        ]
    },
    "Substation Heat Exchangers":  {
        "NP": [
            '1A1 HX1',
            '1A1 HX2',
            '1B1 HX1',
            '1B1 HX2',
            '1D4 HX1',
            '1D4 HX2',
            '1A3 HX1',
            '1A3 HX2',
            '1A4 HX1',
            '1A4 HX2',
            'KTS HX1',
            'KTS HX2',
            '1N1 HX1',
            '1N1 HX2',
            '1N1 HX3',
            'TKW HX1',
            'TKW HX2',
            '1A2 HX1',
            '1A2 HX2',
            '1C1 HX1',
            '1C1 HX2',
            '1D3 HX1',
            '1D3 HX2',
            '1D3 HX3',
            '1F2 HX1',
            '1F2 HX2',
            '1F2 HX3',
            '1F2 HX4',
            '1F2 HX5',
            '1E2A HX1',
            '1E2A HX2',
            '1E2A HX3',
            '1E2B HX1',
            '1E2B HX2',
            '1E2B HX3',
            '1P3-ADB HX1',
            '1P3-ADB HX2',
            '1P3-KVB HX1',
            '1P3-KVB HX2',
            '1F1-Retail HX1',
            '1F1-Retail HX2',
            '1F1-GIC HX1',
            '1F1-GIC HX2',
        ],
        "SP": [
            "3C1-1 HX1",
            "3C1-1 HX2",
            "3C1-1 HX3",
            "3C1-2 HX1",
            "3C1-2 HX2",
            "3C1-2 HX3",
            "4D3-1 HX1",
            "4D3-1 HX2",
            "4D3-2 HX1",
            "4D3-2 HX2",
            "4D3-3 HX1",
            "4D3-3 HX2",
            "4D3-4 HX1",
            "4D3-4 HX2",
        ]
    },
    "Chiller Motor Vibrations":{
        "NP": [
            "WCC-N-1-1",
            "WCC-N-1-2",
            "WCC-N-1-3",
            "WCC-N-1-4",
            "WCC-N-2-1",
            "WCC-N-2-2",
            "WCC-N-2-3",
        ],
        "SP": [
            "WCC-S-1-1",
            "WCC-S-1-2",
            "WCC-S-1-3",
            "WCC-S-1-4",
            "WCC-S-1-5",
            "WCC-S-2-2",
            "WCC-S-2-3",
        ]
    }
}

st.markdown("""
    <style>
    html, body, .stApp {
        background-color: #191919 !important;
        width: 100vw;
        height: 100vh;
        overflow: hidden !important;
    }
    .block-container {
        max-width: 1280px !important;
        min-width: 1280px !important;
        width: 1280px !important;
        margin: auto;
        padding: 32px 64px 32px 64px;
        background: #222;
        border-radius: 10px;
        box-shadow: 0 0 32px #111;
    }
    h1, h2, h3, h4, h5, h6, p, li, label, div, span {
        color: #fff !important;
    }
    .highlight {
        color: orange !important;
        font-weight: bold;
    }
    [data-baseweb="tab-list"] > button[aria-selected="true"] {
        color: orange !important;
        border-bottom: 3px solid orange !important;
    }
    .multi-row-tabs {
        display: flex;
        flex-wrap: wrap; /* Allow tabs to wrap */
        gap: 10px; /* Add some space between tabs */
    }
    .multi-row-tabs .stTabs {
        flex: 1 0 150px; /* Allow tabs to grow and shrink */
        min-width: 120px; /* Minimum width for each tab */
    }
    .stMetric {
        background: #2a2a2a !important;
        border-radius: 7px;
        padding: 15px 0 15px 0;
        margin-bottom: 12px;
        box-shadow: 0 0 4px #111;
        font-size: 2rem;
    }
    .stTabs {
        margin-bottom: 20px !important;
    }
    .stAppHeader {
        visibility: hidden;
    }
    .real_time_clock {
        color: orange;
    }
    </style>
""", unsafe_allow_html=True)

st.title("Preventive Maintenance Dashboard")

@st.fragment(run_every="1s")
def display_live_clock():
    now = datetime.now()
    current_time_str = now.strftime("%H:%M:%S")

    # Use Markdown with HTML for a large, clear display
    st.markdown(f"<h1 >{current_time_str}</h1>", unsafe_allow_html=True)
display_live_clock()



# ---- Overview in ONE ROW ----
# st.markdown("#### <span class='highlight'>Overview</span>", unsafe_allow_html=True)
# overview_cols = st.columns(3)
# overview_cols[0].metric("Total Machines", 7)
# overview_cols[1].metric("Due for Maintenance", 2)
# overview_cols[2].metric("Maintenances (30d)", 3)

def display_machine_image(machine_type):
    # Replace these paths with your actual image paths
    image_paths = {
        "NP": "plot/input/img.png",  # Path for NP image
        "SP": "plot/input/img.png"   # Path for SP image
    }
    return image_paths.get(machine_type, "")

def get_tab_icon(category):
    icons = {
        "NP": "🛠️",  # Icon for NP
        "SP": "⚙️",   # Icon for SP
    }
    return icons.get(category, "")

tabs = st.tabs(list(machinery.keys()))
for i, part in enumerate(machinery):
    with tabs[i]:
        st.markdown(f"<span class='highlight'>{part}</span>", unsafe_allow_html=True)
        machine_tabs = st.tabs(list(machinery[part].keys()))

        for j, category in enumerate(machinery[part]):
            with machine_tabs[j]:
                if i == 0:
                    tariff_rate = st.number_input("Enter Tariff Rate (per kWh)",
                                                  min_value=0.0,
                                                  format="%.2f",
                                                  value=default_tariff_rate,
                                                  key=f"tariff_rate_{i}_{j}")
                    st.write(f"The entered tariff rate is: {tariff_rate} per kWh.")
                    selected_machine = st.selectbox("Select Machine", machinery[part][category])
                    dates = pd.date_range(end=pd.Timestamp.today(), periods=12)
                    st.markdown("<div class='multi-row-tabs'>", unsafe_allow_html=True)
                    st.markdown(
                        f"""
                                       <div style='font-size:22px; line-height:1.4;'>
                                       <b>Machine:</b> <span style='color:orange'>{selected_machine}</span><br>
                                       <b>Next Maintenance:</b> <span style='color:orange'>{plots.predicted_end_date.date()}</span><br>
                                       <b>Last Maintenance:</b> {plots.start_date.date()}<br>
                                       </div>
                                       """,
                        unsafe_allow_html=True
                    )
                    plots.plot_wcc_charts(st,plots.results_df, plots.start_date, plots.predicted_end_date, plots.current_date,
                                          plots.target_cost, plots.current_date_running_hours,key_prefix=f"chart_{i}_{j}")
                if i == 1:
                    selected_machine = st.selectbox("Select Heat Exchangers", machinery[part][category])
                    st.markdown("<div class='multi-row-tabs'>", unsafe_allow_html=True)
                    st.markdown(
                        f"""
                                       <div style='font-size:22px; line-height:1.4;'>
                                       <b>Heat Exchangers:</b> <span style='color:orange'>{selected_machine}</span><br>
                                       <b>Last Maintenance:</b> {plots.ss_start_date}<br>
                                       </div>
                                       """,
                        unsafe_allow_html=True
                    )
                    plots.plot_ss_charts(st, plots.results_df, plots.start_date, plots.predicted_end_date, plots.current_date,
                                          plots.target_cost, plots.current_date_running_hours, key_prefix=f"chart_{i}_{j}")
                if i == 2:
                    selected_machine = st.selectbox("Select Chillers", machinery[part][category])
                    dates = pd.date_range(end=pd.Timestamp.today(), periods=12)
                    st.markdown("<div class='multi-row-tabs'>", unsafe_allow_html=True)
                    st.markdown(
                        f"""
                                                         <div style='font-size:22px; line-height:1.4;'>
                                                         <b>Chiller:</b> <span style='color:orange'>{selected_machine}</span><br>
                                                         <b>Next Maintenance:</b> <span style='color:orange'>{plots.predicted_end_date.date()}</span><br>
                                                         <b>Last Maintenance:</b> {plots.start_date.date()}<br>
                                                         </div>
                                                         """,
                        unsafe_allow_html=True
                    )
                    plots.plot_vib_charts(st, plots.results_df, plots.start_date, plots.predicted_end_date,
                                         plots.current_date,
                                         plots.target_cost, plots.current_date_running_hours,
                                         key_prefix=f"chart_{i}_{j}")

st.markdown("""
    <style>
    #MainMenu, footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)