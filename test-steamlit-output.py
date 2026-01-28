from datetime import datetime, timezone, timedelta
import pandas as pd
import streamlit as st
from streamlit_image_select import image_select
import plots
import json
import os
import re



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
    /* Machine icon button styling */
    div[data-testid*="column"] button {
        border-radius: 8px !important;
        transition: all 0.3s ease !important;
        padding: 8px 12px !important;
        font-size: 11px !important;
        min-height: 60px !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 5px !important;
    }
    div[data-testid*="column"] button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 8px rgba(255, 165, 0, 0.3) !important;
    }
    div[data-testid*="column"] img {
        margin-bottom: 5px !important;
        border-radius: 4px !important;
    }
    /* Center machine title captions in image-select component */
    [data-testid*="image-select"] p,
    [data-testid*="image-select"] div:not(:has(img)),
    [data-testid*="image-select"] span,
    [class*="image-select"] p,
    [class*="image-select"] div:not(:has(img)),
    [class*="image-select"] span,
    div:has(img) ~ p,
    div:has(img) ~ div:not(:has(img)),
    div:has(img) ~ span,
    button:has(img) ~ p,
    button:has(img) ~ div:not(:has(img)),
    button:has(img) ~ span {
        text-align: center !important;
    }
    /* Streamlit image select hover styling - highlight caption text on hover */
    /* Target image containers and their sibling caption text */
    div:has(img):hover ~ p,
    div:has(img):hover ~ div:not(:has(img)),
    div:has(img):hover ~ span,
    button:has(img):hover ~ p,
    button:has(img):hover ~ div:not(:has(img)),
    button:has(img):hover ~ span,
    div:has(> img):hover + p,
    div:has(> img):hover + div:not(:has(img)),
    div:has(> img):hover + span {
        color: orange !important;
        font-weight: bold !important;
        transition: all 0.3s ease !important;
    }
    /* Target caption text within the same container when image is hovered */
    div:has(img:hover) p:not(:has(img)),
    div:has(img:hover) div:not(:has(img)),
    div:has(img:hover) span:not(:has(img)),
    button:has(img:hover) ~ p,
    button:has(img:hover) ~ div:not(:has(img)),
    button:has(img:hover) ~ span {
        color: orange !important;
        font-weight: bold !important;
        transition: all 0.3s ease !important;
    }
    /* Target image-select component specific structure */
    [data-testid*="image-select"]:hover p,
    [data-testid*="image-select"]:hover div:not(:has(img)),
    [data-testid*="image-select"]:hover span,
    [class*="image-select"]:hover p,
    [class*="image-select"]:hover div:not(:has(img)),
    [class*="image-select"]:hover span {
        color: orange !important;
        font-weight: bold !important;
        transition: all 0.3s ease !important;
    }
    /* Target parent container when any child image is hovered */
    div:has(img:hover) {
        color: orange !important;
    }
    div:has(img:hover) > p,
    div:has(img:hover) > div:not(:has(img)),
    div:has(img:hover) > span {
        color: orange !important;
        font-weight: bold !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("Preventive Maintenance Dashboard")

@st.fragment(run_every="1s")
def display_live_clock():
    # Set timezone to UTC+8
    utc_plus_8 = timezone(timedelta(hours=8))
    now = datetime.now(utc_plus_8)
    current_date_str = now.strftime("%Y-%m-%d")
    current_time_str = now.strftime("%H:%M:%S")

    # Use Markdown with HTML for a large, clear display
    st.markdown(f"<h1>{current_date_str} {current_time_str}</h1>", unsafe_allow_html=True)
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
        result_path = f"plot/input/results/{folder_name}/prediction_results_{folder_name}.csv"
        
        if os.path.exists(result_path):
            return result_path
    
    return None

def get_substation_result_path(substation_name):
    """Map substation name to its valve analysis data folder path"""
    # Extract pattern from substation name (e.g., "1A1 HX1" -> "1A1" and "1")
    match = re.match(r'([\w-]+)\s+HX(\d+)', substation_name)
    if match:
        substation = match.group(1)
        hx_number = int(match.group(2))
        valve_name = f"V-{hx_number:02d}_HX{hx_number}"
        result_path = f"plot/input/valve_analysis_plots/{substation}/{valve_name}/cumulative_trends/{valve_name}_all_data.csv"
        
        if os.path.exists(result_path):
            return result_path
    
    return None

def load_machine_data(machine_name):
    """Load data for a specific machine from its result folder"""
    csv_path = get_machine_result_path(machine_name)
    if csv_path and os.path.exists(csv_path):
        try:
            df = pd.read_csv(csv_path, sep=',')
            if len(df) > 0:
                # Extract dates from first row (they're in row 1, index 0)
                start_date = None
                predicted_end_date = None
                current_date = None
                current_running_hour = None
                
                if 'start_date' in df.columns:
                    df['start_date'] = pd.to_datetime(df['start_date'], errors='coerce')
                    start_date = df['start_date'].iloc[0] if not pd.isna(df['start_date'].iloc[0]) else None
                
                if 'predicted_end_date' in df.columns:
                    df['predicted_end_date'] = pd.to_datetime(df['predicted_end_date'], errors='coerce')
                    predicted_end_date = df['predicted_end_date'].iloc[0] if not pd.isna(df['predicted_end_date'].iloc[0]) else None
                
                if 'current_date' in df.columns:
                    df['current_date'] = pd.to_datetime(df['current_date'], errors='coerce')
                    current_date = df['current_date'].iloc[0] if not pd.isna(df['current_date'].iloc[0]) else None
                
                if 'current_running_hour' in df.columns:
                    current_running_hour = df['current_running_hour'].iloc[0] if not pd.isna(df['current_running_hour'].iloc[0]) else None
                
                # Skip the first row (header/metadata row) and return data
                data_df = df[1:].copy() if len(df) > 1 else df.copy()
                
                return {
                    'df': data_df,
                    'start_date': start_date,
                    'predicted_end_date': predicted_end_date,
                    'current_date': current_date,
                    'current_running_hour': current_running_hour
                }
        except Exception as e:
            st.error(f"Error loading data for {machine_name}: {str(e)}")
            return None
    
    return None

def load_substation_data(substation_name):
    """Load data for a specific substation from valve_analysis_plots folder"""
    csv_path = get_substation_result_path(substation_name)
    if csv_path and os.path.exists(csv_path):
        try:
            df = pd.read_csv(csv_path, sep=',')
            if len(df) > 0:
                # Extract dates from second row (row index 1) where dates are stored
                start_date = None
                current_date = None
                
                if 'start_date' in df.columns:
                    # Dates are in row 1 (index 1)
                    start_date_val = df['start_date'].iloc[1] if len(df) > 1 else None
                    if pd.notna(start_date_val) and start_date_val != '':
                        start_date = pd.to_datetime(start_date_val, errors='coerce')
                
                if 'current_date' in df.columns:
                    current_date_val = df['current_date'].iloc[1] if len(df) > 1 else None
                    if pd.notna(current_date_val) and current_date_val != '':
                        current_date = pd.to_datetime(current_date_val, errors='coerce')
                
                # Skip the first two rows (header and metadata row) and return data
                data_df = df[2:].copy() if len(df) > 2 else df[1:].copy() if len(df) > 1 else df.copy()
                
                return {
                    'df': data_df,
                    'start_date': start_date,
                    'predicted_end_date': None,  # Not available in substation data
                    'current_date': current_date,
                    'current_running_hour': None  # Can be calculated from running_hour column if needed
                }
        except Exception as e:
            st.error(f"Error loading substation data for {substation_name}: {str(e)}")
            return None
    
    return None

def display_machine_icons(machines, key_prefix, default_machine=None):
    """Display machines as clickable image icon buttons using streamlit-image-select"""
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
    except:
        image_path = None
    
    if image_path:
        # Prepare images and captions for image_select
        # Since all machines use the same image, create a list with the same image repeated
        images = [image_path] * len(machines)
        captions = machines
        
        # Find the index of the currently selected machine
        try:
            default_index = machines.index(st.session_state[state_key])
        except ValueError:
            default_index = 0
        
        # Use streamlit-image-select component
        selected_index = image_select(
            label="Select Machine",
            images=images,
            captions=captions,
            use_container_width=False,
            return_value="index",
            key=f"{key_prefix}_image_select",
            index=default_index
        )
        
        # Add JavaScript to highlight caption text on hover
        hover_script = f'''
        <script>
        (function() {{
            function setupHoverHighlight() {{
                // Find all image-select items - try multiple selectors
                const selectors = [
                    '[data-testid*="image-select"]',
                    '[class*="image-select"]',
                    '[class*="imageSelect"]',
                    'button[data-testid*="image"]',
                    'div[role="button"]'
                ];
                
                let imageSelectItems = [];
                selectors.forEach(selector => {{
                    const items = document.querySelectorAll(selector);
                    items.forEach(item => {{
                        if (!imageSelectItems.includes(item)) {{
                            imageSelectItems.push(item);
                        }}
                    }});
                }});
                
                imageSelectItems.forEach(function(item) {{
                    // Skip if already has event listeners
                    if (item.hasAttribute('data-hover-setup')) {{
                        return;
                    }}
                    item.setAttribute('data-hover-setup', 'true');
                    
                    item.addEventListener('mouseenter', function() {{
                        // Find the parent container
                        let container = this.closest('div[class*="image"], div[data-testid*="image"], div[class*="st"]');
                        if (!container) container = this.parentElement;
                        
                        // Find caption text - look for text elements that are not images
                        const allElements = container ? container.querySelectorAll('*') : this.querySelectorAll('*');
                        allElements.forEach(function(el) {{
                            const text = el.textContent ? el.textContent.trim() : '';
                            const hasImage = el.querySelector('img') || el.tagName === 'IMG';
                            
                            // If it's a text element with content and no image, highlight it
                            if (text && !hasImage && (el.tagName === 'P' || el.tagName === 'DIV' || el.tagName === 'SPAN' || el.tagName === 'LABEL')) {{
                                // Check if it's likely a caption (short text, below image)
                                if (text.length < 50 && text.length > 0) {{
                                    el.style.color = 'orange';
                                    el.style.fontWeight = 'bold';
                                    el.style.textAlign = 'center';
                                    el.style.transition = 'all 0.3s ease';
                                    el.setAttribute('data-hover-highlight', 'true');
                                }}
                            }}
                        }});
                    }});
                    
                    item.addEventListener('mouseleave', function() {{
                        // Reset all highlighted elements
                        const highlighted = document.querySelectorAll('[data-hover-highlight="true"]');
                        highlighted.forEach(function(el) {{
                            el.style.color = '';
                            el.style.fontWeight = '';
                            el.removeAttribute('data-hover-highlight');
                        }});
                    }});
                }});
            }}
            
            // Function to center all caption text
            function centerCaptions() {{
                const selectors = [
                    '[data-testid*="image-select"]',
                    '[class*="image-select"]',
                    '[class*="imageSelect"]'
                ];
                
                selectors.forEach(selector => {{
                    const items = document.querySelectorAll(selector);
                    items.forEach(item => {{
                        // Find caption text elements
                        const textElements = item.querySelectorAll('p, div:not(:has(img)), span, label');
                        textElements.forEach(el => {{
                            const text = el.textContent ? el.textContent.trim() : '';
                            if (text && text.length < 50 && !el.querySelector('img')) {{
                                el.style.textAlign = 'center';
                            }}
                        }});
                    }});
                }});
            }}
            
            // Run immediately and also after a delay to catch dynamically loaded content
            setupHoverHighlight();
            centerCaptions();
            setTimeout(function() {{
                setupHoverHighlight();
                centerCaptions();
            }}, 500);
            setTimeout(function() {{
                setupHoverHighlight();
                centerCaptions();
            }}, 1000);
            
            // Also run when new content is added
            const observer = new MutationObserver(function(mutations) {{
                setupHoverHighlight();
                centerCaptions();
            }});
            observer.observe(document.body, {{ childList: true, subtree: true }});
        }})();
        </script>
        '''
        st.markdown(hover_script, unsafe_allow_html=True)
        
        # Update session state with the selected machine
        selected_machine = machines[selected_index]
        st.session_state[state_key] = selected_machine
        
        return selected_machine
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
    
    # Load the machine icon image and convert to base64
    image_base64 = None
    try:
        import os
        import base64
        image_path = "frame0/chiller_grey_big.png"
        if os.path.exists(image_path):
            with open(image_path, "rb") as image_file:
                image_bytes = image_file.read()
                image_base64 = base64.b64encode(image_bytes).decode()
    except:
        pass
    
    # Display machines in a grid (4 columns)
    num_cols = 4
    num_rows = (len(machines) + num_cols - 1) // num_cols
    
    # Use query parameters for state updates - no buttons needed
    if image_base64:
        # Check for machine selection in query parameters FIRST (before creating buttons)
        query_params = st.query_params
        selected_machine_param = query_params.get(f'select_machine_{key_prefix}', None)
        if selected_machine_param and selected_machine_param in machines:
            # Update session state with the selected machine
            st.session_state[state_key] = selected_machine_param
            # Remove the parameter to avoid re-triggering on next rerun
            new_params = dict(query_params)
            new_params.pop(f'select_machine_{key_prefix}', None)
            st.query_params = new_params
        
        # Create global JavaScript function to update state via query parameters
        js_function = f'''
        <script>
        if (typeof window.triggerMachineSelection_{key_prefix} === 'undefined') {{
            window.triggerMachineSelection_{key_prefix} = function(buttonKey, machineName) {{
                // Update URL with query parameter to trigger Streamlit rerun
                const currentUrl = new URL(window.location);
                currentUrl.searchParams.set('select_machine_{key_prefix}', encodeURIComponent(machineName));
                // Use replace to avoid adding to history
                window.location.replace(currentUrl.toString());
            }};
        }}
        </script>
        '''
        st.markdown(js_function, unsafe_allow_html=True)
    
    # Display machines using columns with proper HTML rendering
    for row in range(num_rows):
        cols = st.columns(num_cols)
        for col_idx in range(num_cols):
            machine_idx = row * num_cols + col_idx
            if machine_idx < len(machines):
                machine = machines[machine_idx]
                is_selected = st.session_state[state_key] == machine
                
                with cols[col_idx]:
                    button_key = f"{key_prefix}_machine_{machine_idx}"
                    border_color = "orange" if is_selected else "#555"
                    border_width = "3px" if is_selected else "2px"
                    bg_color = "#333" if is_selected else "#2a2a2a"
                    shadow = "0 4px 8px rgba(255, 165, 0, 0.3)" if is_selected else "0 2px 4px rgba(0, 0, 0, 0.3)"
                    font_weight = "bold" if is_selected else "normal"
                    
                    if image_base64:
                        # Create clickable image button - the image itself is the button
                        button_html = f'''
<div style="position: relative; width: 100%; text-align: center;">
<button id="machine-img-btn-{button_key}" 
        onclick="
           window.triggerMachineSelection_{key_prefix}('{button_key}', '{machine}');
        "
        style="
           background: transparent;
           border: none;
           padding: 0;
           margin: 0;
           cursor: pointer;
           display: inline-block;
        ">
<img src="data:image/png;base64,{image_base64}" 
     style="
        width: 100px;
        height: 100px;
        object-fit: contain;
        cursor: pointer;
        border: {border_width} solid {border_color};
        border-radius: 10px;
        padding: 10px;
        background: {bg_color};
        box-shadow: {shadow};
        transition: all 0.3s ease;
        display: block;
        margin: 0 auto 8px auto;
        pointer-events: none;
     "
/>
</button>
<div style="color: white; font-size: 12px; font-weight: {font_weight}; text-align: center; margin-top: 5px;">{machine}</div>
</div>
<script>
(function() {{
    const imgBtn = document.getElementById('machine-img-btn-{button_key}');
    if (imgBtn) {{
        imgBtn.addEventListener('mouseenter', function() {{
            const img = this.querySelector('img');
            if (img) {{
                img.style.transform = 'translateY(-3px)';
                img.style.boxShadow = '0 6px 12px rgba(255, 165, 0, 0.4)';
                img.style.borderColor = 'orange';
            }}
        }});
        imgBtn.addEventListener('mouseleave', function() {{
            const img = this.querySelector('img');
            if (img) {{
                img.style.transform = 'translateY(0)';
                img.style.boxShadow = '{shadow}';
                img.style.borderColor = '{border_color}';
            }}
        }});
    }}
}})();
</script>
'''
                        st.markdown(button_html, unsafe_allow_html=True)
                    # else:
                    #     # Just show button with text
                    #     button_type = "primary" if is_selected else "secondary"
                    #     if st.button(machine, key=button_key, width='stretch', type=button_type):
                    #         st.session_state[state_key] = machine
                    #         st.rerun()
    
    return st.session_state[state_key]

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
                    selected_machine = display_machine_icons(machinery[part][category], f"machine_{i}_{j}")
                    
                    # Load data for the selected machine
                    machine_data = load_machine_data(selected_machine)
                    if machine_data:
                        results_df = machine_data['df']
                        start_date = machine_data['start_date']
                        predicted_end_date = machine_data['predicted_end_date']
                        current_date = machine_data['current_date']
                        current_date_running_hours = machine_data['current_running_hour']
                    else:
                        # Fallback to default data if machine data not found
                        results_df = plots.results_df
                        start_date = plots.start_date
                        predicted_end_date = plots.predicted_end_date
                        current_date = plots.current_date
                        current_date_running_hours = plots.current_date_running_hours
                    
                    dates = pd.date_range(end=pd.Timestamp.today(), periods=12)
                    st.markdown("<div class='multi-row-tabs'>", unsafe_allow_html=True)
                    st.markdown(
                        f"""
                                       <div style='font-size:22px; line-height:1.4;'>
                                       <b>Machine:</b> <span style='color:orange'>{selected_machine}</span><br>
                                       <b>Next Maintenance:</b> <span style='color:orange'>{predicted_end_date.date() if predicted_end_date else "N/A"}</span><br>
                                       <b>Last Maintenance:</b> {start_date.date() if start_date else "N/A"}<br>
                                       </div>
                                       """,
                        unsafe_allow_html=True
                    )
                    target_cost = 300000
                    plots.plot_wcc_charts(st, results_df, start_date, predicted_end_date, current_date,
                                          target_cost, current_date_running_hours, key_prefix=f"chart_{i}_{j}")
                if i == 1:
                    selected_machine = display_machine_icons(machinery[part][category], f"heat_exchanger_{i}_{j}")
                    
                    # Load data for the selected substation
                    substation_data = load_substation_data(selected_machine)
                    if substation_data:
                        results_ss_df = substation_data['df']
                        ss_start_date = substation_data['start_date']
                        ss_current_date = substation_data['current_date']
                        # Extract HX number from selected_machine to get correct column names
                        hx_match = re.search(r'HX(\d+)', selected_machine)
                        hx_num = hx_match.group(1) if hx_match else "1"
                    else:
                        # Fallback to default data if substation data not found
                        results_ss_df = plots.results_ss_df
                        ss_start_date = plots.ss_start_date
                        ss_current_date = plots.ss_current_date
                        hx_num = "1"
                    
                    st.markdown("<div class='multi-row-tabs'>", unsafe_allow_html=True)
                    st.markdown(
                        f"""
                                       <div style='font-size:22px; line-height:1.4;'>
                                       <b>Heat Exchangers:</b> <span style='color:orange'>{selected_machine}</span><br>
                                       <b>Last Maintenance:</b> {ss_start_date.date() if ss_start_date else "N/A"}<br>
                                       </div>
                                       """,
                        unsafe_allow_html=True
                    )
                    # Pass the loaded data to plot function - need to update plot_ss_charts to use results_ss_df parameter
                    plots.plot_ss_charts(st, results_ss_df, ss_start_date, None, ss_current_date,
                                          plots.target_cost, None, key_prefix=f"chart_{i}_{j}", hx_num=hx_num)
                if i == 2:
                    selected_machine = display_machine_icons(machinery[part][category], f"chiller_{i}_{j}")
                    
                    # Load data for the selected machine
                    machine_data = load_machine_data(selected_machine)
                    if machine_data:
                        results_df = machine_data['df']
                        start_date = machine_data['start_date']
                        predicted_end_date = machine_data['predicted_end_date']
                        current_date = machine_data['current_date']
                        current_date_running_hours = machine_data['current_running_hour']
                    else:
                        # Fallback to default data if machine data not found
                        results_df = plots.results_df
                        start_date = plots.start_date
                        predicted_end_date = plots.predicted_end_date
                        current_date = plots.current_date
                        current_date_running_hours = plots.current_date_running_hours
                    
                    dates = pd.date_range(end=pd.Timestamp.today(), periods=12)
                    st.markdown("<div class='multi-row-tabs'>", unsafe_allow_html=True)
                    st.markdown(
                        f"""
                                                         <div style='font-size:22px; line-height:1.4;'>
                                                         <b>Chiller:</b> <span style='color:orange'>{selected_machine}</span><br>
                                                         <b>Next Maintenance:</b> <span style='color:orange'>{predicted_end_date.date() if predicted_end_date else "N/A"}</span><br>
                                                         <b>Last Maintenance:</b> {start_date.date() if start_date else "N/A"}<br>
                                                         </div>
                                                         """,
                        unsafe_allow_html=True
                    )
                    target_cost = 300000
                    plots.plot_vib_charts(st, results_df, start_date, predicted_end_date,
                                         current_date,
                                         target_cost, current_date_running_hours,
                                         key_prefix=f"chart_{i}_{j}")

st.markdown("""
    <style>
    #MainMenu, footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)