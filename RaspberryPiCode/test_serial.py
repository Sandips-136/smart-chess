import serial
import time

PORT = "/dev/ttyUSB0"   # change if needed
BAUD = 9600

ser = serial.Serial(PORT, BAUD, timeout=1)
time.sleep(2)

print("Listening...\n")

while True:
    line = ser.readline().decode("utf-8", errors="replace").strip()
    if line:
        print("RAW:", line)
