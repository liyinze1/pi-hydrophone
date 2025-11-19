import subprocess
import numpy as np
import matplotlib.pyplot as plt
from collections import deque

RATE = 44100
CHANNELS = 2
FORMAT = 'S16_LE'
CHUNK = 4096  # frames per read
WINDOW_SEC = 1
WINDOW_SIZE = RATE * WINDOW_SEC

# Rolling buffers for left & right channels
buf_left = deque(maxlen=WINDOW_SIZE)
buf_right = deque(maxlen=WINDOW_SIZE)

# Start arecord for stereo
process = subprocess.Popen(
    [
        'arecord',
        '-f', FORMAT,
        '-r', str(RATE),
        '-c', str(CHANNELS),
        '-q',
        '-'
    ],
    stdout=subprocess.PIPE,
    stderr=subprocess.DEVNULL
)

plt.ion()
fig, axs = plt.subplots(2, 2, figsize=(10, 6))
(ax_wl, ax_wr), (ax_fl, ax_fr) = axs

while True:
    # Read raw bytes: CHUNK frames × CHANNELS × 2 bytes
    raw = process.stdout.read(CHUNK * CHANNELS * 2)
    if not raw:
        break

    # Raw PCM → numpy
    data = np.frombuffer(raw, dtype=np.int16).reshape(-1, CHANNELS)
    left = data[:, 0]
    right = data[:, 1]

    # Update rolling buffers
    buf_left.extend(left)
    buf_right.extend(right)

    # Convert rolling buffer → numpy arrays
    left_1s = np.array(buf_left)
    right_1s = np.array(buf_right)

    # Skip until buffer has 1 second
    if len(left_1s) < WINDOW_SIZE:
        continue

    # ------- Waveforms -------
    ax_wl.clear()
    ax_wl.set_title('Left Waveform (last 1 sec)')
    ax_wl.plot(left_1s)

    ax_wr.clear()
    ax_wr.set_title('Right Waveform (last 1 sec)')
    ax_wr.plot(right_1s)

    # ------- FFTs -------
    fft_left = np.fft.rfft(left_1s)
    fft_right = np.fft.rfft(right_1s)
    freqs = np.fft.rfftfreq(len(left_1s), 1 / RATE)

    ax_fl.clear()
    ax_fl.set_title('Left FFT (last 1 sec)')
    ax_fl.plot(freqs, np.abs(fft_left))

    ax_fr.clear()
    ax_fr.set_title('Right FFT (last 1 sec)')
    ax_fr.plot(freqs, np.abs(fft_right))

    plt.tight_layout()
    plt.pause(0.001)
