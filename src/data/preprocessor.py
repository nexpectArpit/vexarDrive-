import pandas as pd
import numpy as np
import pickle
from src.config import DATASET_PATH, PROCESSED_DATA_PATH, BUTTER_CUTOFF, BUTTER_FS, BUTTER_ORDER
from src.data.filters import apply_lowpass_filter
from src.ml.anomaly import run_anomaly_detection

def preprocess_data():
    print("Loading raw sheets from Excel...")
    drivers_df = pd.read_excel(DATASET_PATH, sheet_name='Drivers', header=2)
    vehicles_df = pd.read_excel(DATASET_PATH, sheet_name='Vehicles', header=2)
    trips_df = pd.read_excel(DATASET_PATH, sheet_name='Trips', header=2)
    telemetry_df = pd.read_excel(DATASET_PATH, sheet_name='Telemetry', header=2)

    trips_df['Trip_Date'] = pd.to_datetime(trips_df['Trip_Date'])
    vehicles_df['Registration_Date'] = pd.to_datetime(vehicles_df['Registration_Date'])
    vehicles_df['Last_Service_Date'] = pd.to_datetime(vehicles_df['Last_Service_Date'])
    
    ref_date = trips_df['Trip_Date'].max()
    vehicles_df['Days_Since_Service'] = (ref_date - vehicles_df['Last_Service_Date']).dt.days
    vehicles_df['Age_Years'] = (ref_date - vehicles_df['Registration_Date']).dt.days / 365.25

    print("Applying signal processing (Butterworth lowpass filter) on telemetry...")
    sensor_cols = ['Accel_X_g', 'Accel_Y_g', 'Accel_Z_g', 'Gyro_X_dps', 'Gyro_Y_dps', 'Gyro_Z_dps']
    
    for col in sensor_cols:
        telemetry_df[col + '_smooth'] = telemetry_df[col]
        
    for trip_id, group in telemetry_df.groupby('Trip_ID'):
        for col in sensor_cols:
            smoothed = apply_lowpass_filter(group[col], cutoff=BUTTER_CUTOFF, fs=BUTTER_FS, order=BUTTER_ORDER)
            telemetry_df.loc[group.index, col + '_smooth'] = smoothed

    print("Calculating stationary sensor biases...")
    stationary = telemetry_df[telemetry_df['Speed_kmph'] == 0]
    stationary_bias = stationary.groupby('Vehicle_ID')[sensor_cols].mean().reset_index()
    stationary_bias.columns = ['Vehicle_ID'] + [f'bias_{c}' for c in sensor_cols]
    
    print("Calculating driver risk behaviors...")
    driver_telemetry = telemetry_df.groupby('Driver_ID').agg(
        total_minutes=('Timestamp', 'count'),
        speeding_events=('Speed_kmph', lambda x: (x > 50).sum()),
        harsh_braking=('Accel_Y_g_smooth', lambda x: (x < -0.3).sum()),
        harsh_acceleration=('Accel_Y_g_smooth', lambda x: (x > 0.3).sum()),
        harsh_cornering=('Accel_X_g_smooth', lambda x: (x.abs() > 0.6).sum()),
        harsh_yaw=('Gyro_Z_dps_smooth', lambda x: (x.abs() > 35).sum())
    ).reset_index()

    for col in ['speeding_events', 'harsh_braking', 'harsh_acceleration', 'harsh_cornering', 'harsh_yaw']:
        driver_telemetry[col + '_rate'] = (driver_telemetry[col] / driver_telemetry['total_minutes']) * 60

    driver_telemetry['risk_score'] = (
        driver_telemetry['speeding_events_rate'] * 1.0 +
        driver_telemetry['harsh_braking_rate'] * 2.0 +
        driver_telemetry['harsh_acceleration_rate'] * 1.0 +
        driver_telemetry['harsh_cornering_rate'] * 1.5 +
        driver_telemetry['harsh_yaw_rate'] * 1.5
    )
    
    def segment_safety(score):
        if score >= 12:
            return 'High Risk'
        elif score >= 6:
            return 'Medium Risk'
        return 'Safe'
        
    driver_telemetry['safety_tier'] = driver_telemetry['risk_score'].apply(segment_safety)
    drivers_final = pd.merge(drivers_df, driver_telemetry, on='Driver_ID', how='inner')

    print("Analyzing vehicle telemetry and health metrics...")
    veh_vibration = telemetry_df.groupby('Vehicle_ID').agg(
        z_std=('Accel_Z_g_smooth', 'std'),
        x_std=('Accel_X_g_smooth', 'std'),
        y_std=('Accel_Y_g_smooth', 'std'),
        gyro_z_std=('Gyro_Z_dps_smooth', 'std'),
        avg_speed=('Speed_kmph', 'mean')
    ).reset_index()

    vehicles_final = pd.merge(vehicles_df, veh_vibration, on='Vehicle_ID', how='inner')
    vehicles_final = pd.merge(vehicles_final, stationary_bias, on='Vehicle_ID', how='left')
    
    bias_cols = [f'bias_{c}' for c in sensor_cols]
    vehicles_final[bias_cols] = vehicles_final[bias_cols].fillna(0)

    print("Executing Machine Learning for Vehicle Wear (Isolation Forest)...")
    vehicles_final = run_anomaly_detection(vehicles_final)

    def get_urgency(row):
        if row['health_score'] < 60:
            return 'Urgent Maintenance'
        elif row['health_score'] < 80:
            return 'Monitoring Required'
        return 'Healthy'
        
    vehicles_final['maintenance_status'] = vehicles_final.apply(get_urgency, axis=1)

    print("Saving processed states...")
    processed_data = {
        'drivers': drivers_final,
        'vehicles': vehicles_final,
        'trips': trips_df,
        'telemetry': telemetry_df
    }
    
    with open(PROCESSED_DATA_PATH, 'wb') as f:
        pickle.dump(processed_data, f)
        
    print("Preprocessing completed successfully!")

if __name__ == '__main__':
    preprocess_data()
