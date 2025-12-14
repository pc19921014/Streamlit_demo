import pandas as pd
import plotly.express as px
import numpy as np
import plotly.graph_objs as go


results_df = pd.read_csv('plot/input/prediction_results_SP_2_2.csv', sep = ',')
results_df['start_date'] = pd.to_datetime(results_df['start_date'])
start_date = results_df['start_date'][0]
results_df['predicted_end_date'] = pd.to_datetime(results_df['predicted_end_date'])
predicted_end_date = results_df['predicted_end_date'][0]
results_df['current_date'] = pd.to_datetime(results_df['current_date'])
current_date = results_df['current_date'][0]
target_cost = 300000
current_date_running_hours = results_df['current_running_hour'][0]
results_df = results_df[1:]


results_ss_df = pd.read_csv('plot/input/V-01_HX1_all_data (1).csv', sep = ',')
results_ss_df['start_date'] = pd.to_datetime(results_ss_df['start_date'])
ss_start_date = results_ss_df['start_date'][0]
results_ss_df['current_date'] = pd.to_datetime(results_ss_df['current_date'])
ss_current_date = results_ss_df['current_date'][0]




def plot_wcc_charts(st,results_df, start_date, predicted_end_date, current_date, target_cost,current_date_running_hours,key_prefix):
    # Plot 1: Total Cost Over Time
    fig1 = px.line(results_df, x='cumulative_running_hours', y='cumulative_cost', title='Total Cost Increase Over Running Hours')
    fig1.add_hline(y=target_cost, line_dash="dash", line_color="red", annotation_text=f'Target Cost (${target_cost:,.0f})',annotation_font=dict(color="red"),
                    annotation_position="bottom right")
    if current_date_running_hours is not None:
        fig1.add_vline(x=current_date_running_hours, line_dash="dot", line_color="grey",annotation_font=dict(color="grey"),
                       annotation_text=f'Current Date ({current_date.strftime("%Y-%m")})',
                       annotation_position="bottom right")
    if start_date is not None:
        fig1.add_vline(x=min(results_df['cumulative_running_hours']),
                       line_dash="dot", line_color="grey",annotation_font=dict(color="grey"),
                       annotation_text=f'Start Date ({start_date.strftime("%Y-%m-%d")})',
                       annotation_position="bottom right")

    if predicted_end_date is not None:
        fig1.add_vline(x=max(results_df['cumulative_running_hours']),
                       line_dash="dot", line_color="grey",annotation_font=dict(color="grey"),
                       annotation_text=f'End Date ({predicted_end_date.strftime("%Y-%m-%d")})',
                       annotation_position="bottom right")

    fig1.update_layout(
        plot_bgcolor="#222",
        paper_bgcolor="#222",
        font_color="white",
        title_font_color="white",
        xaxis=dict(title='Cumulative Running Hours', color='white',dtick=200),
        yaxis=dict(title='Total Cost ($)', color='white'),
        height=400,
        margin=dict(l=40, r=30, t=60, b=40)
    )
    fig1.update_traces(line_color="orange")

    # Plot 2: Power Difference Over Time
    fig2 = px.line(results_df, x='cumulative_running_hours', y='power_difference', title='Power Difference Over Running Hours')
    if current_date_running_hours is not None:
        fig2.add_vline(x=current_date_running_hours, line_dash="dot", line_color="grey",annotation_font=dict(color="grey"),
                       annotation_text=f'Current Date ({current_date.strftime("%Y-%m")})',
                       annotation_position="bottom right")
    if start_date is not None:
        fig2.add_vline(x=min(results_df['cumulative_running_hours']),
                       line_dash="dot", line_color="grey",annotation_font=dict(color="grey"),
                       annotation_text=f'Start Date ({start_date.strftime("%Y-%m-%d")})',
                       annotation_position="bottom right")

    if predicted_end_date is not None:
        fig2.add_vline(x=max(results_df['cumulative_running_hours']),
                       line_dash="dot", line_color="grey",annotation_font=dict(color="grey"),
                       annotation_text=f'End Date ({predicted_end_date.strftime("%Y-%m-%d")})',
                       annotation_position="bottom right")

    fig2.update_layout(
        plot_bgcolor="#222",
        paper_bgcolor="#222",
        font_color="white",
        title_font_color="white",
        xaxis=dict(title='Cumulative Running Hours', color='white',dtick=200),
        yaxis=dict(title='Power (kWh)', color='white'),
        height=400,
        margin=dict(l=40, r=30, t=60, b=40)
    )
    fig2.update_traces(line_color="orange")

    # Plot 3: Cumulative Small Delta T Over Time
    fig3 = px.line(results_df, x='cumulative_running_hours', y='cumulative_small_delta_t_increase', title='Cumulative Small DeltaT Over Running Hours')
    if current_date_running_hours is not None:
        fig3.add_vline(x=current_date_running_hours, line_dash="dot", line_color="grey",annotation_font=dict(color="grey"),
                       annotation_text=f'Current Date ({current_date.strftime("%Y-%m")})',
                       annotation_position="bottom right")
    if start_date is not None:
        fig3.add_vline(x=min(results_df['cumulative_running_hours']),
                       line_dash="dot", line_color="grey",annotation_font=dict(color="grey"),
                       annotation_text=f'Start Date ({start_date.strftime("%Y-%m-%d")})',
                       annotation_position="bottom right")

    if predicted_end_date is not None:
        fig3.add_vline(x=max(results_df['cumulative_running_hours']),
                       line_dash="dot", line_color="grey",annotation_font=dict(color="grey"),
                       annotation_text=f'End Date ({predicted_end_date.strftime("%Y-%m-%d")})',
                       annotation_position="bottom right")
    fig3.update_layout(
        plot_bgcolor="#222",
        paper_bgcolor="#222",
        font_color="white",
        title_font_color="white",
        xaxis=dict(title='Cumulative Running Hours', color='white',dtick=200),
        yaxis=dict(title='Cumulative Small DeltaT (°C)', color='white'),
        height=400,
        margin=dict(l=40, r=30, t=60, b=40)
    )
    fig3.update_traces(line_color="orange")

    # Display plots in Streamlit
    st.plotly_chart(fig1, use_container_width=True, key=f"{key_prefix}_fig1")
    st.plotly_chart(fig2, use_container_width=True, key=f"{key_prefix}_fig2")
    st.plotly_chart(fig3, use_container_width=True, key=f"{key_prefix}_fig3")

