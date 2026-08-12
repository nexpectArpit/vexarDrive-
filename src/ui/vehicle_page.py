import streamlit as st
import pandas as pd
import plotly.express as px
from src.ui.common import layout_theme

def render_vehicle_page(vehicles):
    st.markdown("<h1 class='main-title'>Vehicle Health Dashboard</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Analyze mechanical wear, suspension degradation, and sensor calibration metrics across the fleet.</p>", unsafe_allow_html=True)

    urgent_count = len(vehicles[vehicles['maintenance_status'] == 'Urgent Maintenance'])
    monitor_count = len(vehicles[vehicles['maintenance_status'] == 'Monitoring Required'])
    avg_health = vehicles['health_score'].mean()

    st.markdown(f"""
    <div class="metric-grid">
        <div class="kpi-card">
            <div class="kpi-title">Urgent Workshop Service</div>
            <div class="kpi-value">{urgent_count}</div>
            <div class="kpi-delta text-red">Book maintenance immediately</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">Monitoring Required</div>
            <div class="kpi-value">{monitor_count}</div>
            <div class="kpi-delta text-amber">Flagged for vibration drift</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">Average Fleet Health</div>
            <div class="kpi-value">{avg_health:.1f}%</div>
            <div class="kpi-delta text-emerald">Within safety margins</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<h3 class='section-header'>Critical Maintenance Alerts</h3>", unsafe_allow_html=True)
    urgent_vehicles = vehicles[vehicles['maintenance_status'] == 'Urgent Maintenance']
    
    if not urgent_vehicles.empty:
        for idx, row in urgent_vehicles.iterrows():
            st.markdown(
                f"<div class='custom-alert alert-urgent'>"
                f"<strong>Vehicle {row['Vehicle_ID']} ({row['Make']} {row['Model']})</strong>: "
                f"Health Score: {row['health_score']}% | Odometer: {row['Odometer_KM_Start_of_Week']} KM | "
                f"Days Since Service: {row['Days_Since_Service']} | Vibration (Z-std): {row['z_std']:.3f}g.<br>"
                f"<span class='justification-text'>Diagnostic Justification: Excess structural noise indicates mechanical wear. Odometer limits reached.</span>"
                f"</div>",
                unsafe_allow_html=True
            )
    else:
        st.success("All vehicles are operating within normal mechanical thresholds.")
 
    st.markdown("<h3 class='section-header'>Sensor Calibration & Stationary Offsets <span class='tooltip'>ⓘ<span class='tooltiptext'><b>Why we use this diagnostics sheet</b>:<br>Assesses telemetry data integrity when stationary (Speed == 0). Ideal offsets should read 0.0 for horizontal/gyroscope axes, and 1.0 for gravity on the Z-axis.<br><br><b>Action</b>:<br>Flag vehicles with high bias offsets (colored cells). This indicates loose phone mounts or sensor hardware drift distorting score accuracy.</span></span></h3>", unsafe_allow_html=True)
    st.write("Verifies sensor zero-biases when the vehicle is stationary. Drift offsets identify loose phone mounts or sensor calibration anomalies.")
    
    diag_df = vehicles[[
        'Vehicle_ID', 'Make', 'Model', 'Odometer_KM_Start_of_Week', 'Days_Since_Service', 
        'z_std', 'bias_Accel_X_g', 'bias_Accel_Y_g', 'bias_Accel_Z_g', 'bias_Gyro_Z_dps', 'health_score'
    ]]
    diag_df.columns = [
        'Vehicle ID', 'Make', 'Model', 'Odometer (KM)', 'Days Since Service', 
        'Vibration (Z-std)', 'Bias Accel X', 'Bias Accel Y', 'Bias Accel Z', 'Bias Gyro Yaw', 'Health Score'
    ]
    
    st.dataframe(
        diag_df.style.format({
            'Vibration (Z-std)': '{:.3f}', 'Bias Accel X': '{:.3f}', 'Bias Accel Y': '{:.3f}',
            'Bias Accel Z': '{:.3f}', 'Bias Gyro Yaw': '{:.3f}', 'Health Score': '{:.1f}%'
        }).background_gradient(subset=['Vibration (Z-std)', 'Bias Accel X'], cmap='Blues'),
        use_container_width=True,
        hide_index=True
    )

    st.markdown("<h3 class='section-header'>Odometer Mileage vs. Suspension Vibration <span class='tooltip'>ⓘ<span class='tooltiptext'><b>Why we use this chart</b>:<br>Visualizes suspension wear patterns across odometer travel mileage and structural vibration metrics. Bubble sizes indicate service recency.<br><br><b>Action</b>:<br>Prioritize maintenance for high-mileage, high-vibration vehicles (red markers, top-right), and inspect recently serviced units showing high vibration.</span></span></h3>", unsafe_allow_html=True)
    fig_scatter = px.scatter(
        vehicles, x='Odometer_KM_Start_of_Week', y='z_std',
        size='Days_Since_Service', color='maintenance_status',
        color_discrete_map={
            'Urgent Maintenance': '#ef4444',
            'Monitoring Required': '#f59e0b',
            'Healthy': '#10b981'
        },
        hover_data=['Vehicle_ID', 'Make', 'Model', 'health_score', 'Days_Since_Service'],
        labels={
            'Odometer_KM_Start_of_Week': 'Odometer (KM)',
            'z_std': 'Suspension Vibration (Z-axis std dev)',
            'maintenance_status': 'Maintenance Status'
        }
    )
    fig_scatter.update_layout(layout_theme)
    st.plotly_chart(fig_scatter, use_container_width=True, config={'displayModeBar': False})

    st.markdown("<h3 class='section-header'>Future Opportunities Beyond the Dashboard</h3>", unsafe_allow_html=True)
    
    col_u1, col_u2 = st.columns(2)
    with col_u1:
        st.markdown("""
        <div class="business-card">
            <h4 class="future-opportunity-title">Road Quality Mapping (Pothole Detection)</h4>
            <p class="future-opportunity-desc">
                By aggregating vertical vibration metrics (Accel_Z_g_smooth standard deviation) across 
                geographic coordinate boundaries, VexarDrive can create a live heatmap of road damage. 
                Riders can be routed away from highly damaged roads to protect vehicle suspensions and cargo.
            </p>
        </div>
        <div class="business-card business-card-margin-top">
            <h4 class="future-opportunity-title">Predictive Maintenance Models</h4>
            <p class="future-opportunity-desc">
                Rather than simple time-based servicing, the fleet can transition to proactive scheduling. 
                By monitoring real-time changes in vertical vibration and gyroscope noise thresholds, the system 
                can trigger automated service check-ins when wear indicators exceed normal baseline limits.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
    with col_u2:
        st.markdown("""
        <div class="business-card">
            <h4 class="future-opportunity-title">Usage-Based Insurance (UBI)</h4>
            <p class="future-opportunity-desc">
                Insurance premiums can be directly linked to individual safety ratings. 
                Riders with low risk scores (like D09 or D11) can receive insurance discounts, promoting 
                safer driving behaviors across the fleet.
            </p>
        </div>
        <div class="business-card business-card-margin-top">
            <h4 class="future-opportunity-title">Gamified Incentives & Safety Bonuses</h4>
            <p class="future-opportunity-desc">
                Introduce peer-group leaderboards inside the driver app. Safe rider badges, fuel efficiency scores, 
                and minor cash bonuses for safe profiles encourage friendly competition and reduce fleet accident rates.
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div class='credit-badge'>-by Arpit tripathi</div>", unsafe_allow_html=True)

