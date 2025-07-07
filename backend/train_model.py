import numpy as np
from sklearn.preprocessing import MinMaxScaler
from keras.models import Model
from keras.layers import Input, Dense
from keras.optimizers import Adam
import joblib
import os

# Generate synthetic normal spindle vibration data
normal_data = np.random.normal(loc=0.0, scale=0.5, size=(1000, 3))

# Normalize data
scaler = MinMaxScaler()
normal_data_scaled = scaler.fit_transform(normal_data)

# Build autoencoder
input_dim = normal_data_scaled.shape[1]
input_layer = Input(shape=(input_dim,))
encoded = Dense(4, activation='relu')(input_layer)
encoded = Dense(2, activation='relu')(encoded)
decoded = Dense(4, activation='relu')(encoded)
decoded = Dense(input_dim, activation='sigmoid')(decoded)

autoencoder = Model(inputs=input_layer, outputs=decoded)
autoencoder.compile(optimizer=Adam(learning_rate=0.001), loss='mse')

# Train the model
autoencoder.fit(normal_data_scaled, normal_data_scaled,
                epochs=50, batch_size=32, verbose=1)

# Save model
os.makedirs("model", exist_ok=True)
autoencoder.save("model/autoencoder_model.h5")

# ✅ Save the scaler for use during detection
joblib.dump(scaler, "model/scaler.pkl")
print("✅ Model and scaler saved in 'model/' directory")