def plot_ss_charts(st,results_df, ss_start_date, predicted_end_date, ss_current_date, target_cost,current_date_running_hours,key_prefix):
    # Plot 1: Total Cost Over Time
    fig1 = px.line(results_ss_df, x='running_hour', y='HX1_lmtd_cumulative_change', title='HX Log Mean Temp Over Running Hours')
    if ss_start_date is not None:
        fig1.add_vline(x=min(results_ss_df['running_hour']),
                       line_dash="dot", line_color="grey",annotation_font=dict(color="grey"),
                       annotation_text=f'Start Date ({ss_start_date.strftime("%Y-%m-%d")})',
                       annotation_position="bottom right")
    if ss_current_date is not None:
        fig1.add_vline(x=max(results_ss_df['running_hour']), line_dash="dot", line_color="grey",annotation_font=dict(color="grey"),
                       annotation_text=f'Current Date ({ss_current_date.strftime("%Y-%m")})',
                       annotation_position="bottom right")

    fig1.update_layout(
        plot_bgcolor="#222",
        paper_bgcolor="#222",
        font_color="white",
        title_font_color="white",
        xaxis=dict(title='Cumulative Running Hours', color='white',dtick=1000),
        yaxis=dict(title='HX Log Mean Temp (°C)', color='white',dtick=0.05),
        height=400,
        margin=dict(l=40, r=30, t=60, b=40)
    )
    fig1.update_traces(line_color="orange")

    fig2 = px.line(results_ss_df, x='running_hour', y='HX1_supply_dt_cumulative_change',
                   title='HX Primary Side Supply DeltaT Over Running Hours')
    if ss_start_date is not None:
        fig2.add_vline(x=min(results_ss_df['running_hour']),
                       line_dash="dot", line_color="grey",annotation_font=dict(color="grey"),
                       annotation_text=f'Start Date ({ss_start_date.strftime("%Y-%m-%d")})',
                       annotation_position="bottom right")
    if ss_current_date is not None:
        fig2.add_vline(x=max(results_ss_df['running_hour']), line_dash="dot", line_color="grey",annotation_font=dict(color="grey"),
                       annotation_text=f'Current Date ({ss_current_date.strftime("%Y-%m")})',
                       annotation_position="bottom right")
    fig2.update_layout(
        plot_bgcolor="#222",
        paper_bgcolor="#222",
        font_color="white",
        title_font_color="white",
        xaxis=dict(title='Cumulative Running Hours', color='white', dtick=1000),
        yaxis=dict(title='HX Primary Side Supply DeltaT(°C)', color='white', dtick=0.05),
        height=400,
        margin=dict(l=40, r=30, t=60, b=40)
    )
    fig2.update_traces(line_color="orange")


    fig2 = px.line(results_ss_df, x='running_hour', y='HX1_supply_dt_cumulative_change',
                   title='HX Primary Side Supply DeltaT Over Running Hours')
    if ss_start_date is not None:
        fig2.add_vline(x=min(results_ss_df['running_hour']),
                       line_dash="dot", line_color="grey",annotation_font=dict(color="grey"),
                       annotation_text=f'Start Date ({ss_start_date.strftime("%Y-%m-%d")})',
                       annotation_position="bottom right")
    if ss_current_date is not None:
        fig2.add_vline(x=max(results_ss_df['running_hour']), line_dash="dot", line_color="grey",annotation_font=dict(color="grey"),
                       annotation_text=f'Current Date ({ss_current_date.strftime("%Y-%m")})',
                       annotation_position="bottom right")
    fig2.update_layout(
        plot_bgcolor="#222",
        paper_bgcolor="#222",
        font_color="white",
        title_font_color="white",
        xaxis=dict(title='Cumulative Running Hours', color='white', dtick=1000),
        yaxis=dict(title='HX Primary Side Supply DeltaT(°C)', color='white', dtick=0.05),
        height=400,
        margin=dict(l=40, r=30, t=60, b=40)
    )
    fig2.update_traces(line_color="orange")


    fig3 = px.line(results_ss_df, x='running_hour', y='HX1_primary_dp_cumulative_change',
                   title='HX Primary Side DeltaP Over Running Hours')
    if ss_start_date is not None:
        fig3.add_vline(x=min(results_ss_df['running_hour']),
                       line_dash="dot", line_color="grey",annotation_font=dict(color="grey"),
                       annotation_text=f'Start Date ({ss_start_date.strftime("%Y-%m-%d")})',
                       annotation_position="bottom right")
    if ss_current_date is not None:
        fig3.add_vline(x=max(results_ss_df['running_hour']), line_dash="dot", line_color="grey",annotation_font=dict(color="grey"),
                       annotation_text=f'Current Date ({ss_current_date.strftime("%Y-%m")})',
                       annotation_position="bottom right")
    fig3.update_layout(
        plot_bgcolor="#222",
        paper_bgcolor="#222",
        font_color="white",
        title_font_color="white",
        xaxis=dict(title='Cumulative Running Hours', color='white', dtick=1000),
        yaxis=dict(title='HX Secondary Side DeltaP(kPA)', color='white', dtick=1),
        height=400,
        margin=dict(l=40, r=30, t=60, b=40)
    )
    fig3.update_traces(line_color="orange")

    fig4 = px.line(results_ss_df, x='running_hour', y='HX1_secondary_dp_cumulative_change',
                   title='HX Secondary Side DeltaP Over Running Hours')
    if ss_start_date is not None:
        fig4.add_vline(x=min(results_ss_df['running_hour']),
                       line_dash="dot", line_color="grey",annotation_font=dict(color="grey"),
                       annotation_text=f'Start Date ({ss_start_date.strftime("%Y-%m-%d")})',
                       annotation_position="bottom right")
    if ss_current_date is not None:
        fig4.add_vline(x=max(results_ss_df['running_hour']), line_dash="dot", line_color="grey",annotation_font=dict(color="grey"),
                       annotation_text=f'Current Date ({ss_current_date.strftime("%Y-%m")})',
                       annotation_position="bottom right")
    fig4.update_layout(
        plot_bgcolor="#222",
        paper_bgcolor="#222",
        font_color="white",
        title_font_color="white",
        xaxis=dict(title='Cumulative Running Hours', color='white', dtick=1000),
        yaxis=dict(title='HX Primary Side DeltaP(kPA)', color='white', dtick=0.1),
        height=400,
        margin=dict(l=40, r=30, t=60, b=40)
    )
    fig4.update_traces(line_color="orange")

    # Display plots in Streamlit
    st.plotly_chart(fig1, use_container_width=True, key=f"{key_prefix}_fig1")
    st.plotly_chart(fig2, use_container_width=True, key=f"{key_prefix}_fig2")
    st.plotly_chart(fig3, use_container_width=True, key=f"{key_prefix}_fig3")
    st.plotly_chart(fig4, use_container_width=True, key=f"{key_prefix}_fig4")

