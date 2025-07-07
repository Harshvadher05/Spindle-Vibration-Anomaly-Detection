import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime
from collections import deque
import sys

# Add backend path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))
from data_simulator import simulate_vibration
from detect_anomaly import is_anomaly

st.set_page_config(page_title="Spindle Vibration Monitor", layout="wide")
col1, col2 = st.columns([1, 5])  # Adjust width ratio
with col1:
    st.image("backend/spindle logo.png")
with col2:
    st.title("Spindle Vibration Anomaly Detection Dashboard")

# Choose mode
mode = st.sidebar.radio("📡 Choose Monitoring Mode", ["Upload CSV", "Live Real-Time Monitor"])

# -----------------------------------------
# MODE 1: CSV Upload Detection
# -----------------------------------------
if mode == "Upload CSV":
    st.markdown("🗂️ Analyze uploaded spindle vibration data for anomalies.")
    uploaded_file = st.file_uploader("📎 Upload Vibration Data CSV", type="csv")

    if uploaded_file:
        data = pd.read_csv(uploaded_file)

        required_cols = {"timestamp", "X", "Y", "Z"}
        if not required_cols.issubset(data.columns):
            st.error("❌ CSV must contain: timestamp, X, Y, Z")
            st.stop()

        data["Anomaly"] = data[["X", "Y", "Z"]].apply(lambda row: is_anomaly(row.tolist()), axis=1)

        # Summary
        st.markdown(f"### ⚠️ Total Anomalies Detected: `{data['Anomaly'].sum()}`")
        st.line_chart(data[["X", "Y", "Z"]])

        if data["Anomaly"].sum() > 0:
            st.dataframe(data[data["Anomaly"] == True][["timestamp", "X", "Y", "Z"]])
            st.download_button("🗂️ Download Anomaly Log CSV",
                               data=data[data["Anomaly"] == True].to_csv(index=False),
                               file_name="anomaly_log.csv", mime="text/csv")
        else:
            st.success("✅ No anomalies detected.")
            
            
# -----------------------------------------
# MODE 2: Live Real-Time Monitoring
# -----------------------------------------
elif mode == "Live Real-Time Monitor":
    st.markdown("🔴 Simulated real-time monitoring with random anomaly spikes every **15–30 seconds**.")

    # -------- Session State Setup --------
    window_size = 50
    if "data_window" not in st.session_state:
        st.session_state.data_window = deque(maxlen=window_size)
    if "anomaly_count" not in st.session_state:
        st.session_state.anomaly_count = 0
    if "simulator" not in st.session_state:
        st.session_state.simulator = simulate_vibration()
    if "run_monitoring" not in st.session_state:
        st.session_state.run_monitoring = False
    if "last_run" not in st.session_state:
        st.session_state.last_run = 0

    # -------- Buttons --------
    col1, col2,col3 = st.columns(3)
    with col1:
        if st.button("🚀 Click Here to Start Live Monitoring"):
            st.session_state.run_monitoring = True
            st.session_state.last_run = 0  # Reset loop timer
    
    with col2:
        if st.button("⏹️ Stop Monitoring"):
            st.session_state.run_monitoring = False
    
    with col3:
        if st.button("🔄 Reset Monitoring"):
            st.session_state.run_monitoring = False
            st.session_state.anomaly_count = 0
            st.session_state.data_window = deque(maxlen=window_size)
            st.session_state.simulator = simulate_vibration()
            st.session_state.last_run = 0

    # -------- Persistent Placeholders (Only defined once to avoid blinking) --------
    if "chart_container" not in st.session_state:
        st.session_state.chart_container = st.empty()
    if "status_container" not in st.session_state:
        st.session_state.status_container = st.empty()
    if "log_container" not in st.session_state:
        st.session_state.log_container = st.empty()

    # -------- Log File --------
    log_file = os.path.join("logs", "anomaly_log_realtime.csv")
    os.makedirs("logs", exist_ok=True)
    if not os.path.exists(log_file):
        with open(log_file, "w") as f:
            f.write("timestamp,X,Y,Z\n")

    # -------- Live Monitoring Loop --------
    if st.session_state.run_monitoring:
        current_time = time.time()
        if current_time - st.session_state.last_run >= 0.5:
            vibration = next(st.session_state.simulator)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            is_anom = is_anomaly(vibration)

            st.session_state.data_window.append({
                "timestamp": timestamp,
                "X": vibration[0],
                "Y": vibration[1],
                "Z": vibration[2],
                "Anomaly": is_anom
            })

            df = pd.DataFrame(st.session_state.data_window)
            st.session_state.chart_container.line_chart(df[["X", "Y", "Z"]])

            if is_anom:
                st.session_state.anomaly_count += 1
                st.session_state.status_container.error(f"⚠️ Anomaly #{st.session_state.anomaly_count} at {timestamp}")
                with open(log_file, "a") as f:
                    f.write(f"{timestamp},{vibration[0]},{vibration[1]},{vibration[2]}\n")
            else:
                st.session_state.status_container.success(f"✅ Normal at {timestamp}")

            st.session_state.log_container.markdown(f"**Total Anomalies:** `{st.session_state.anomaly_count}`")

            st.session_state.last_run = current_time

        time.sleep(0.5)
        st.rerun()

    # -------- After Monitoring Ends --------
    if not st.session_state.run_monitoring and len(st.session_state.data_window) > 0:
        df = pd.DataFrame(st.session_state.data_window)
        st.subheader("📈 Last Recorded Vibration Chart")
        st.line_chart(df[["X", "Y", "Z"]])

        st.subheader("📋 Final Anomaly Summary")
        st.markdown(f"**Total Anomalies Detected:** `{st.session_state.anomaly_count}`")

        if df["Anomaly"].any():
            st.markdown("**🕒 Timestamps of Anomalies:**")
            anomaly_df = df[df["Anomaly"] == True][["timestamp", "X", "Y", "Z"]]
            st.dataframe(anomaly_df)

            # ✅ Download Button
            csv_data = anomaly_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="🗂️ Download Anomaly Log (CSV)",
                data=csv_data,
                file_name="anomaly_log.csv",
                mime="text/csv"
            )
        else:
            st.success("✅ No anomalies detected in last session.")


