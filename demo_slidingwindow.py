import subprocess
import numpy as np
import matplotlib.pyplot as plt

RATE = 16000
CHANNELS = 2
FORMAT = 'S16_LE'
CHUNK = RATE // 2  # read 0.5 second per read
WINDOW_SEC = 2
WINDOW_SIZE = RATE * WINDOW_SEC

# Rolling buffers
buf_left = np.zeros(WINDOW_SIZE, dtype=np.float32)
buf_right = np.zeros(WINDOW_SIZE, dtype=np.float32)

# Launch arecord
process = subprocess.Popen(
    ['arecord', '-f', FORMAT, '-r', str(RATE), '-c', str(CHANNELS), '-q', '-'],
    stdout=subprocess.PIPE,
    stderr=subprocess.DEVNULL
)

plt.ion()
# 2 rows × 2 columns, but bottom-right panel unused
fig, axs = plt.subplots(2, 2, figsize=(15, 8))
(ax_wl, ax_wr), (ax_fl, ax_unused) = axs  # ax_unused will not be used

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
    buf_left = np.roll(buf_left, -L)
    buf_right = np.roll(buf_right, -L)

    buf_left[-L:] = left
    buf_right[-L:] = right

    print("Updating plots...")

    # --- Waveforms ---
    ax_wl.clear()
    ax_wl.plot(buf_left)
    ax_wl.set_title(f'Left Waveform (last {WINDOW_SEC} sec)')
    ax_wl.set_ylim(-1000, 1000)

    ax_wr.clear()
    ax_wr.plot(buf_right, color='orange')
    ax_wr.set_title(f'Right Waveform (last {WINDOW_SEC} sec)')
    ax_wr.set_ylim(-1000, 1000)

    # --- Left FFT Only ---
    freqs = np.fft.rfftfreq(WINDOW_SIZE, 1 / RATE)
    fft_left = np.fft.rfft(buf_left)

    ax_fl.clear()
    ax_fl.plot(freqs, np.abs(fft_left))
    ax_fl.set_title(f'Left FFT (last {WINDOW_SEC} sec)')
    ax_fl.set_ylim(0, 100000)

    # clear and hide the unused subplot
    ax_unused.clear()
    ax_unused.axis('off')

    plt.pause(0.1)