def plot_vib_charts(st,results_df, ss_start_date, predicted_end_date, ss_current_date, target_cost,current_date_running_hours,key_prefix):
    # Parameters
    # Parameters
    num_samples = 1000  # Number of data points to generate
    time = np.linspace(0, 10, num_samples)  # Time vector

    # Generate random RMS velocity data for X, Y, Z
    x_rms = np.random.uniform(0, 4, num_samples)
    y_rms = np.random.uniform(0, 4, num_samples)
    z_rms = np.random.uniform(0, 4, num_samples)

    # ISO 10816-3 Group 1 alert lines
    normal_limit = 2.8  # Normal (Green Zone)
    warning_limit = 4.5  # Warning (Yellow Zone)

    # Create individual Plotly figures
    fig_x = go.Figure()
    fig_y = go.Figure()
    fig_z = go.Figure()

    # Plot for X RMS Velocity
    fig_x.add_trace(go.Scatter(x=time, y=x_rms, mode='lines', name='X RMS Velocity', line=dict(color='purple')))
    fig_x.add_hline(y=normal_limit, line_color='orange', line_dash='dash',
                    annotation_text='Normal Limit (2.8 mm/s)', annotation_position='top right')
    fig_x.add_hline(y=warning_limit, line_color='red', line_dash='dash',
                    annotation_text='Warning Limit (4.5 mm/s)', annotation_position='top right')
    fig_x.update_layout(title='X RMS Velocity', xaxis_title='Time (s)', yaxis_title='RMS Velocity (mm/s)',
                        template='plotly_white')

    # Plot for Y RMS Velocity
    fig_y.add_trace(go.Scatter(x=time, y=y_rms, mode='lines', name='Y RMS Velocity', line=dict(color='green')))
    fig_y.add_hline(y=normal_limit, line_color='orange', line_dash='dash',
                    annotation_text='Normal Limit (2.8 mm/s)', annotation_position='top right')
    fig_y.add_hline(y=warning_limit, line_color='red', line_dash='dash',
                    annotation_text='Warning Limit (4.5 mm/s)', annotation_position='top right')
    fig_y.update_layout(title='Y RMS Velocity', xaxis_title='Time (s)', yaxis_title='RMS Velocity (mm/s)',
                        template='plotly_white')

    # Plot for Z RMS Velocity
    fig_z.add_trace(go.Scatter(x=time, y=z_rms, mode='lines', name='Z RMS Velocity', line=dict(color='blue')))
    fig_z.add_hline(y=normal_limit, line_color='orange', line_dash='dash',
                    annotation_text='Normal Limit (2.8 mm/s)', annotation_position='top right')
    fig_z.add_hline(y=warning_limit, line_color='red', line_dash='dash',
                    annotation_text='Warning Limit (4.5 mm/s)', annotation_position='top right')
    fig_z.update_layout(title='Z RMS Velocity', xaxis_title='Time (s)', yaxis_title='RMS Velocity (mm/s)',
                        template='plotly_white')

    # Display each figure in Streamlit
    st.plotly_chart(fig_x)
    st.plotly_chart(fig_y)
    st.plotly_chart(fig_z)
