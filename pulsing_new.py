import machine
import time
from machine import Pin, SPI, I2C
from ssd1306 import SSD1306_I2C
from mcp3008 import MCP3008
import utime

spi = SPI(0, sck=Pin(2), mosi=Pin(3), miso=Pin(4), baudrate=100000)
cs = Pin(22, Pin.OUT)#can be any GPIO pins on the board
cs.value(1)  # disable chip at start
mcp3008 = MCP3008(spi, cs)
# Define pins
pin1 = machine.Pin(14, machine.Pin.OUT)
pin2 = machine.Pin(15, machine.Pin.OUT)

WINDOW_SIZE = 2000 #needs to be big enough to accurately calculate heart rate
# Buffers and variable
red_buffer = [] 
ir_buffer = []  #for blood oxygen levels
def LED_switch():
    
    print("pulsing the leds now")
    # Record the start time
    start_time = utime.ticks_ms()
    elapsed_time = 0  # Initialize elapsed time

    # Continue the loop until 5 seconds (5000 milliseconds) have passed
    while elapsed_time < 7000:
        pin1.high()
        pin2.low()

        # Calculate the elapsed time
        elapsed_time = utime.ticks_diff(utime.ticks_ms(), start_time)

        # Check if 2 seconds have passed
        if elapsed_time >= 2000:
            # Now, we record the values as 2 seconds have passed
            for _ in range(2):  # read 2 times per cycle, as per your original code
                utime.sleep_us(300)  # wait for signal to get high
                red_buffer.append(mcp3008.read(0))  # Read from channel 0 of the MCP3008

        utime.sleep_us(700)
        pin1.low()
        utime.sleep_us(4500)  # This combined with the above sleep gives a total cycle time of about 5 ms


while True:
    LED_switch()
    
    break