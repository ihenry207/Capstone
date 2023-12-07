import machine
import time

# Set up GPIO 14 and 15 as outputs
pin14 = machine.Pin(14, machine.Pin.OUT)
pin15 = machine.Pin(15, machine.Pin.OUT)

# Initial states: GPIO14 is high, GPIO15 is low
pin14.high()
pin15.low()

try:
    while True:
        # Toggle the states of the pins
        pin14.toggle()
        pin15.toggle()
        time.sleep(0.001)  # 10ms delay for 50Hz frequency

except KeyboardInterrupt:
    # Reset the pins to low before exiting
    pin14.low()
    pin15.low()
