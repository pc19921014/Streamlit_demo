import os

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import streamlit as st

TARGET_COST = 300_000
MAX_WCC_POINTS = 2_500
MAX_SS_POINTS = 3_000
MAX_CURRENT_RUNNING_HOUR = 20_000

# Plot text sizing (adjust these in one place)
PLOT_TITLE_FONT_SIZE = 24
PLOT_AXIS_TITLE_FONT_SIZE = 20
PLOT_AXIS_TICK_FONT_SIZE = 16
PLOT_LEGEND_FONT_SIZE = 16

# Shared X/Y/Z colours for vibration reference image and charts.
MOVEMENT_AXIS_COLORS = {
    "X": "#ff6b6b",
    "Y": "#51cf66",
    "Z": "#4da6ff",
}

# Shipped defaults (lazy-loaded via @st.cache_data — not read at import time)
DEFAULT_WCC_CSV = os.path.join(
    "plot", "input", "chiller result", "NP_2_1", "prediction_results_NP_2_1.csv"
)
DEFAULT_SS_CSV = os.path.join(
    "plot",
    "input",
    "valve_analysis_plots",
    "1A1",
    "V-01_HX1",
    "cumulative_trends",
    "V-01_HX1_all_data.csv",
)

_WCC_COLUMNS = (
    "cumulative_running_hours",
    "cumulative_cost",
    "cumulative_power_increase",
    "cumulative_small_delta_t_increase",
    "start_date",
    "current_date",
    "predicted_end_date",
    "current_running_hour",
)


def _substation_columns_for_hx(hx_num: str) -> list[str]:
    n = str(hx_num)
    return [
        "start_date",
        "current_date",
        "running_hour",
        f"HX{n}_lmtd_cumulative_change",
        f"HX{n}_supply_dt_cumulative_change",
        f"HX{n}_primary_dp_cumulative_change",
        f"HX{n}_secondary_dp_cumulative_change",
    ]