# --------------------------------------------------------------------------------------------------------(first simple version)
# # -----------------------------------------
# # MODE 2: Live Real-Time Monitoring
# # -----------------------------------------
# elif mode == "Live Real-Time Monitor":
#     st.markdown("🔴 **Simulated real-time monitoring with random anomaly spikes every 10–20s**")

#     # ------------------ Session State Setup ------------------
#     window_size = 50
#     if "data_window" not in st.session_state:
#         st.session_state.data_window = deque(maxlen=window_size)
#     if "anomaly_count" not in st.session_state:
#         st.session_state.anomaly_count = 0
#     if "simulator" not in st.session_state:
#         st.session_state.simulator = simulate_vibration()
#     if "run_monitoring" not in st.session_state:
#         st.session_state.run_monitoring = False

#     # ------------------ Buttons (Always Visible) ------------------
#     col1, col2 = st.columns(2)
#     with col1:
#         label = "⏹️ Stop Monitoring" if st.session_state.run_monitoring else "▶️ Start Monitoring"
#         if st.button(label):
#             st.session_state.run_monitoring = not st.session_state.run_monitoring
#     with col2:
#         if st.button("🔄 Reset Monitoring"):
#             st.session_state.run_monitoring = False
#             st.session_state.anomaly_count = 0
#             st.session_state.data_window = deque(maxlen=window_size)
#             st.session_state.simulator = simulate_vibration()

#     # ------------------ Placeholders ------------------
#     chart_placeholder = st.empty()
#     status_placeholder = st.empty()
#     log_placeholder = st.empty()

#     # Create log file if not exists
#     log_file = os.path.join("logs", "anomaly_log_realtime.csv")
#     os.makedirs("logs", exist_ok=True)
#     if not os.path.exists(log_file):
#         with open(log_file, "w") as f:
#             f.write("timestamp,X,Y,Z\n")

#     # ------------------ Monitoring Logic ------------------
#     if st.session_state.run_monitoring:
#         # Collect new vibration reading
#         vibration = next(st.session_state.simulator)
#         timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#         is_anom = is_anomaly(vibration)

#         # Store in session state
#         st.session_state.data_window.append({
#             "timestamp": timestamp,
#             "X": vibration[0],
#             "Y": vibration[1],
#             "Z": vibration[2],
#             "Anomaly": is_anom
#         })

#         # Draw chart without blinking
#         df = pd.DataFrame(st.session_state.data_window)
#         chart_placeholder.line_chart(df[["X", "Y", "Z"]])

#         # Show status message
#         if is_anom:
#             st.session_state.anomaly_count += 1
#             status_placeholder.error(f"⚠️ Anomaly #{st.session_state.anomaly_count} at {timestamp}")
#             with open(log_file, "a") as f:
#                 f.write(f"{timestamp},{vibration[0]},{vibration[1]},{vibration[2]}\n")
#         else:
#             status_placeholder.success(f"✅ Normal at {timestamp}")

#         log_placeholder.markdown(f"**Total Anomalies:** `{st.session_state.anomaly_count}`")

#         # Wait and rerun
#         time.sleep(0.5)
#         st.rerun()  # Safe in 1.46.1

