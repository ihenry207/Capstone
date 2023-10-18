"""this code is able to pulse LED using a single core at 200.5Hz as expected"""

import machine
import time
from machine import Pin, SPI, I2C
from ssd1306 import SSD1306_I2C
from mcp3008 import MCP3008
import utime
import math

spi = SPI(0, sck=Pin(2), mosi=Pin(3), miso=Pin(4), baudrate=100000)
cs = Pin(22, Pin.OUT)#can be any GPIO pins on the board
cs.value(1)  # disable chip at start
mcp3008 = MCP3008(spi, cs)
# Define pins
pin1 = machine.Pin(14, machine.Pin.OUT)
pin2 = machine.Pin(15, machine.Pin.OUT)

WINDOW_SIZE = 2000 #needs to be big enough to accurately calculate heart rate
# Buffers and variable
red_buffer = [0] * WINDOW_SIZE
ir_buffer = [0] * WINDOW_SIZE #for blood oxygen levels


def LED_switch(Window_Size):
    print("pulsing the leds now")
    i = 0
    while i < Window_Size:
        pin1.high()
        pin2.low()

        utime.sleep_us(500) #wait for signal to get high
        red_buffer[i] = mcp3008.read(0)
        utime.sleep_us(1631)
     
        pin1.low()
        pin2.high()
        
        utime.sleep_us(500) #sleep for half a pulse
        ir_buffer[i] = mcp3008.read(0)
        utime.sleep_us(1631)
    
        i += 1
    print("red_buffer_values = [" + ", ".join(map(str, red_buffer)) + "];")

    
while True:
    LED_switch(WINDOW_SIZE)
    red_buffer = []#clear the buffers
    Ir_buffer = []
    break 
