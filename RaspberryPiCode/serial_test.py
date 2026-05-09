import serial
import time

ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
time.sleep(2)

print("Listening to Arduino...\n")

while True:
    if ser.in_waiting > 0:
        data = ser.readline().decode('utf-8', errors='replace').strip()

        print("RAW:", data)

        if data.startswith("M:"):
            print(" MODE =", data[2:])

        elif data.startswith("S:"):
            print(" SKILL =", data[2:])

        elif data.startswith("T:"):
            print(" TIME =", data[2:])

        elif data.startswith("P:"):
            print(" MOVE =", data[2:])

        else:
            print(" UNKNOWN:", data)
