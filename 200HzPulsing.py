"""this code is able to pulse LED using a single core at 200.5Hz as expected"""

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
red_buffer = [0] * WINDOW_SIZE
ir_buffer = [0] * WINDOW_SIZE #for blood oxygen levels



#for debugging purposes
led_toggle_time = [0] * WINDOW_SIZE
read_time = [0] * WINDOW_SIZE
append_time_red = [0] * WINDOW_SIZE
led_toggle_time_2 = [0] * WINDOW_SIZE
read_time_2 = [0] * WINDOW_SIZE
append_time_ir = [0] * WINDOW_SIZE 
#i = 0
print("pulsing the leds now")
def LED_switch(Window_Size):
    i = 0
    while i < Window_Size:
        #start_time = utime.ticks_us()
    
        pin1.high()
        pin2.low()
        #led_toggle_time[i] = utime.ticks_diff(utime.ticks_us(), start_time)
        
        utime.sleep_us(500) #sleep for half a pulse
        #start_time = utime.ticks_us()
        #value = mcp3008.read(0)
        #read_time[i] = utime.ticks_diff(utime.ticks_us(), start_time)
    
        #start_time = utime.ticks_us()
        red_buffer[i] = mcp3008.read(0)
        #append_time_red[i] = utime.ticks_diff(utime.ticks_us(), start_time)
        utime.sleep_us(1631)
    
        #start_time = utime.ticks_us()
        pin1.low()
        pin2.high()
        #led_toggle_time_2[i] = utime.ticks_diff(utime.ticks_us(), start_time)
        
        utime.sleep_us(500) #sleep for half a pulse
        #start_time = utime.ticks_us()
        #value2 = mcp3008.read(0)
        #read_time_2[i] = utime.ticks_diff(utime.ticks_us(), start_time)
    
        #start_time = utime.ticks_us()
        ir_buffer[i] = mcp3008.read(0)
        #append_time_ir[i] = utime.ticks_diff(utime.ticks_us(), start_time)
        utime.sleep_us(1631)
    
        i += 1
while True:
    LED_switch(WINDOW_SIZE)
    
    
    #for numbers in red_buffer:
    #    print(numbers)
    break
