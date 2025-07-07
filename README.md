# Spindle Vibration Anomaly Detection

## Project Overview

This software-only project simulates real-time spindle vibration data and uses an AI model to detect anomalies (e.g., misalignment or tool wear). If an anomaly is detected, an alert is displayed and you can download also log text file.<br>
Detects abnormal vibration patterns using AI — without any physical hardware — using simulated MPU6050-like sensor data.
<br><br>
here is 2 type of option available
- you can detect anomalies from csv file of vibration data in well structured.
- you can get result from random generated data at real time(later you can use sensors).

## 📁 Project Structure

- `backend/`: Simulation + AI detection + email alerts
- `dashboard/`: Streamlit live chart
- `data/`: Placeholder for vibration logs

## ✅ Your Setup = 100% Software-Simulated

| Component        | Real Setup                       | Your Setup (✅)                          |
|------------------|----------------------------------|------------------------------------------|
| Vibration sensor | Physical sensor (e.g., MEMS)     | `simulate_vibration()` generator         |
| Live data stream | From machine PLC or MQTT         | Simulated with Python loop               |
| Detection system | On-device or edge gateway        | Python + Autoencoder                     |
| Dashboard        | HMI or SCADA                     | Streamlit                                |


## How to Run

1. Install dependencies:

   ```bash
   pip install -r backend/requirements.txt
   ```

2. Add Pretrained AI Model / train module (backend/train_model.py)

   ```bash
   backend/model/autoencoder_model.h5
   ```

   or

   ```bash
   cd backend
   mkdir model
   python train_model.py
   ```

3. Run Dashboard

   ```bash
   streamlit run dashboard/app.py
   ```

## Features

- ✅ Real-time synthetic data generation
- ✅ Autoencoder-based anomaly detection
- ✅ Anomaly count + timestamps logging
- ✅ Live Streamlit dashboard with charts
- ✅ Email alert system (via Gmail SMTP)
- ✅ Reset and Pause monitoring controls
- ✅ No hardware needed (100% simulation)

---

## 🛠️ In the Future (Optional Hardware Setup)

If you later want to test on **real hardware**, you'd need:

- A vibration sensor (e.g., MPU6050, ADXL345)  
- A microcontroller (Arduino / Raspberry Pi)  
- A way to send data to your backend (USB, WiFi, MQTT)  
- Modify `simulate_vibration()` to read from the sensor

