import subprocess
import numpy as np
import matplotlib.pyplot as plt

RATE = 16000
CHANNELS = 2
FORMAT = 'S16_LE'
CHUNK = RATE // 2  # read 0.1 second per read
WINDOW_SEC = 2
WINDOW_SIZE = RATE * WINDOW_SEC

# Rolling buffers (no deque)
buf_left = np.zeros(WINDOW_SIZE, dtype=np.float32)
buf_right = np.zeros(WINDOW_SIZE, dtype=np.float32)

# Launch arecord in stereo
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
fig, axs = plt.subplots(2, 2, figsize=(15, 8))
(ax_wl, ax_wr), (ax_fl, ax_fr) = axs

while True:
    print("Reading audio data...")
    raw = process.stdout.read(CHUNK * CHANNELS * 2)
    if not raw:
        break

    print("Processing audio data...")
    data = np.frombuffer(raw, dtype=np.int16).reshape(-1, CHANNELS).astype(np.float32)
    left = data[:, 0]
    right = data[:, 1]

    L = len(left)

    print("Rolling window...")
    # === Update rolling 1-second buffer ===
    buf_left = np.roll(buf_left, -L)
    buf_right = np.roll(buf_right, -L)

    buf_left[-L:] = left
    buf_right[-L:] = right
    # =====================================

    # Skip drawing until we have 1 second filled
    # if np.any(buf_left == 0):
    #     continue

    print("Updating plots...")
    # --- Waveforms ---
    ax_wl.clear()
    ax_wl.plot(buf_left)
    ax_wl.set_title('Left Waveform (last 1 sec)')
    ax_wl.set_ylim(-1000, 1000)


    ax_wr.clear()
    ax_wr.plot(buf_right)
    ax_wr.set_title('Right Waveform (last 1 sec)')

    # --- FFTs ---
    freqs = np.fft.rfftfreq(WINDOW_SIZE, 1 / RATE)
    fft_left = np.fft.rfft(buf_left)
    fft_right = np.fft.rfft(buf_right)

    ax_fl.clear()
    ax_fl.plot(freqs, np.abs(fft_left))
    ax_fl.set_title('Left FFT (last 1 sec)')
    ax_fl.set_ylim(0, 100000)

    ax_fr.clear()
    ax_fr.plot(freqs, np.abs(fft_right))
    ax_fr.set_title('Right FFT (last 1 sec)')

    # plt.tight_layout()
    plt.pause(0.1)
