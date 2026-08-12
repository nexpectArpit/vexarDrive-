import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px
import plotly.graph_objects as go
from src.ui.common import layout_theme

def render_driver_page(drivers, trips, telemetry, get_road_route):
    st.markdown("<h1 class='main-title'>Driver Behaviour Dashboard</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Evaluate, score, and rank rider safety indicators. Metrics are normalized per hour of active telemetry.</p>", unsafe_allow_html=True)

    avg_risk = drivers['risk_score'].mean()
    high_risk_count = len(drivers[drivers['safety_tier'] == 'High Risk'])
    medium_risk_count = len(drivers[drivers['safety_tier'] == 'Medium Risk'])
    safe_count = len(drivers[drivers['safety_tier'] == 'Safe'])

    st.markdown(f"""
    <div class="metric-grid">
        <div class="kpi-card">
            <div class="kpi-title">Fleet Risk Score (Avg)</div>
            <div class="kpi-value">{avg_risk:.2f}</div>
            <div class="kpi-delta text-red">↑ 1.2% this week</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">High Risk Riders</div>
            <div class="kpi-value">{high_risk_count}</div>
            <div class="kpi-delta text-darkred">Requires policy intervention</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">Medium Risk Riders</div>
            <div class="kpi-value">{medium_risk_count}</div>
            <div class="kpi-delta text-amber">Bi-weekly monitoring</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">Low Risk Riders</div>
            <div class="kpi-value">{safe_count}</div>
            <div class="kpi-delta text-emerald">Eligible for rewards</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<h3 class='section-header'>Rider Safety Leaderboard</h3>", unsafe_allow_html=True)
    leaderboard_df = drivers[[
        'Driver_ID', 'Driver_Name', 'Home_Hub', 'total_minutes', 
        'risk_score', 'safety_tier', 'speeding_events_rate', 
        'harsh_braking_rate', 'harsh_cornering_rate', 'harsh_yaw_rate'
    ]].sort_values('risk_score', ascending=False)
    
    leaderboard_df.columns = [
        'Driver ID', 'Name', 'Home Hub', 'Active Minutes', 
        'Risk Score', 'Safety Tier', 'Speeding / Hr', 
        'Harsh Braking / Hr', 'Harsh Cornering / Hr', 'Swerving / Hr'
    ]
    
    st.dataframe(
        leaderboard_df.style.format({
            'Risk Score': '{:.2f}', 'Speeding / Hr': '{:.2f}',
            'Harsh Braking / Hr': '{:.2f}', 'Harsh Cornering / Hr': '{:.2f}', 'Swerving / Hr': '{:.2f}'
        }).background_gradient(subset=['Risk Score'], cmap='Reds'),
        use_container_width=True,
        hide_index=True
    )

    st.markdown("<h3 class='section-header'>Individual Rider Profiler</h3>", unsafe_allow_html=True)
    selected_driver_id = st.selectbox("Select a Driver to Inspect:", drivers['Driver_ID'].unique())
    
    driver_row = drivers[drivers['Driver_ID'] == selected_driver_id].iloc[0]
    
    col_d1, col_d2 = st.columns([1, 2])
    with col_d1:
        st.markdown(f"""
        <div class="business-card full-height">
            <h4 class="business-card-title">Rider Profile: {driver_row['Driver_Name']}</h4>
            <table class="profile-table">
                <tr><td class="profile-table-label">Driver ID</td><td class="profile-table-val-right"><code>{selected_driver_id}</code></td></tr>
                <tr><td class="profile-table-label">Age / Gender</td><td class="profile-table-val-right">{driver_row['Age']} yrs / {driver_row['Gender']}</td></tr>
                <tr><td class="profile-table-label">Experience</td><td class="profile-table-val-right">{driver_row['License_Experience_Years']} Years</td></tr>
                <tr><td class="profile-table-label">Hub Locality</td><td class="profile-table-val-right">{driver_row['Home_Hub']}</td></tr>
                <tr><td class="profile-table-label">Primary Vehicle</td><td class="profile-table-val-right"><code>{driver_row['Primary_Vehicle_ID']}</code></td></tr>
                <tr><td class="profile-table-label">Safety Tier</td><td class="profile-table-val-right bold-blue">{driver_row['safety_tier']}</td></tr>
                <tr><td class="profile-table-label bold-red">Risk Score</td><td class="profile-table-val-right bold-red">{driver_row['risk_score']:.2f}</td></tr>
            </table>
            <div class="profile-note-box">
                <strong>Justification Score Breakdown:</strong><br>
                The risk rating is calculated using sensor alerts normalized per active driving duration. 
                Rider has {driver_row['speeding_events_rate']:.1f} speeding mins/hr and {driver_row['harsh_braking_rate']:.1f} decel counts/hr.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_d2:
        rates = pd.DataFrame({
            'Metric': ['Speeding Rate', 'Harsh Braking', 'Harsh Accel', 'Harsh Cornering', 'Swerving (Yaw)'],
            'Events per Hour': [
                driver_row['speeding_events_rate'],
                driver_row['harsh_braking_rate'],
                driver_row['harsh_acceleration_rate'],
                driver_row['harsh_cornering_rate'],
                driver_row['harsh_yaw_rate']
            ]
        })
        st.markdown("#### Hourly Offense Rates <span class='tooltip'>ⓘ<span class='tooltiptext'><b>Why we use this chart</b>:<br>Identifies specific dangerous riding habits by normalizing safety occurrences per active hour.<br><br><b>Action</b>:<br>Target drivers exceeding 1.0 offense/hr in any category for custom safety coaching.</span></span>", unsafe_allow_html=True)
        fig_rates = px.bar(
            rates, x='Events per Hour', y='Metric', orientation='h',
            color='Events per Hour', color_continuous_scale=['#f3f4f6', '#FFDD00'],
            labels={'Events per Hour': 'Events / Hr'},
            title=""
        )
        fig_rates.update_layout(layout_theme)
        st.plotly_chart(fig_rates, use_container_width=True, config={'displayModeBar': False})

    st.markdown("<h3 class='section-header'>Trip Spatial Route Map <span class='tooltip'>ⓘ<span class='tooltiptext'><b>Why we use this map</b>:<br>Traces active delivery routes and highlights spatial coordinates of harsh deceleration events.<br><br><b>Action</b>:<br>Analyze cluster boundaries to identify hazardous roads, speed anomalies, or route delays.</span></span></h3>", unsafe_allow_html=True)
    driver_trips = trips[trips['Driver_ID'] == selected_driver_id]
    driver_telemetry = telemetry[telemetry['Driver_ID'] == selected_driver_id]
    
    if not driver_trips.empty:
        selected_trip_id = st.selectbox(
            "Select Trip to Inspect Route:", 
            driver_trips['Trip_ID'].unique(),
            key=f"trip_select_{selected_driver_id}"
        )
        
        trip_row = driver_trips[driver_trips['Trip_ID'] == selected_trip_id].iloc[0]
        trip_telemetry = driver_telemetry[driver_telemetry['Trip_ID'] == selected_trip_id].sort_values('Timestamp')
        
        map_center = [trip_row['Start_Latitude'], trip_row['Start_Longitude']]
        m = folium.Map(location=map_center, zoom_start=13)
        
        folium.Marker(
            location=[trip_row['Start_Latitude'], trip_row['Start_Longitude']],
            popup=f"Trip {selected_trip_id} Start",
            icon=folium.Icon(color='green', icon='play')
        ).add_to(m)
        
        folium.Marker(
            location=[trip_row['End_Latitude'], trip_row['End_Longitude']],
            popup=f"Trip {selected_trip_id} End",
            icon=folium.Icon(color='red', icon='stop')
        ).add_to(m)
        
        road_route = get_road_route(
            trip_row['Start_Latitude'], trip_row['Start_Longitude'],
            trip_row['End_Latitude'], trip_row['End_Longitude']
        )
        
        folium.PolyLine(
            road_route,
            color='#111111',
            width=5,
            opacity=0.8,
            popup=f"Trip {selected_trip_id} Route Path (Street Grid)"
        ).add_to(m)
        
        if not trip_telemetry.empty:
            harsh_braking_coords = trip_telemetry[trip_telemetry['Accel_Y_g_smooth'] < -0.3]
            for idx, r_tel in harsh_braking_coords.iterrows():
                folium.CircleMarker(
                    location=[r_tel['Latitude'], r_tel['Longitude']],
                    radius=8,
                    color='red',
                    fill=True,
                    fill_color='red',
                    fill_opacity=0.8,
                    popup=f"Harsh Decel: {r_tel['Accel_Y_g_smooth']:.2f}g"
                ).add_to(m)
            
        st_folium(m, height=450, width=1200, key=f"map_{selected_driver_id}")
    else:
        st.warning("No trips recorded for this driver.")

    st.markdown("<h3 class='section-header'>Signal Noise Filtering Justification <span class='tooltip'>ⓘ<span class='tooltiptext'><b>Why we use this visualization</b>:<br>Compares raw high-frequency mobile sensor signals with Butterworth low-pass filtered outputs to demonstrate sensor noise removal.<br><br><b>Action</b>:<br>Verifies that safety scoring algorithms are only triggered by physical riding anomalies, protecting safe driver safety ratings.</span></span></h3>", unsafe_allow_html=True)
    st.write("A digital low-pass Butterworth filter isolates actual vehicle movements by attenuating high-frequency phone vibration noise.")
    
    sample_trip_id = st.selectbox("Select a Trip to inspect raw vs. smoothed signals:", telemetry['Trip_ID'].unique()[:10])
    trip_data = telemetry[telemetry['Trip_ID'] == sample_trip_id]
    
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.markdown("#### Longitudinal Acceleration - Braking & Accel")
        fig_y = go.Figure()
        fig_y.add_trace(go.Scatter(x=trip_data['Timestamp'], y=trip_data['Accel_Y_g'], mode='lines', name='Raw (Noisy)', line=dict(color='#fca5a5', width=1)))
        fig_y.add_trace(go.Scatter(x=trip_data['Timestamp'], y=trip_data['Accel_Y_g_smooth'], mode='lines', name='Butterworth Filtered', line=dict(color='#111111', width=2.5)))
        fig_y.update_layout(layout_theme)
        fig_y.update_layout(margin=dict(l=10, r=10, t=30, b=10), height=350)
        st.plotly_chart(fig_y, use_container_width=True, config={'displayModeBar': False})
        
    with col_chart2:
        st.markdown("#### Gyroscope Yaw Rate - Turning & Swerving")
        fig_z = go.Figure()
        fig_z.add_trace(go.Scatter(x=trip_data['Timestamp'], y=trip_data['Gyro_Z_dps'], mode='lines', name='Raw (Noisy)', line=dict(color='#fca5a5', width=1)))
        fig_z.add_trace(go.Scatter(x=trip_data['Timestamp'], y=trip_data['Gyro_Z_dps_smooth'], mode='lines', name='Butterworth Filtered', line=dict(color='#111111', width=2.5)))
        fig_z.update_layout(layout_theme)
        fig_z.update_layout(margin=dict(l=10, r=10, t=30, b=10), height=350)
        st.plotly_chart(fig_z, use_container_width=True, config={'displayModeBar': False})

    st.markdown("<div class='credit-badge'>-by Arpit tripathi</div>", unsafe_allow_html=True)

