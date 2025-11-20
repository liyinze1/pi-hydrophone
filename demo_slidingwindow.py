import subprocess
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

RATE = 16000
CHANNELS = 2
FORMAT = 'S16_LE'
CHUNK = RATE // 5
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

# ----- GRID: First row has 2 columns, second row only one full-width plot -----
fig = plt.figure(figsize=(15, 8))
gs = gridspec.GridSpec(2, 2, height_ratios=[1, 1])

ax_wl = fig.add_subplot(gs[0, 0])       # row 0, col 0
ax_wr = fig.add_subplot(gs[0, 1])       # row 0, col 1
ax_fft = fig.add_subplot(gs[1, :])      # row 1, spanning both columns
# -----------------------------------------------------------------------------

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

    # --- Waveforms (top row) ---
    ax_wl.clear()
    ax_wl.plot(buf_left)
    ax_wl.set_title(f'Hydrophone Waveform (last {WINDOW_SEC} sec)')
    ax_wl.set_ylim(-2000, 2000)

    ax_wr.clear()
    ax_wr.plot(buf_right, color='orange')
    ax_wr.set_title(f'Pulse (last {WINDOW_SEC} sec)')
    ax_wr.set_ylim(-200, 200)

    # --- FFT spanning entire bottom row ---
    freqs = np.fft.rfftfreq(WINDOW_SIZE, 1 / RATE)
    fft_left = np.fft.rfft(buf_left)

    ax_fft.clear()
    ax_fft.plot(freqs, np.abs(fft_left))
    ax_fft.set_title(f'Hydrophone FFT (last {WINDOW_SEC} sec)')
    ax_fft.set_ylim(0, 100000)

    plt.pause(0.05)
