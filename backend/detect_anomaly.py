import os
import joblib
import numpy as np
from keras.models import load_model

# Get absolute path to model directory
base_dir = os.path.dirname(os.path.abspath(__file__))
model_dir = os.path.join(base_dir, "model")
scaler_path = os.path.join(model_dir, "scaler.pkl")
model_path = os.path.join(model_dir, "autoencoder_model.h5")

# Load model and scaler
model = load_model(model_path)
scaler = joblib.load(scaler_path)

def is_anomaly(vibration_data):
    data = scaler.transform([vibration_data])
    reconstruction = model.predict(data, verbose=0)
    mse = np.mean(np.power(data - reconstruction, 2))
    return mse > 0.01  # You can tweak this threshold
