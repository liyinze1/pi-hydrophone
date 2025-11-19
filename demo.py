import subprocess
import numpy as np
import matplotlib.pyplot as plt
from collections import deque

RATE = 44100
CHANNELS = 2
FORMAT = 'S16_LE'
CHUNK = 4096
WINDOW_SEC = 1
WINDOW_SIZE = RATE * WINDOW_SEC

TARGET_RMS = 0.1  # normalized target loudness (0–1 range)

buf_left = deque(maxlen=WINDOW_SIZE)
buf_right = deque(maxlen=WINDOW_SIZE)

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

def rms_normalize(signal, target_rms):
    """Normalize signal RMS loudness."""
    signal = signal.astype(np.float32)
    rms = np.sqrt(np.mean(signal ** 2)) + 1e-8
    gain = target_rms / rms
    return signal * gain

while True:
    raw = process.stdout.read(CHUNK * CHANNELS * 2)
    if not raw:
        break

    data = np.frombuffer(raw, dtype=np.int16).reshape(-1, CHANNELS)
    left = data[:, 0]
    right = data[:, 1]

    buf_left.extend(left)
    buf_right.extend(right)

    if len(buf_left) < WINDOW_SIZE:
        continue

    left_1s = np.array(buf_left, dtype=np.float32)
    right_1s = np.array(buf_right, dtype=np.float32)

    # --- Loudness Normalize ---
    # left_norm = rms_normalize(left_1s, TARGET_RMS)
    # right_norm = rms_normalize(right_1s, TARGET_RMS)

    # Clip back to safe range for plotting
    left_norm = np.clip(left_norm, -1.0, 1.0)
    right_norm = np.clip(right_norm, -1.0, 1.0)

    # --- Waveforms ---
    ax_wl.clear()
    ax_wl.set_title('Left Waveform (normalized, last 1 sec)')
    ax_wl.plot(left_norm)

    ax_wr.clear()
    ax_wr.set_title('Right Waveform (normalized, last 1 sec)')
    ax_wr.plot(right_norm)

    # --- FFTs ---
    fft_left = np.fft.rfft(left_norm)
    fft_right = np.fft.rfft(right_norm)
    freqs = np.fft.rfftfreq(len(left_norm), 1 / RATE)

    ax_fl.clear()
    ax_fl.set_title('Left FFT (normalized)')
    ax_fl.plot(freqs, np.abs(fft_left))

    ax_fr.clear()
    ax_fr.set_title('Right FFT (normalized)')
    ax_fr.plot(freqs, np.abs(fft_right))

    plt.tight_layout()
    plt.pause(0.001)
