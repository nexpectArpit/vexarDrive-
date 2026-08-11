from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

def run_anomaly_detection(vehicles_final):
    vehicles_final['bias_error_x'] = vehicles_final['bias_Accel_X_g'].abs()
    vehicles_final['bias_error_y'] = vehicles_final['bias_Accel_Y_g'].abs()
    vehicles_final['bias_error_z'] = (vehicles_final['bias_Accel_Z_g'] - 1.0).abs()
    vehicles_final['bias_error_gyro_z'] = vehicles_final['bias_Gyro_Z_dps'].abs()
    
    ml_features = ['z_std', 'Days_Since_Service', 'Odometer_KM_Start_of_Week', 
                   'bias_error_x', 'bias_error_z', 'bias_error_gyro_z']
    
    scaler = StandardScaler()
    scaled_feats = scaler.fit_transform(vehicles_final[ml_features])
    
    clf = IsolationForest(contamination=0.1, random_state=42)
    vehicles_final['anomaly_score'] = clf.fit_predict(scaled_feats)
    raw_scores = clf.decision_function(scaled_feats)
    min_s, max_s = raw_scores.min(), raw_scores.max()
    vehicles_final['health_score'] = 100.0 - (((raw_scores - min_s) / (max_s - min_s)) * 30.0 + 5.0)
    
    for idx, row in vehicles_final.iterrows():
        score = vehicles_final.at[idx, 'health_score']
        if row['Days_Since_Service'] > 60:
            score = min(score, 75.0)
        if row['z_std'] > 0.12:
            score = min(score, 50.0)
        vehicles_final.at[idx, 'health_score'] = round(score, 1)
        
    return vehicles_final
