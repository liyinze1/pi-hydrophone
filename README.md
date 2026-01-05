# pi-hydrophone

### Hat configuration
https://www.hifiberry.com/docs/data-sheets/datasheet-dac-adc-pro/

### uart_control.py

This is the script to interact with Ambiq Apollo3. It will keep listening the UART. Once it receive the message from Ambiq Apollo3, the script will start recording audio, and save timestamp of each pulse to a txt file. 

The message format from Ambiq Apollo3 is: `'s' + node_id (1 byte) + timestamp (ms) (4 bytes)`.

### demo_slidingwindow.py

This script is to show the live FFT and waveform of the microphone input. 