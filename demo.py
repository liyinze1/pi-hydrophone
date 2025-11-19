import subprocess
import numpy as np
import matplotlib.pyplot as plt

RATE = 44100
CHANNELS = 2
FORMAT = 'S16_LE'
CHUNK = RATE   # read exactly 1 second per read

process = subprocess.Popen(
    ['arecord', '-f', FORMAT, '-r', str(RATE), '-c', str(CHANNELS), '-q', '-'],
    stdout=subprocess.PIPE,
    stderr=subprocess.DEVNULL
)

plt.ion()
fig, axs = plt.subplots(2,2, figsize=(20, 12))
(ax_wl, ax_wr), (ax_fl, ax_fr) = axs

ax_wl.set_ylim(-1000, 1000)

while True:
    
    print("Reading audio data...")
    raw = process.stdout.read(CHUNK * CHANNELS * 2)
    if not raw:
        break
    
    print("Processing audio data...")
    data = np.frombuffer(raw, dtype=np.int16).reshape(-1, CHANNELS)
    left = data[:, 0]
    right = data[:, 1]
    
    print("Updating plots...")
    # --- Waveforms ---
    ax_wl.clear()
    ax_wl.plot(left)
    ax_wl.set_title('Left Waveform (1 sec)')

    ax_wr.clear()
    ax_wr.plot(right, color='orange')
    ax_wr.set_title('Right Waveform (1 sec)')

    # --- FFTs ---
    freqs = np.fft.rfftfreq(len(left), 1/RATE)
    ax_fl.clear()
    ax_fl.plot(freqs, np.abs(np.fft.rfft(left)))
    ax_fl.set_title('Left FFT')

    ax_fr.clear()
    ax_fr.plot(freqs, np.abs(np.fft.rfft(right)), color='orange')
    ax_fr.set_title('Right FFT')

    plt.pause(0.1)
