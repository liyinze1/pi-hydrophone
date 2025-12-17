import os
import serial
import struct

# Configuration
SERIAL_PORT = '/dev/ttyACM0'
BAUD_RATE = 230400
record_cmd = 'arecord -f S32_LE -r 192000 -c 2 -d 20'

class UART_control:
    def __init__(self):
        self.initial_process = None
        self.record_process = None
        self.last_ts = None

    def main(self):
        ser = serial.Serial(port=SERIAL_PORT, baudrate=BAUD_RATE)
        while True:
            b = ser.read(1)
            if not b:
                continue
            if b != b's':
                continue
            nid = ser.read(1)
            data = ser.read(4)
            if len(nid) != 1 or len(data) != 4:
                continue
            node_id = nid[0]
            utc_ms = struct.unpack("<I", data)[0]
            self.record(node_id, utc_ms)
    
    def record(self, node, ms):
        cmd = record_cmd + ' ' + str(node) + '-' + str(ms) + '.wav'
        os.system(cmd)
        print('finish')

if __name__ == '__main__':
    uart_control = UART_control()
    uart_control.main()
