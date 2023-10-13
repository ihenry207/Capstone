import machine
from machine import Pin, SPI, I2C
from ssd1306 import SSD1306_I2C
from mcp3008 import MCP3008
import utime
import time

# Set up GPIO 14 and 15 as outputs for LED flashing
redLED = machine.Pin(14, machine.Pin.OUT)
IrLED = machine.Pin(15, machine.Pin.OUT)

spi = SPI(0, sck=Pin(2), mosi=Pin(3), miso=Pin(4), baudrate=100000)
cs = Pin(22, Pin.OUT)#can be any GPIO pins on the board
cs.value(1)  # disable chip at start
mcp3008 = MCP3008(spi, cs)

led = Pin('LED', Pin.OUT)

# Buffers and variable
red_buffer = []
ir_buffer = [] #for blood oxygen levels

WINDOW_SIZE = 2800 #needs to be big enough to accurately calculate heart rate

#function to pulse the leds
def LED_switch(Window_Size):
    IrLED.low()
    redLED.low()
    print("pulsing the leds now")
    
    pulse_duration = 0.0025  # 2.5ms for 200Hz
    half_pulse_duration = pulse_duration / 2
    for i in range(0, Window_Size-1):
        redLED.high()
        IrLED.low()
        utime.sleep(half_pulse_duration)#trying to get the high
        value = mcp3008.read(0)#trying to capture it's effect right after
        red_buffer.append(value)
        utime.sleep(pulse_duration)  # sleep for 2.5ms
        
        redLED.low()
        IrLED.high()
        utime.sleep(half_pulse_duration)
        value2 = mcp3008.read(0)#trying to capture its effect right after
        ir_buffer.append(value2)
        utime.sleep(pulse_duration)  # sleep for 2.5ms
        
while True:
    LED_switch(Window_Size)
    for number in red_buffer:#print numbers inside the red_buffer for checking
        print(number)
    red_buffer = []
    ir_buffer = []
    utime.sleep(0.5) #give it time to rest/breathe