"""this code is able to pulse LED using a single core at 100Hz as expected"""

import machine
import time
from machine import Pin, SPI, I2C
from ssd1306 import SSD1306_I2C
from mcp3008 import MCP3008
import utime
import math
import gc
 

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
#ir_buffer = [0] * WINDOW_SIZE #for blood oxygen levels

#reading 3 values when red is on
def LED_switch(Window_Size):
    print("pulsing the leds now")
    i = 0
    while i < Window_Size:
        pin1.high()
        pin2.low()
        
        # Perform the readings
        
        for _ in range(1):#3 reading per cycle
            if i >= Window_Size:
                break  # Prevent writing beyond the buffer size

            utime.sleep_us(500) #wait for signal to get high
            red_buffer[i] = mcp3008.read(0) #read from the sensor
            i += 1  # Move to the next buffer position
        utime.sleep_us(1620)#100Hz 3262- (520+320+520+320+20(if stats)) = 1582 = 1600
     
        pin1.low()
        pin2.high()
        
        #utime.sleep_us(500) #sleep for half a pulse
        #ir_buffer[i] = mcp3008.read(0)
        utime.sleep_us(4082) #plus 3262+ 500 +320 for the reading adc
    
        #i += 1
    # Number of readings to discard
    readings_to_discard = 600#since we are reading 3 times when it's high
    valid_red_buffer = red_buffer[readings_to_discard:]
    gc.collect() #trigger garbage collection
    print("red_buffer_values = [" + ", ".join(map(str, valid_red_buffer)) + "];")#for matlab plottign

    
while True:
    LED_switch(WINDOW_SIZE)
    red_buffer = []#clear the buffers
    Ir_buffer = []
    break 