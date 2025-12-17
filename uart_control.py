import os
import signal
import serial
import subprocess
import time

# Configuration
SERIAL_PORT = '/dev/ttyACM0'
BAUD_RATE = 230400
OUTPUT_DIR = os.path.expanduser('~/recordings')
os.makedirs(OUTPUT_DIR, exist_ok=True)

initial_cmd = 'ros2 run audio_common audio_capturer_node --ros-args -p device:=0 -p rate:=192000 -p channels:=2 -p format:=1'
record_cmd = 'ros2 bag record --topics /audio'


class UART_control:
    def __init__(self):
        self.ser = serial.Serial(port=SERIAL_PORT, baudrate=BAUD_RATE, timeout=1)
        self.initial_process = None
        self.record_process = None
        self.last_ts = None

        os.makedirs(OUTPUT_DIR, exist_ok=True)

    def main(self):
        while True:
            c = self.ser.read(1)
            if not c:
                continue

            if c == b'i':
                self.initial()
            elif c == b's':
                ts = self.ser.read(4).decode('ascii', errors='ignore')
                self.last_ts = ts
                self.start(ts)
            elif c == b'e':
                self.end()
                
    def test_main(self):
        while True:
            c = input('input i, s, or e')
            if not c:
                continue

            if c == 'i':
                self.initial()
            elif c == 's':
                ts = input('input timestamp')
                self.last_ts = ts
                self.start(ts)
            elif c == 'e':
                self.end()

    def _is_running(self, proc):
        return proc is not None and proc.poll() is None

    def _start_process(self, cmd, cwd=None):
        # Start in its own process group so we can signal the whole tree
        return subprocess.Popen(
            cmd,
            shell=True,
            cwd=cwd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
            preexec_fn=os.setsid
        )

    def _stop_process(self, proc, name='process', sigint_wait_s=2.0):
        if not self._is_running(proc):
            return

        try:
            pgid = os.getpgid(proc.pid)

            # Try graceful stop first (ROS nodes usually stop on SIGINT)
            os.killpg(pgid, signal.SIGINT)

            deadline = time.time() + sigint_wait_s
            while time.time() < deadline:
                if proc.poll() is not None:
                    return
                time.sleep(0.05)

            # Force kill if still alive
            os.killpg(pgid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        except Exception as e:
            print(f'Failed to stop {name}: {e}')

    def initial(self):
        if self._is_running(self.initial_process):
            print('initial already running')
            return

        print('starting initial...')
        self.initial_process = self._start_process(initial_cmd)

    def start(self, ts=None):
        if self._is_running(self.record_process):
            print('record already running')
            return

        # Optional: create a unique bag name using the 4-byte ts
        bag_name = f'bag_{ts}' if ts else 'bag'
        bag_path = os.path.join(OUTPUT_DIR, bag_name)

        # ros2 bag record can take an output prefix: -o <name>
        cmd = f'{record_cmd} -o {bag_path}'
        print(f'starting record: {bag_path}')
        self.record_process = self._start_process(cmd, cwd=OUTPUT_DIR)

    def end(self):
        print('stopping record + initial...')
        # Stop record first so capturer can still exist during shutdown if needed
        self._stop_process(self.record_process, name='record')
        self.record_process = None

        self._stop_process(self.initial_process, name='initial')
        self.initial_process = None


if __name__ == '__main__':
    uart_control =  UART_control()
    uart_control.main()
