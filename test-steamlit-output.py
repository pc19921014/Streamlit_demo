import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import plots
import json
import os
import re
import base64



with open('config.json') as f:
    config = json.load(f)

default_tariff_rate = config.get("default_tariff_rate", 3.2)  # Default to 3.2 if not found

# Machine selection card sizing (adjust these values as needed)
MACHINE_IMAGE_WIDTH_PX = 200
MACHINE_IMAGE_HEIGHT_PX = 200
MACHINE_CARD_COLUMNS = 4
MACHINE_CARDS_PER_PAGE = 12
MACHINE_TITLE_FONT_PX = 20
TITLE_FONT_SIZE_PX = 50
TITLE_HEIGHT_PX = 130

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
            # "WCC-N-3-1",
            # "WCC-N-3-2",
            # "WCC-N-3-3",
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
            # '1E2A HX1',
            # '1E2A HX2',
            # '1E2A HX3',
            # '1E2B HX1',
            # '1E2B HX2',
            # '1E2B HX3',
            # '1P3-ADB HX1',
            # '1P3-ADB HX2',
            # '1P3-KVB HX1',
            # '1P3-KVB HX2',
            # '1F1-Retail HX1',
            # '1F1-Retail HX2',
            # '1F1-GIC HX1',
            # '1F1-GIC HX2',
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
        font-size: 18px !important;
        width: 100vw;
        min-height: 100vh;
        overflow-x: hidden !important;
        overflow-y: auto !important;
    }
    p, li, label, div, span, input, textarea, select, button {
        font-size: 1.08rem !important;
    }
    [data-testid="stHeadingWithActionElements"] h1 {
        font-size: 50px !important;
        line-height: 1.15 !important;
    }
    h2 { font-size: 2rem !important; }
    h3 { font-size: 1.6rem !important; }
    [data-testid="stMarkdownContainer"] p {
        font-size: 1.08rem !important;
    }
    .block-container {
        max-width: 100% !important;
        min-width: 0 !important;
        width: 100% !important;
        margin: auto;
        padding: clamp(12px, 2.5vw, 32px) clamp(12px, 4vw, 64px);
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
    h2.machine-title {
        font-size: 1.875rem !important;
        font-weight: 600 !important;
        margin: 0 0 0.35em 0 !important;
        line-height: 1.2 !important;
    }
    [data-baseweb="tab-list"] > button[aria-selected="true"] {
        color: orange !important;
        border-bottom: 3px solid orange !important;
        border-color: orange !important;
    }
    [data-baseweb="tab-highlight"] {
        background-color: orange !important;
    }
    [data-baseweb="tab-border"] {
        background-color: rgba(140, 140, 140, 0.55) !important;
    }
    [data-baseweb="tab-list"] > button {
        color: #ffcc80 !important;
        font-size: 1.08rem !important;
        font-weight: 600 !important;
    }
    [data-baseweb="tab-list"] > button:hover {
        color: orange !important;
    }
    /* Segmented controls (System / Category) in orange theme */
    [data-baseweb="button-group"] button {
        border-color: #7a7a7a !important;
        color: #ffcc80 !important;
        font-size: 1.05rem !important;
    }
    [data-baseweb="button-group"] button[aria-pressed="true"] {
        background-color: orange !important;
        border-color: orange !important;
        color: #191919 !important;
        font-weight: 700 !important;
    }
    /* Global button recolor to orange theme */
    .stButton > button {
        border: 1px solid #7a7a7a !important;
        color: orange !important;
        font-size: 1.08rem !important;
    }
    .stButton > button:hover {
        border-color: #9a9a9a !important;
        color: #ffb347 !important;
        box-shadow: 0 0 0 1px rgba(160, 160, 160, 0.22) inset !important;
    }
    .stButton > button[kind="primary"] {
        background-color: orange !important;
        color: #191919 !important;
        font-weight: 700 !important;
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
        font-size: 2.2rem;
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
    /* Machine icon button styling (anchored right before each machine button) */
    div[data-testid="stElementContainer"]:has(.machine-card-block) {
        display: flex !important;
        justify-content: center !important;
        padding-left: 0 !important;
        padding-right: 0 !important;
    }
    div[data-testid="stElementContainer"]:has(.machine-button-anchor) + div[data-testid="stElementContainer"] {
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        padding-left: 0 !important;
        padding-right: 0 !important;
        width: 100% !important;
        text-align: center !important;
    }
    div[data-testid="stElementContainer"]:has(.machine-button-anchor) + div[data-testid="stElementContainer"] button {
        border-radius: 8px !important;
        transition: all 0.3s ease !important;
        padding: 8px 12px !important;
        font-size: 1.05rem !important;
        min-height: 60px !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 5px !important;
    }
    div[data-testid="stElementContainer"]:has(.machine-button-anchor) + div[data-testid="stElementContainer"] .stButton {
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        width: 100% !important;
        margin-left: auto !important;
        margin-right: auto !important;
        margin-top: -6px !important;
    }
    div[data-testid="stElementContainer"]:has(.machine-button-anchor) + div[data-testid="stElementContainer"] .stButton > button {
        display: block !important;
        margin: 0 auto !important;
        box-sizing: border-box !important;
        width: 100% !important;
        max-width: 100% !important;
        padding-left: 0 !important;
        padding-right: 0 !important;
        text-align: center !important;
        position: static !important;
    }
    div[data-testid="stElementContainer"]:has(.machine-button-anchor) + div[data-testid="stElementContainer"] button:hover {
        transform: none !important;
        box-shadow: 0 4px 8px rgba(255, 165, 0, 0.3) !important;
    }
    .machine-card-block img {
        margin-bottom: 5px !important;
        border-radius: 4px !important;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown(
    f"""
    <style>
    .machine-card-block {{
        width: {MACHINE_IMAGE_WIDTH_PX}px !important;
        margin: 0 auto 4px auto !important;
    }}
    div[data-testid="stElementContainer"]:has(.machine-button-anchor) + div[data-testid="stElementContainer"] .stButton > button {{
        width: {MACHINE_IMAGE_WIDTH_PX}px !important;
        min-width: {MACHINE_IMAGE_WIDTH_PX}px !important;
        max-width: {MACHINE_IMAGE_WIDTH_PX}px !important;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

components.html(
    f"""
    <div style="
      font-size: {TITLE_FONT_SIZE_PX}px;
      line-height: 1.15;
      font-weight: 700;
      margin: 0 0 0.35rem 0;
      color: #fff;
      font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    ">
      Preventive Maintenance Dashboard
    </div>
    """,
    height=TITLE_HEIGHT_PX,
)


def display_live_clock():
    """UTC+8 clock ticks in the iframe only (no 1 Hz Streamlit reruns).

    A @st.fragment(run_every="1s") clock overloads the ForwardMsg cache and can
    trigger: Cached ForwardMsg MISS websocket errors.
    """
    components.html(
        """
        <!DOCTYPE html>
        <html>
        <head>
          <style>
            body { margin: 0; background: transparent; font-family: system-ui, sans-serif; }
            #clock {
              font-size: 1.75rem;
              font-weight: 600;
              color: #ffffff;
              letter-spacing: 0.02em;
            }
          </style>
        </head>
        <body>
          <div id="clock"></div>
          <script>
            function pad(n) { return String(n).padStart(2, "0"); }
            function tick() {
              var now = new Date();
              var utcMs = now.getTime() + (now.getTimezoneOffset() * 60000);
              var cn = new Date(utcMs + 8 * 3600000);
              var s = cn.getFullYear() + "-" + pad(cn.getMonth() + 1) + "-" + pad(cn.getDate())
                + " " + pad(cn.getHours()) + ":" + pad(cn.getMinutes()) + ":" + pad(cn.getSeconds());
              document.getElementById("clock").textContent = s;
            }
            tick();
            setInterval(tick, 1000);
          </script>
        </body>
        </html>
        """,
        height=72,
        scrolling=False,
    )


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
        "NP": "frame0/chiller_grey_big.png",  # Path for NP image
        "SP": "frame0/chiller_grey_big.png"   # Path for SP image
    }
    return image_paths.get(machine_type, "")

def get_tab_icon(category):
    icons = {
        "NP": "🛠️",  # Icon for NP
        "SP": "⚙️",   # Icon for SP
    }
    return icons.get(category, "")

def get_machine_result_path(machine_name):
    """Map machine name to its result folder path"""
    # Extract the pattern from machine name (e.g., "WCC-N-1-1" -> "NP_1_1")
    # Pattern: WCC-N-X-Y or WCC-S-X-Y -> NP_X_Y or SP_X_Y
    match = re.match(r'WCC-([NS])-(\d+)-(\d+)', machine_name)
    if match:
        prefix = "NP" if match.group(1) == "N" else "SP"
        section = match.group(2)
        unit = match.group(3)
        folder_name = f"{prefix}_{section}_{unit}"
        result_path = f"plot/input/chiller result/{folder_name}/prediction_results_{folder_name}.csv"
        
        if os.path.exists(result_path):
            return result_path
    
    return None

def get_substation_result_paths(substation_name, area):
    """Map substation name to prediction + valve data paths."""
    match = re.match(r"([\w-]+)\s+HX(\d+)", substation_name)
    if not match:
        return {"prediction_path": None, "valve_path": None, "hx_num": "1"}

    substation = match.group(1)
    hx_number = int(match.group(2))
    area_upper = (area or "").upper()
    substation_for_prediction = substation.replace("-", "_")
    prediction_filename = (
        f"prediction_results_{area_upper}_{substation_for_prediction}_HX{hx_number}.csv"
    )
    prediction_path = (
        f"plot/input/substation_prediction_bundle/{area_upper}/"
        f"{area_upper}_{substation_for_prediction}/{prediction_filename}"
    )
    valve_name = f"V-{hx_number:02d}_HX{hx_number}"
    valve_path = (
        f"plot/input/valve_analysis_plots_selected_SS/{area_upper}/{substation}/"
        f"{valve_name}/{valve_name}_valve_vs_all_metrics_preprocessed.csv"
    )
    return {
        "prediction_path": prediction_path if os.path.exists(prediction_path) else None,
        "valve_path": valve_path if os.path.exists(valve_path) else None,
        "hx_num": str(hx_number),
    }

def load_machine_data(machine_name):
    """Load data for a specific machine from its result folder (cached, column-pruned)."""
    csv_path = get_machine_result_path(machine_name)
    if not csv_path or not os.path.isfile(csv_path):
        return None
    try:
        bundle = plots.load_prediction_bundle(csv_path, os.path.getmtime(csv_path))
        if bundle and bundle.get("overflow"):
            return {"overflow": True}
        if not bundle or "df" not in bundle or bundle["df"] is None or bundle["df"].empty:
            return None
        return bundle
    except Exception as e:
        st.error(f"Error loading data for {machine_name}: {str(e)}")
        return None

def load_substation_data(substation_name, area):
    """Load substation prediction + valve CSVs for the HX unit."""
    paths = get_substation_result_paths(substation_name, area)
    prediction_path = paths["prediction_path"]
    valve_path = paths["valve_path"]
    hx_num = paths["hx_num"]
    if not prediction_path or not valve_path:
        return None
    try:
        bundle = plots.load_substation_bundle(
            prediction_path,
            valve_path,
            hx_num,
            os.path.getmtime(prediction_path),
            os.path.getmtime(valve_path),
        )
        if not bundle or "df" not in bundle or bundle["df"] is None or bundle["df"].empty:
            return None
        return bundle
    except Exception as e:
        st.error(f"Error loading substation data for {substation_name}: {str(e)}")
        return None


def get_vibration_result_path(machine_name):
    """Map machine name to vibration movement dataset path."""
    match = re.match(r"WCC-([NS])-(\d+)-(\d+)", machine_name)
    if match:
        area = "np" if match.group(1) == "N" else "sp"
        section = match.group(2)
        unit = match.group(3)
        machine_segment = f"{match.group(1)}-{section}-{unit}"
        candidate_paths = [
            (
                f"plot/input/valid_movement_only_vib/{area}/"
                f"{machine_segment}/data/processed_valid_movement_chiller.csv"
            ),
        ]
        for result_path in candidate_paths:
            if os.path.exists(result_path):
                return result_path
    return None


def load_vibration_data(machine_name):
    """Load chiller vibration movement data from valid_movement_only_vib."""
    csv_path = get_vibration_result_path(machine_name)
    if not csv_path or not os.path.isfile(csv_path):
        return None
    try:
        df = pd.read_csv(csv_path)
        if df is None or df.empty:
            return None
        return {
            "df": df,
            "start_date": None,
            "predicted_end_date": None,
            "current_date": None,
            "current_running_hour": None,
        }
    except Exception as e:
        st.error(f"Error loading vibration data for {machine_name}: {str(e)}")
        return None

@st.cache_data(show_spinner=False)
def get_resized_image_path(source_path, size_px=56):
    """Create and cache square thumbnails so image_select renders smaller icons."""
    if not source_path or not os.path.isfile(source_path):
        return source_path
    try:
        from PIL import Image

        thumb_dir = os.path.join(".streamlit_cache", "thumbnails")
        os.makedirs(thumb_dir, exist_ok=True)

        name, ext = os.path.splitext(os.path.basename(source_path))
        thumb_path = os.path.join(thumb_dir, f"{name}_{size_px}px{ext}")

        src_mtime = os.path.getmtime(source_path)
        if (not os.path.isfile(thumb_path)) or (os.path.getmtime(thumb_path) < src_mtime):
            with Image.open(source_path) as img:
                img = img.convert("RGBA")
                img.thumbnail((size_px, size_px), Image.Resampling.LANCZOS)

                canvas = Image.new("RGBA", (size_px, size_px), (0, 0, 0, 0))
                x = (size_px - img.width) // 2
                y = (size_px - img.height) // 2
                canvas.paste(img, (x, y))
                canvas.save(thumb_path)
        return thumb_path
    except Exception:
        return source_path


@st.cache_data(show_spinner=False)
def get_image_base64(source_path, _mtime):
    """Return image as base64 for lightweight HTML card rendering."""
    try:
        with open(source_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    except Exception:
        return None


def on_machine_pick(state_key, machine):
    """Apply machine selection before app rerender."""
    st.session_state[state_key] = machine


def display_machine_icons(machines, key_prefix, default_machine=None, enable_paging=True):
    """Display machines as selectable image-title blocks."""
    if not machines:
        return None
    # Initialize session state for selected machine if not exists
    state_key = f"selected_machine_{key_prefix}"
    if state_key not in st.session_state:
        st.session_state[state_key] = default_machine if default_machine else machines[0]
    
    # Load the machine icon image path based on machine type
    image_path = None
    try:
        import os
        # Use heat exchanger image for substations, chiller image for others
        if "heat_exchanger" in key_prefix:
            image_path = "plot/input/hero_callout_plate_exchanger-1.png"
        else:
            image_path = "frame0/chiller_grey_big.png"
        
        if not os.path.exists(image_path):
            image_path = None
    except OSError:
        image_path = None
    
    if image_path:
        thumbnail_path = get_resized_image_path(
            image_path,
            size_px=max(MACHINE_IMAGE_WIDTH_PX, MACHINE_IMAGE_HEIGHT_PX),
        )
        image_b64 = get_image_base64(thumbnail_path, os.path.getmtime(thumbnail_path))
        if not image_b64:
            return st.session_state[state_key]

        if enable_paging:
            page_key = f"machine_page_{key_prefix}"
            selected_pos = (
                machines.index(st.session_state[state_key])
                if st.session_state[state_key] in machines
                else 0
            )
            if page_key not in st.session_state:
                st.session_state[page_key] = selected_pos // MACHINE_CARDS_PER_PAGE

            cards_per_page = MACHINE_CARDS_PER_PAGE
            total_pages = max(1, (len(machines) + cards_per_page - 1) // cards_per_page)
            current_page = max(0, min(st.session_state[page_key], total_pages - 1))
            st.session_state[page_key] = current_page

            pager_col1, pager_col2, pager_col3 = st.columns([1, 1, 1], vertical_alignment="center")
            with pager_col1:
                clicked_prev = st.button(
                    "Prev",
                    key=f"{key_prefix}_prev_page",
                    disabled=current_page == 0,
                    use_container_width=True,
                )
            with pager_col3:
                clicked_next = st.button(
                    "Next",
                    key=f"{key_prefix}_next_page",
                    disabled=current_page >= total_pages - 1,
                    use_container_width=True,
                )

            next_page = current_page
            if clicked_prev:
                next_page = max(0, current_page - 1)
            elif clicked_next:
                next_page = min(total_pages - 1, current_page + 1)

            if next_page != current_page:
                current_page = next_page
                st.session_state[page_key] = current_page
                # Force a clean rerun so button disabled states match new page immediately.
                st.rerun()

            with pager_col2:
                st.markdown(
                    f"<div style='text-align:center; font-size:1rem; line-height:2.1rem;'>Page {current_page + 1} / {total_pages}</div>",
                    unsafe_allow_html=True,
                )

            start = current_page * cards_per_page
            end = min(start + cards_per_page, len(machines))
        else:
            start = 0
            end = len(machines)
        visible_machines = machines[start:end]
        if not visible_machines:
            return st.session_state[state_key]

        for row_start in range(0, len(visible_machines), MACHINE_CARD_COLUMNS):
            cols = st.columns(MACHINE_CARD_COLUMNS)
            row_items = visible_machines[row_start: row_start + MACHINE_CARD_COLUMNS]
            for idx, machine in enumerate(row_items):
                with cols[idx]:
                    is_selected = st.session_state[state_key] == machine
                    border_color = "orange" if is_selected else "#666"
                    overlay_bg = "rgba(255,140,0,0.35)" if is_selected else "rgba(0,0,0,0.45)"
                    st.markdown(
                        f"""
                        <div class="machine-card-block" style="width:{MACHINE_IMAGE_WIDTH_PX}px; margin:0 auto 10px auto;">
                          <div
                            style="
                              border:3px solid {border_color};
                              border-radius:10px;
                              box-sizing:border-box;
                              padding:0;
                              background:{'rgba(255,165,0,0.10)' if is_selected else 'transparent'};
                              width:{MACHINE_IMAGE_WIDTH_PX}px;
                              height:{MACHINE_IMAGE_HEIGHT_PX}px;
                              position:relative;
                              overflow:hidden;
                              box-shadow:{'0 0 14px rgba(255,165,0,0.70)' if is_selected else '0 0 4px rgba(0,0,0,0.30)'};
                              transform:none;
                              transition:all 0.18s ease;
                            "
                            title="{machine}{' (selected)' if is_selected else ''}"
                          >
                            <img
                              src="data:image/png;base64,{image_b64}"
                              style="
                                width:{MACHINE_IMAGE_WIDTH_PX}px;
                                height:{MACHINE_IMAGE_HEIGHT_PX}px;
                                object-fit:contain;
                                display:block;
                              "
                            />
                            <div style="
                              position:absolute;
                              inset:0;
                              display:flex;
                              align-items:center;
                              justify-content:center;
                              text-align:center;
                              font-size:{MACHINE_TITLE_FONT_PX}px;
                              line-height:1.1;
                              font-weight:700;
                              color:#fff;
                              text-shadow:0 1px 2px rgba(0,0,0,0.9);
                              background:{overlay_bg};
                              padding:2px;
                            ">{machine}</div>
                            {"<div style='position:absolute; top:2px; right:2px; width:12px; height:12px; border-radius:50%; background:#ffa500; color:#111; font-size:9px; font-weight:800; display:flex; align-items:center; justify-content:center;'>✓</div>" if is_selected else ""}
                          </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    st.markdown("<div class='machine-button-anchor'></div>", unsafe_allow_html=True)
                    st.button(
                        machine,
                        key=f"{key_prefix}_pick_{start + row_start + idx}",
                        type="primary" if is_selected else "secondary",
                        width=MACHINE_IMAGE_WIDTH_PX,
                        on_click=on_machine_pick,
                        args=(state_key, machine),
                    )
        return st.session_state[state_key]
    else:
        # Fallback to regular selectbox if no image available
        selected_machine = st.selectbox(
            "Select Machine",
            machines,
            index=machines.index(st.session_state[state_key]) if st.session_state[state_key] in machines else 0,
            key=f"{key_prefix}_selectbox"
        )
        st.session_state[state_key] = selected_machine
        return selected_machine

parts = list(machinery.keys())
selected_part = st.segmented_control(
    "System",
    options=parts,
    selection_mode="single",
    default=st.session_state.get("selected_part", parts[0]),
    key="selected_part",
    width="stretch",
)
if selected_part is None:
    selected_part = parts[0]
st.markdown(f"<span class='highlight'>{selected_part}</span>", unsafe_allow_html=True)

categories = list(machinery[selected_part].keys())
category_key = f"selected_category_{selected_part}"
selected_category = st.segmented_control(
    "Category",
    options=categories,
    selection_mode="single",
    default=st.session_state.get(category_key, categories[0]),
    key=category_key,
    width="stretch",
)
if selected_category is None:
    selected_category = categories[0]

i = parts.index(selected_part)
j = categories.index(selected_category)

if i == 0:
    selector_key = f"machine_{i}_{j}"
    tariff_rate = st.number_input(
        "Enter Tariff Rate (per kWh)",
        min_value=0.0,
        format="%.2f",
        value=default_tariff_rate,
        key=f"tariff_rate_{i}_{j}",
    )
    st.write(f"The entered tariff rate is: {tariff_rate} per kWh.")
    selected_machine = display_machine_icons(
        machinery[selected_part][selected_category], selector_key, enable_paging=False
    )
    machine_data = load_machine_data(selected_machine)
    if machine_data and machine_data.get("overflow"):
        st.warning("data overflow")
    elif not machine_data:
        st.info("No data")
    else:
        results_df = machine_data["df"]
        start_date = machine_data["start_date"]
        predicted_end_date = machine_data["predicted_end_date"]
        current_date = machine_data["current_date"]
        current_date_running_hours = machine_data["current_running_hour"]

        st.markdown(
            f"""
            <div style='line-height:1.4;'>
            <h2 class='machine-title'><b>Machine:</b> <span class='highlight'>{selected_machine}</span></h2>
            <p style='font-size:22px; margin:0;'><b>Next Maintenance:</b> <span class='highlight'>{predicted_end_date.date() if predicted_end_date else "N/A"}</span><br>
            <b>Last Maintenance:</b> {start_date.date() if start_date else "N/A"}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        plots.plot_wcc_charts(
            st,
            results_df,
            start_date,
            predicted_end_date,
            current_date,
            plots.TARGET_COST,
            current_date_running_hours,
            key_prefix=f"chart_{i}_{j}",
        )

elif i == 1:
    substation_machines = machinery[selected_part][selected_category]
    substation_ids = []
    for machine_name in substation_machines:
        m = re.match(r"(.+)\s+HX\d+$", machine_name)
        if m:
            substation_id = m.group(1)
            if substation_id not in substation_ids:
                substation_ids.append(substation_id)

    selected_substation = st.segmented_control(
        "Substation",
        options=substation_ids,
        selection_mode="single",
        default=st.session_state.get(
            f"substation_subcategory_{i}_{j}",
            substation_ids[0] if substation_ids else None,
        ),
        key=f"substation_subcategory_{i}_{j}",
        width="stretch",
    )
    if selected_substation is None and substation_ids:
        selected_substation = substation_ids[0]

    filtered_substations = [
        machine_name
        for machine_name in substation_machines
        if selected_substation and machine_name.startswith(f"{selected_substation} ")
    ]

    if not filtered_substations:
        st.info("No data")
        selected_machine = None
    else:
        selector_key = f"heat_exchanger_{i}_{j}_{selected_substation}"
        selected_machine = display_machine_icons(
            filtered_substations, selector_key, enable_paging=False
        )

    if selected_machine:
        hx_match = re.search(r"HX(\d+)", selected_machine)
        hx_num = hx_match.group(1) if hx_match else "1"
        substation_data = load_substation_data(selected_machine, selected_category)
        if not substation_data:
            st.info("No data")
        else:
            results_ss_df = substation_data["df"]
            valve_ss_df = substation_data["valve_df"]
            ss_start_date = substation_data["start_date"]
            ss_current_date = substation_data["current_date"]

            st.markdown(
                f"""
                <div style='line-height:1.4;'>
                <h2 class='machine-title'><b>Heat Exchangers:</b> <span class='highlight'>{selected_machine}</span></h2>
                <p style='font-size:22px; margin:0;'><b>Last Maintenance:</b> {ss_start_date.date() if ss_start_date else "N/A"}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            plots.plot_ss_charts(
                st,
                results_ss_df,
                valve_ss_df,
                ss_start_date,
                None,
                ss_current_date,
                plots.TARGET_COST,
                None,
                key_prefix=f"chart_{i}_{j}",
                hx_num=hx_num,
            )

else:
    selector_key = f"chiller_{i}_{j}"
    selected_machine = display_machine_icons(
        machinery[selected_part][selected_category], selector_key, enable_paging=False
    )
    machine_data = load_vibration_data(selected_machine)
    if not machine_data:
        st.info("No data")
        results_df = None
        start_date = None
        predicted_end_date = None
        current_date = None
        current_date_running_hours = None
    else:
        results_df = machine_data["df"]
        start_date = machine_data["start_date"]
        predicted_end_date = machine_data["predicted_end_date"]
        current_date = machine_data["current_date"]
        current_date_running_hours = machine_data["current_running_hour"]

    if machine_data:
        st.markdown(
            f"""
            <div style='line-height:1.4;'>
            <h2 class='machine-title'><b>Chiller:</b> <span class='highlight'>{selected_machine}</span></h2>
            <p style='font-size:22px; margin:0;'><b>Next Maintenance:</b> <span class='highlight'>{predicted_end_date.date() if predicted_end_date else "N/A"}</span><br>
            <b>Last Maintenance:</b> {start_date.date() if start_date else "N/A"}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        plots.plot_vib_charts(
            st,
            results_df,
            start_date,
            predicted_end_date,
            current_date,
            plots.TARGET_COST,
            current_date_running_hours,
            key_prefix=f"chart_{i}_{j}",
        )

st.markdown("""
    <style>
    #MainMenu, footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)