#     # ------------------ After Monitoring ------------------
#     if not st.session_state.run_monitoring and len(st.session_state.data_window) > 0:
#         df = pd.DataFrame(st.session_state.data_window)
#         st.subheader("📈 Last Recorded Vibration Chart")
#         st.line_chart(df[["X", "Y", "Z"]])

#         st.subheader("📊 Final Anomaly Summary")
#         st.markdown(f"**Total Anomalies Detected:** `{st.session_state.anomaly_count}`")

#         if df["Anomaly"].any():
#             st.markdown("**🕒 Timestamps of Anomalies:**")
#             st.dataframe(df[df["Anomaly"] == True][["timestamp", "X", "Y", "Z"]])
#         else:
#             st.success("✅ No anomalies detected in last session.")




# # ------------------------------------------------------------------------------------------------------(done but still blinking)
# # -----------------------------------------
# # MODE 2: Live Real-Time Monitoring
# # -----------------------------------------
# elif mode == "Live Real-Time Monitor":
#     st.markdown("🔴 Simulated real-time monitoring with random anomaly spikes every **15–30 seconds**.")
#     st.markdown("#### 🕒 Anomalies are injected every ~15–30 seconds (random)")

#     # -------- Session State Setup --------
#     window_size = 50
#     if "data_window" not in st.session_state:
#         st.session_state.data_window = deque(maxlen=window_size)
#     if "anomaly_count" not in st.session_state:
#         st.session_state.anomaly_count = 0
#     if "simulator" not in st.session_state:
#         st.session_state.simulator = simulate_vibration()
#     if "run_monitoring" not in st.session_state:
#         st.session_state.run_monitoring = False
#     if "last_run" not in st.session_state:
#         st.session_state.last_run = 0

#     # -------- Buttons --------
#     col1, col2, col3 = st.columns(3)
#     with col1:
#         if st.button("▶️ Start Monitoring"):
#             st.session_state.run_monitoring = True
#     with col2:
#         if st.button("⏹️ Stop Monitoring"):
#             st.session_state.run_monitoring = False
#     with col3:
#         if st.button("🔄 Reset Monitoring"):
#             st.session_state.run_monitoring = False
#             st.session_state.anomaly_count = 0
#             st.session_state.data_window = deque(maxlen=window_size)
#             st.session_state.simulator = simulate_vibration()

#     # -------- Placeholders --------
#     chart_placeholder = st.empty()
#     status_placeholder = st.empty()
#     log_placeholder = st.empty()

#     # -------- Log File --------
#     log_file = os.path.join("logs", "anomaly_log_realtime.csv")
#     os.makedirs("logs", exist_ok=True)
#     if not os.path.exists(log_file):
#         with open(log_file, "w") as f:
#             f.write("timestamp,X,Y,Z\n")

#     # -------- Main Monitoring Display --------
#     if st.session_state.run_monitoring:
#         current_time = time.time()
#         if current_time - st.session_state.last_run >= 0.5:
#             vibration = next(st.session_state.simulator)
#             timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#             is_anom = is_anomaly(vibration)

#             st.session_state.data_window.append({
#                 "timestamp": timestamp,
#                 "X": vibration[0],
#                 "Y": vibration[1],
#                 "Z": vibration[2],
#                 "Anomaly": is_anom
#             })

#             df = pd.DataFrame(st.session_state.data_window)
#             chart_placeholder.line_chart(df[["X", "Y", "Z"]])

#             if is_anom:
#                 st.session_state.anomaly_count += 1
#                 status_placeholder.error(f"⚠️ Anomaly #{st.session_state.anomaly_count} at {timestamp}")
#                 with open(log_file, "a") as f:
#                     f.write(f"{timestamp},{vibration[0]},{vibration[1]},{vibration[2]}\n")
#             else:
#                 status_placeholder.success(f"✅ Normal at {timestamp}")

#             log_placeholder.markdown(f"**Total Anomalies:** `{st.session_state.anomaly_count}`")
#             st.session_state.last_run = current_time

#         # Refresh only every 500ms (prevents blinking)
#         time.sleep(0.5)
#         st.rerun()
    

#     # -------- After Stop --------
#     if not st.session_state.run_monitoring and len(st.session_state.data_window) > 0:
#         df = pd.DataFrame(st.session_state.data_window)
#         st.subheader("📈 Last Recorded Vibration Chart")
#         st.line_chart(df[["X", "Y", "Z"]])

#         st.subheader("📊 Final Anomaly Summary")
#         st.markdown(f"**Total Anomalies Detected:** `{st.session_state.anomaly_count}`")

#         if df["Anomaly"].any():
#             st.markdown("**🕒 Timestamps of Anomalies:**")
#             st.dataframe(df[df["Anomaly"] == True][["timestamp", "X", "Y", "Z"]])
#         else:
#             st.success("✅ No anomalies detected in last session.")
