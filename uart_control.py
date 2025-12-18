import serial
import struct
import subprocess

# Configuration
SERIAL_PORT = '/dev/ttyAMA0'
BAUD_RATE = 115200
record_cmd = 'arecord -D plughw:CARD=sndrpihifiberry,DEV=0 -r 192000 -c 2 -f S32_LE -d 60'

class UART_control:
    def __init__(self):
        self.initial_process = None
        self.record_process = None
        self.last_ts = None
        self.record_thread = None
        self.audio_file_name = None
        self.log_file_name = None
        self.count = 0

    def main(self):
        ser = serial.Serial(port=SERIAL_PORT, baudrate=BAUD_RATE)
        while True:
            b = ser.read(1)
            if not b:
                continue
            if b != b'|':
                continue
            nid = ser.read(1)
            data = ser.read(4)
            if len(nid) != 1 or len(data) != 4:
                continue
            node_id = nid[0]
            utc_ms = struct.unpack("<I", data)[0]
            self.record(node_id, utc_ms)
            
    def test_main(self):
        while True:
            b = input('input cmd:')
            if b == 's':
                node = input('input node id:')
                ms = input('input ms:')
                self.record(node, ms)
    
    def log(self, node, ms):
        with open(self.log_file_name, 'a') as f:
            self.count += 1
            f.write(str(self.count) + ' ' + str(node) + '-' + str(ms) + '\n')

    def record(self, node, ms):
        if self.record_thread is not None and self.record_thread.poll() is None:
            self.log(node, ms)
        else:
            cmd = record_cmd + ' ' + str(node) + '-' + str(ms) + '.wav'
            print('start' + cmd)
            self.record_thread = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
            self.log_file_name = str(node) + '-' + str(ms) + '.txt'
            self.count = 0
if __name__ == '__main__':
    uart_control = UART_control()
    uart_control.main()
