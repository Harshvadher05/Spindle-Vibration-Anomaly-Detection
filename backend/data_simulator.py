def simulate_vibration():
    import numpy as np, time, random
    spike_timer = 0
    spike_interval = random.randint(10, 20)  # Change here if needed

    while True:
        x = np.random.normal(0.1, 0.05)
        y = np.random.normal(-0.2, 0.05)
        z = np.random.normal(0.3, 0.05)

        if spike_timer >= spike_interval:
            x = np.random.uniform(3.5, 4.5)
            y = np.random.uniform(3.5, 4.5)
            z = np.random.uniform(3.5, 4.5)
            spike_timer = 0
            spike_interval = random.randint(10, 20)

        yield [x, y, z]
        time.sleep(0.5)
        spike_timer += 0.5
