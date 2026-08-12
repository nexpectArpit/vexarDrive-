# VexarDrive Fleet Analytics Portal

This project provides a data preprocessing pipeline and interactive dashboards to analyze driver behavior and vehicle health for a two-wheeler delivery fleet.

## Project Structure

*   `app.py`: Launches the main Streamlit dashboard application routing system.
*   `assets/`: Contains isolated design layouts and style resources:
    *   `style.css`: Clean light mode styling based on Rapido aesthetics.
    *   `animation.css`: Isolated styling for chase bike cursor and tooltips.
*   `dataset/`: Contains raw datasets:
    *   `VEXAR_Fleet_Dataset_CANDIDATE_VERSION.xlsx`: The raw excel sheet.
*   `src/`: Core source modules:
    *   `config.py`: Central configurations and dataset paths.
    *   `data/filters.py`: Signal processing modules (Butterworth low-pass filtering).
    *   `data/preprocessor.py`: Raw Excel ingestion and driver risk behavior calculation.
    *   `ml/anomaly.py`: Isolation Forest anomaly detection engine for suspension wear.
    *   `ui/common.py`: Shared UI asset loaders, custom cursors, and logo card components.
    *   `ui/driver_page.py`: Renders driver profiling, safety leaderboards, and OSRM maps.
    *   `ui/vehicle_page.py`: Renders maintenance alerts, calibration diagnostic grids, and scatter plots.
*   `requirements.txt`: Lists Python dependencies.
*   `Dockerfile`: Containerization script.

## How to Run Locally

1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the preprocessing module:
   ```bash
   python3 -m src.data.preprocessor
   ```

3. Start the Streamlit application:
   ```bash
   streamlit run app.py
   ```

## How to Run with Docker

1. Build the Docker image:
   ```bash
   docker build -t vexardrive-analytics .
   ```

2. Run the container:
   ```bash
   docker run -p 8501:8501 vexardrive-analytics
   ```

3. Open your browser and navigate to:
   `http://localhost:8501`