def _downsample_for_plot(df: pd.DataFrame, x_col: str, max_points: int) -> pd.DataFrame:
    """Return a lightweight frame for chart rendering."""
    if df is None or df.empty or x_col not in df.columns:
        return df
    n = len(df)
    if n <= max_points:
        return df
    step = max(1, n // max_points)
    sampled = df.iloc[::step].copy()
    # Always keep the latest point for end-date / current-date markers.
    if sampled.index[-1] != df.index[-1]:
        sampled = pd.concat([sampled, df.tail(1)], axis=0)
    return sampled


def _axis_with_fonts(title: str | None = None, **kwargs):
    axis = dict(kwargs)
    axis["color"] = "white"
    axis["tickfont"] = dict(size=PLOT_AXIS_TICK_FONT_SIZE, color="white")
    if title is not None:
        axis["title"] = dict(
            text=title,
            font=dict(size=PLOT_AXIS_TITLE_FONT_SIZE, color="white"),
        )
    return axis


@st.cache_data(show_spinner=False)
def _build_xyz_reference_image():
    """Static XYZ axis diagram for vibration movement reference."""
    from PIL import Image, ImageDraw

    width, height = 480, 360
    img = Image.new("RGB", (width, height), "#222222")
    draw = ImageDraw.Draw(img)

    origin = (210, 250)
    axis_length = 95

    def _draw_axis(end, color: str, label: str, title: str) -> None:
        draw.line([origin, end], fill=color, width=4)
        draw.ellipse([end[0] - 4, end[1] - 4, end[0] + 4, end[1] + 4], fill=color)
        draw.text((end[0] + 8, end[1] - 8), label, fill=color)
        draw.text((end[0] + 8, end[1] + 10), title, fill="white")

    z_end = (origin[0], origin[1] - axis_length)
    x_end = (origin[0] + int(axis_length * 0.95), origin[1] + int(axis_length * 0.35))
    y_end = (origin[0] - int(axis_length * 0.95), origin[1] + int(axis_length * 0.35))

    _draw_axis(z_end, MOVEMENT_AXIS_COLORS["Z"], "Z", "Global Z Movement")
    _draw_axis(x_end, MOVEMENT_AXIS_COLORS["X"], "X", "Global X Movement")
    _draw_axis(y_end, MOVEMENT_AXIS_COLORS["Y"], "Y", "Global Y Movement")

    draw.ellipse(
        [origin[0] - 5, origin[1] - 5, origin[0] + 5, origin[1] + 5],
        fill="white",
    )
    draw.text((origin[0] + 10, origin[1] + 8), "Origin (0, 0, 0)", fill="white")
    draw.text((24, 24), "Global XYZ Movement Reference", fill="white")

    return img


@st.cache_data(show_spinner=False)
def load_prediction_bundle(path: str, _mtime: float) -> dict | None:
    """Load WCC / chiller prediction CSV (metadata row 0, series from row 1)."""
    if not path or not os.path.isfile(path):
        return None
    try:
        try:
            df = pd.read_csv(path, sep=",", usecols=list(_WCC_COLUMNS))
        except ValueError:
            df = pd.read_csv(path, sep=",")
    except Exception:
        return None
    if len(df) == 0:
        return None
    start_date = predicted_end_date = current_date = current_running_hour = None
    if "start_date" in df.columns:
        df["start_date"] = pd.to_datetime(df["start_date"], errors="coerce")
        start_date = (
            df["start_date"].iloc[0]
            if not pd.isna(df["start_date"].iloc[0])
            else None
        )
    if "predicted_end_date" in df.columns:
        df["predicted_end_date"] = pd.to_datetime(
            df["predicted_end_date"], errors="coerce"
        )
        predicted_end_date = (
            df["predicted_end_date"].iloc[0]
            if not pd.isna(df["predicted_end_date"].iloc[0])
            else None
        )
    if "current_date" in df.columns:
        df["current_date"] = pd.to_datetime(df["current_date"], errors="coerce")
        current_date = (
            df["current_date"].iloc[0]
            if not pd.isna(df["current_date"].iloc[0])
            else None
        )
    if "current_running_hour" in df.columns:
        v = df["current_running_hour"].iloc[0]
        current_running_hour = v if pd.notna(v) else None
        if current_running_hour is not None and current_running_hour > MAX_CURRENT_RUNNING_HOUR:
            return {
                "overflow": True,
                "current_running_hour": current_running_hour,
            }
    data_df = df[1:].copy() if len(df) > 1 else df.copy()
    return {
        "df": data_df,
        "start_date": start_date,
        "predicted_end_date": predicted_end_date,
        "current_date": current_date,
        "current_running_hour": current_running_hour,
    }


@st.cache_data(show_spinner=False)
def load_substation_bundle(
    prediction_path: str,
    valve_path: str,
    hx_num: str,
    _prediction_mtime: float,
    _valve_mtime: float,
) -> dict | None:
    """Load substation prediction bundle + valve metrics bundle."""
    if (
        not prediction_path
        or not valve_path
        or not os.path.isfile(prediction_path)
        or not os.path.isfile(valve_path)
    ):
        return None
    try:
        prediction_df = pd.read_csv(prediction_path, sep=",")
        valve_df = pd.read_csv(valve_path, sep=",")
    except Exception:
        return None
    if prediction_df is None or prediction_df.empty or valve_df is None or valve_df.empty:
        return None

    start_date = current_date = predicted_end_date = None
    if "start_date" in prediction_df.columns:
        start_date = pd.to_datetime(prediction_df["start_date"].iloc[0], errors="coerce")
    if "current_date" in prediction_df.columns:
        current_date = pd.to_datetime(
            prediction_df["current_date"].iloc[0], errors="coerce"
        )
    if "predicted_end_date" in prediction_df.columns:
        predicted_end_date = pd.to_datetime(
            prediction_df["predicted_end_date"].iloc[0], errors="coerce"
        )

    # First row carries bundle metadata; trend rows start from row 1.
    prediction_data_df = prediction_df.iloc[1:].copy() if len(prediction_df) > 1 else prediction_df.copy()

    return {
        "df": prediction_data_df,
        "valve_df": valve_df,
        "start_date": start_date if pd.notna(start_date) else None,
        "predicted_end_date": predicted_end_date if pd.notna(predicted_end_date) else None,
        "current_date": current_date if pd.notna(current_date) else None,
        "current_running_hour": None,
        "hx_num": str(hx_num),
    }


def get_default_wcc_bundle() -> dict | None:
    """Fallback demo data for WCC charts; loads once then cached."""
    if not os.path.isfile(DEFAULT_WCC_CSV):
        return None
    return load_prediction_bundle(DEFAULT_WCC_CSV, os.path.getmtime(DEFAULT_WCC_CSV))


def get_default_substation_bundle() -> dict | None:
    """Fallback demo data for substation charts (HX1 columns)."""
    if not os.path.isfile(DEFAULT_SS_CSV):
        return None
    return None


def plot_wcc_charts(
    st,
    results_df,
    start_date,
    predicted_end_date,
    current_date,
    target_cost,
    current_date_running_hours,
    key_prefix,
):
    plot_df = _downsample_for_plot(
        results_df, "cumulative_running_hours", MAX_WCC_POINTS
    )
    if plot_df is None or plot_df.empty:
        st.warning("No data available for chart rendering.")
        return

    # Plot 1: Total Cost Over Time
    fig1 = px.line(
        plot_df,
        x="cumulative_running_hours",
        y="cumulative_cost",
        title="Total Cost Increase Over Running Hours",
        render_mode="webgl",
    )
    fig1.add_hline(
        y=target_cost,
        line_dash="dash",
        line_color="red",
        annotation_text=f"Target Cost (${target_cost:,.0f})",
        annotation_font=dict(color="red"),
        annotation_position="bottom right",
    )
    if current_date_running_hours is not None and current_date is not None:
        fig1.add_vline(
            x=current_date_running_hours,
            line_dash="dot",
            line_color="grey",
            annotation_font=dict(color="grey"),
            annotation_text=f'Current Date ({current_date.strftime("%Y-%m")})',
            annotation_position="bottom right",
        )
    if start_date is not None:
        fig1.add_vline(
            x=min(plot_df["cumulative_running_hours"]),
            line_dash="dot",
            line_color="grey",
            annotation_font=dict(color="grey"),
            annotation_text=f'Start Date ({start_date.strftime("%Y-%m-%d")})',
            annotation_position="bottom right",
        )

    if predicted_end_date is not None:
        fig1.add_vline(
            x=max(plot_df["cumulative_running_hours"]),
            line_dash="dot",
            line_color="grey",
            annotation_font=dict(color="grey"),
            annotation_text=f'End Date ({predicted_end_date.strftime("%Y-%m-%d")})',
            annotation_position="bottom right",
        )

    fig1.update_layout(
        plot_bgcolor="#222",
        paper_bgcolor="#222",
        font_color="white",
        title_font_color="white",
        title_font=dict(size=PLOT_TITLE_FONT_SIZE),
        xaxis=_axis_with_fonts("Cumulative Running Hours", dtick=200),
        yaxis=_axis_with_fonts("Total Cost ($)"),
        height=400,
        margin=dict(l=40, r=30, t=60, b=40),
    )
    fig1.update_traces(line_color="orange")

    # Plot 2: Power Difference Over Time
    fig2 = px.line(
        plot_df,
        x="cumulative_running_hours",
        y="cumulative_power_increase",
        title="Power Difference Over Running Hours",
        render_mode="webgl",
    )
    if current_date_running_hours is not None and current_date is not None:
        fig2.add_vline(
            x=current_date_running_hours,
            line_dash="dot",
            line_color="grey",
            annotation_font=dict(color="grey"),
            annotation_text=f'Current Date ({current_date.strftime("%Y-%m")})',
            annotation_position="bottom right",
        )
    if start_date is not None:
        fig2.add_vline(
            x=min(plot_df["cumulative_running_hours"]),
            line_dash="dot",
            line_color="grey",
            annotation_font=dict(color="grey"),
            annotation_text=f'Start Date ({start_date.strftime("%Y-%m-%d")})',
            annotation_position="bottom right",
        )

    if predicted_end_date is not None:
        fig2.add_vline(
            x=max(plot_df["cumulative_running_hours"]),
            line_dash="dot",
            line_color="grey",
            annotation_font=dict(color="grey"),
            annotation_text=f'End Date ({predicted_end_date.strftime("%Y-%m-%d")})',
            annotation_position="bottom right",
        )

    fig2.update_layout(
        plot_bgcolor="#222",
        paper_bgcolor="#222",
        font_color="white",
        title_font_color="white",
        title_font=dict(size=PLOT_TITLE_FONT_SIZE),
        xaxis=_axis_with_fonts("Cumulative Running Hours", dtick=200),
        yaxis=_axis_with_fonts("Power (kW)"),
        height=400,
        margin=dict(l=40, r=30, t=60, b=40),
    )
    fig2.update_traces(line_color="orange")

    # Plot 3: Cumulative Small Delta T Over Time
    fig3 = px.line(
        plot_df,
        x="cumulative_running_hours",
        y="cumulative_small_delta_t_increase",
        title="Cumulative Small DeltaT Over Running Hours",
        render_mode="webgl",
    )
    if current_date_running_hours is not None and current_date is not None:
        fig3.add_vline(
            x=current_date_running_hours,
            line_dash="dot",
            line_color="grey",
            annotation_font=dict(color="grey"),
            annotation_text=f'Current Date ({current_date.strftime("%Y-%m")})',
            annotation_position="bottom right",
        )
    if start_date is not None:
        fig3.add_vline(
            x=min(plot_df["cumulative_running_hours"]),
            line_dash="dot",
            line_color="grey",
            annotation_font=dict(color="grey"),
            annotation_text=f'Start Date ({start_date.strftime("%Y-%m-%d")})',
            annotation_position="bottom right",
        )

    if predicted_end_date is not None:
        fig3.add_vline(
            x=max(plot_df["cumulative_running_hours"]),
            line_dash="dot",
            line_color="grey",
            annotation_font=dict(color="grey"),
            annotation_text=f'End Date ({predicted_end_date.strftime("%Y-%m-%d")})',
            annotation_position="bottom right",
        )
    fig3.update_layout(
        plot_bgcolor="#222",
        paper_bgcolor="#222",
        font_color="white",
        title_font_color="white",
        title_font=dict(size=PLOT_TITLE_FONT_SIZE),
        xaxis=_axis_with_fonts("Cumulative Running Hours", dtick=200),
        yaxis=_axis_with_fonts("Cumulative Small DeltaT (°C)"),
        height=400,
        margin=dict(l=40, r=30, t=60, b=40),
    )
    fig3.update_traces(line_color="orange")

    # Display plots in Streamlit
    st.plotly_chart(fig1, width="stretch", key=f"{key_prefix}_fig1")
    st.plotly_chart(fig2, width="stretch", key=f"{key_prefix}_fig2")
    st.plotly_chart(fig3, width="stretch", key=f"{key_prefix}_fig3")


def plot_ss_charts(
    st,
    results_ss_df,
    valve_ss_df,
    ss_start_date,
    predicted_end_date,
    ss_current_date,
    target_cost,
    current_date_running_hours,
    key_prefix,
    hx_num="1",
):
    if results_ss_df is None or results_ss_df.empty:
        st.warning("No substation data available for chart rendering.")
        return

    prediction_df = results_ss_df.copy()
    valve_df = valve_ss_df
    if valve_df is None or not isinstance(valve_df, pd.DataFrame) or valve_df.empty:
        st.warning("No substation valve data available for chart rendering.")
        return

    def _find_col(df: pd.DataFrame, candidates: list[str]) -> str | None:
        lowered = {c.lower(): c for c in df.columns}
        for token in candidates:
            for col_lower, original in lowered.items():
                if token in col_lower:
                    return original
        return None

    def _line_chart(df: pd.DataFrame, x_col: str, y_col: str, title: str, y_title: str, key: str):
        chart_df = df[[x_col, y_col]].copy()
        chart_df[x_col] = pd.to_numeric(chart_df[x_col], errors="coerce")
        chart_df[y_col] = pd.to_numeric(chart_df[y_col], errors="coerce")
        chart_df = chart_df.dropna(subset=[x_col, y_col])
        if chart_df.empty:
            st.info(f"{title}: no data")
            return
        fig = px.line(chart_df, x=x_col, y=y_col, title=title, render_mode="webgl")
        fig.update_layout(
            plot_bgcolor="#222",
            paper_bgcolor="#222",
            font_color="white",
            title_font_color="white",
            title_font=dict(size=PLOT_TITLE_FONT_SIZE),
            xaxis=_axis_with_fonts("Running Hour"),
            yaxis=_axis_with_fonts(y_title),
            height=400,
            margin=dict(l=40, r=30, t=60, b=40),
        )
        fig.update_traces(line_color="orange")
        st.plotly_chart(fig, width="stretch", key=key)

    def _valve_box_with_median(df: pd.DataFrame, valve_col: str, y_col: str, title: str, y_title: str, key: str):
        chart_df = df[[valve_col, y_col]].copy()
        chart_df[valve_col] = pd.to_numeric(chart_df[valve_col], errors="coerce")
        chart_df[y_col] = pd.to_numeric(chart_df[y_col], errors="coerce")
        chart_df = chart_df.dropna(subset=[valve_col, y_col])
        if chart_df.empty:
            st.info(f"{title}: no data")
            return
        chart_df["valve_bin"] = (np.floor(chart_df[valve_col] / 10) * 10).clip(0, 90)
        chart_df["valve_bin_label"] = chart_df["valve_bin"].apply(
            lambda v: f"{int(v)}-{int(min(v + 10, 100))}%"
        )
        bin_order = [f"{i}-{min(i + 10, 100)}%" for i in range(0, 100, 10)]
        grouped = (
            chart_df.groupby("valve_bin_label", observed=True)[y_col]
            .median()
            .reset_index(name="median_y")
        )
        grouped["sort_key"] = grouped["valve_bin_label"].str.extract(r"^(\d+)").astype(float)
        grouped = grouped.sort_values("sort_key")
        fig = px.box(
            chart_df,
            x="valve_bin_label",
            y=y_col,
            category_orders={"valve_bin_label": bin_order},
            title=title,
            points=False,
            labels={"valve_bin_label": "Valve Percentage", y_col: y_title},
        )
        fig.add_trace(
            go.Scatter(
                x=grouped["valve_bin_label"],
                y=grouped["median_y"],
                mode="lines+markers",
                name="Median",
                line=dict(color="orange", width=2),
                marker=dict(color="orange", size=7),
            )
        )
        fig.update_layout(
            plot_bgcolor="#222",
            paper_bgcolor="#222",
            font_color="white",
            title_font_color="white",
            title_font=dict(size=PLOT_TITLE_FONT_SIZE),
            xaxis=_axis_with_fonts("Valve Percentage (10% Interval)"),
            yaxis=_axis_with_fonts(y_title),
            legend=dict(font=dict(color="white", size=PLOT_LEGEND_FONT_SIZE)),
            height=420,
            margin=dict(l=40, r=30, t=60, b=40),
        )
        st.plotly_chart(fig, width="stretch", key=key)

    prediction_running_col = _find_col(prediction_df, ["cumulative_running_hours", "running_hour"])
    supply_dt_pred_col = _find_col(prediction_df, ["supply_dt_increase", "supply dt increase"])
    power_kwh_col = _find_col(prediction_df, ["cumulative_ea_increase", "ea_increase"])
    extra_cost_col = _find_col(prediction_df, ["cumulative_cost", "cost"])

    valve_pct_col = _find_col(valve_df, ["averaged", "valve"])
    valve_supply_dt_col = _find_col(valve_df, [f"hx{hx_num} supply_dt", "supply_dt"])
    valve_lmtd_col = _find_col(valve_df, [f"hx{hx_num} lmtd", "lmtd"])
    valve_primary_chw_dt_col = _find_col(valve_df, [f"hx{hx_num} primary chw dt", "primary chw dt"])
    valve_secondary_chw_dt_col = _find_col(valve_df, [f"hx{hx_num} secondary chw dt", "secondary chw dt"])

    if prediction_running_col and supply_dt_pred_col:
        _line_chart(
            prediction_df,
            prediction_running_col,
            supply_dt_pred_col,
            "Supply Delta T vs Running Hour",
            "Supply Delta T",
            f"{key_prefix}_fig1",
        )
    else:
        st.info("Supply Delta T vs Running Hour: no data")

    if prediction_running_col and power_kwh_col:
        _line_chart(
            prediction_df,
            prediction_running_col,
            power_kwh_col,
            "Power kWh vs Running Hour",
            "Power kWh",
            f"{key_prefix}_fig2",
        )
    else:
        st.info("Power kWh vs Running Hour: no data")

    if prediction_running_col and extra_cost_col:
        _line_chart(
            prediction_df,
            prediction_running_col,
            extra_cost_col,
            "Extra Cost vs Running Hour",
            "Extra Cost",
            f"{key_prefix}_fig3",
        )
    else:
        st.info("Extra Cost vs Running Hour: no data")

    if valve_pct_col and valve_supply_dt_col:
        _valve_box_with_median(
            valve_df,
            valve_pct_col,
            valve_supply_dt_col,
            "Supply Delta T vs Valve Percentage",
            "Supply Delta T",
            f"{key_prefix}_fig4",
        )
    else:
        st.info("Supply Delta T vs Valve Percentage: no data")

    if valve_pct_col and valve_lmtd_col:
        _valve_box_with_median(
            valve_df,
            valve_pct_col,
            valve_lmtd_col,
            "Log Mean Temperature Difference vs Valve Percentage",
            "Log Mean Temperature Difference",
            f"{key_prefix}_fig5",
        )
    else:
        st.info("Log Mean Temperature Difference vs Valve Percentage: no data")

    if valve_pct_col and valve_primary_chw_dt_col:
        _valve_box_with_median(
            valve_df,
            valve_pct_col,
            valve_primary_chw_dt_col,
            "Primary Chilled Water Delta T vs Valve Percentage",
            "Primary Chilled Water Delta T",
            f"{key_prefix}_fig6",
        )
    else:
        st.info("Primary Chilled Water Delta T vs Valve Percentage: no data")

    if valve_pct_col and valve_secondary_chw_dt_col:
        _valve_box_with_median(
            valve_df,
            valve_pct_col,
            valve_secondary_chw_dt_col,
            "Secondary Chilled Water Delta T vs Valve Percentage",
            "Secondary Chilled Water Delta T",
            f"{key_prefix}_fig7",
        )
    else:
        st.info("Secondary Chilled Water Delta T vs Valve Percentage: no data")


def plot_vib_charts(
    st,
    results_df,
    ss_start_date,
    predicted_end_date,
    ss_current_date,
    target_cost,
    current_date_running_hours,
    key_prefix,
):
    if results_df is None or results_df.empty:
        st.info("No vibration data")
        return

    vib_df = results_df.copy()

    required_axes = ["Global_X_Movement", "Global_Y_Movement", "Global_Z_Movement"]
    if not all(col in vib_df.columns for col in required_axes):
        st.info("No vibration data")
        return

    for col in required_axes:
        vib_df[col] = pd.to_numeric(vib_df[col], errors="coerce")

    movement_axis_labels = {
        "Global_X_Movement": "X",
        "Global_Y_Movement": "Y",
        "Global_Z_Movement": "Z",
    }

    def _first_matching_column(candidates: list[str]) -> str | None:
        lowered = {c.lower(): c for c in vib_df.columns}
        for key in candidates:
            for col_lower, original in lowered.items():
                if key in col_lower:
                    return original
        return None

    delta_pressure_col = _first_matching_column(["delta_pressure", "delta pressure"])
    running_hour_col = _first_matching_column(["running hours", "running_hour"])
    motor_fla_col = _first_matching_column(["motor fla loading", "fla loading"])

    st.image(
        _build_xyz_reference_image(),
        caption="Global XYZ Movement Reference",
        width=420,
    )

    def _make_binned_box_plot(
        source_df: pd.DataFrame, x_col: str, title: str, x_title: str, chart_key: str
    ) -> None:
        if not x_col or x_col not in source_df.columns:
            st.info(f"{title}: no data")
            return

        chart_df = source_df[[x_col] + required_axes].copy()
        chart_df[x_col] = pd.to_numeric(chart_df[x_col], errors="coerce")
        chart_df = chart_df.dropna(subset=[x_col])
        if chart_df.empty:
            st.info(f"{title}: no data")
            return

        bins = min(12, max(4, chart_df[x_col].nunique()))
        try:
            chart_df["bin"] = pd.qcut(chart_df[x_col], q=bins, duplicates="drop")
        except ValueError:
            chart_df["bin"] = pd.cut(chart_df[x_col], bins=min(8, bins))

        chart_df = chart_df.dropna(subset=["bin"])
        if chart_df.empty:
            st.info(f"{title}: no data")
            return

        def _bin_mid(interval_value) -> float | None:
            if pd.isna(interval_value):
                return None
            return round((float(interval_value.left) + float(interval_value.right)) / 2.0, 1)

        chart_df["bin_mid"] = chart_df["bin"].apply(_bin_mid)
        chart_df = chart_df.dropna(subset=["bin_mid"])
        if chart_df.empty:
            st.info(f"{title}: no data")
            return

        melted = chart_df.melt(
            id_vars=["bin_mid"],
            value_vars=required_axes,
            var_name="movement_axis",
            value_name="movement",
        )
        melted["movement_axis"] = melted["movement_axis"].map(movement_axis_labels)
        melted = melted.dropna(subset=["movement"])
        if melted.empty:
            st.info(f"{title}: no data")
            return

        fig = px.box(
            melted,
            x="bin_mid",
            y="movement",
            color="movement_axis",
            labels={
                "bin_mid": x_title,
                "movement": "Global Movement",
                "movement_axis": "Axis",
            },
            points=False,
            category_orders={"movement_axis": ["X", "Y", "Z"]},
            color_discrete_map=MOVEMENT_AXIS_COLORS,
        )
        fig.update_traces(
            line=dict(width=2),
            marker_line=dict(width=1, color="white"),
        )
        for axis_name in ["X", "Y", "Z"]:
            axis_df = melted[melted["movement_axis"] == axis_name]
            if axis_df.empty:
                continue
            grouped = (
                axis_df.groupby("bin_mid", observed=True)["movement"]
                .median()
                .reset_index(name="median_movement")
                .sort_values("bin_mid")
            )
            fig.add_trace(
                go.Scatter(
                    x=grouped["bin_mid"],
                    y=grouped["median_movement"],
                    mode="lines+markers",
                    name=f"{axis_name} Median",
                    alignmentgroup=True,
                    offsetgroup=axis_name,
                    marker=dict(
                        color=MOVEMENT_AXIS_COLORS[axis_name],
                        size=8,
                        symbol="diamond",
                    ),
                    line=dict(color=MOVEMENT_AXIS_COLORS[axis_name], width=2),
                    legendgroup=axis_name,
                )
            )
        fig.update_layout(
            title=title,
            plot_bgcolor="#222",
            paper_bgcolor="#222",
            font_color="white",
            title_font_color="white",
            title_font=dict(size=PLOT_TITLE_FONT_SIZE),
            height=420,
            margin=dict(l=40, r=20, t=60, b=40),
            xaxis=_axis_with_fonts(x_title, tickangle=-20, tickformat=".1f"),
            yaxis=_axis_with_fonts("Global Movement", tickformat=".1f"),
            legend=dict(font=dict(color="white", size=PLOT_LEGEND_FONT_SIZE)),
        )
        st.plotly_chart(fig, width="stretch", key=chart_key)

    _make_binned_box_plot(
        vib_df,
        delta_pressure_col,
        "Global X/Y/Z Movement vs Chiller Delta Pressure",
        "Chiller Delta Pressure",
        f"{key_prefix}_vib_delta_pressure",
    )
    _make_binned_box_plot(
        vib_df,
        running_hour_col,
        "Global X/Y/Z Movement vs Running Hour",
        "Running Hour",
        f"{key_prefix}_vib_running_hour",
    )
    _make_binned_box_plot(
        vib_df,
        motor_fla_col,
        "Global X/Y/Z Movement vs Motor FLA Loading",
        "Motor FLA Loading",
        f"{key_prefix}_vib_motor_fla",
    )
