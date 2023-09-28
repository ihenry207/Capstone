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
#end of spi connection

#start of I2C configuration for the oled
WIDTH = 128
HEIGHT = 64
i2c = I2C(0, scl = Pin(17), sda = Pin(16), freq = 200000)
oled = SSD1306_I2C(WIDTH, HEIGHT, i2c)
led = Pin('LED', Pin.OUT)

# Buffers and variable
red_buffer = []
ir_buffer = []
WINDOW_SIZE = 2800 #needs to be big enough to accurately calculate heart rate


#function for switching the LED
def LED_switch(Window_Size): #I might wanna assume the first few samples are scratch and remove them
    #here I want to gather flash the LED and get samples at the same time
    #this is crucial in calculating the heart rate and blood oxygen levels
    #assume both LED are off
    IrLED.low()
    redLED.low()
    i = 0
    while j < WINDOW_SIZE: 
        redLED.high()
        IrLED.low()
        time.sleep(0.01)#sleep
        #value = mcp3008.read(0)
        red_buffer.append(mcp3008.read(0))#append new sample read throught the spi adc
        redLED.low()
        IrLED.high()
        time.sleep(0.01)#sleep
        ir_buffer.append(mcp3008.read(0))
        #increase i
        j += 1


#function for detecting heart rate
def detect_peak(heart_rate_buffer):
    # Peak detection for heart rate
        peaks = []
        for i in range(1, len(heart_rate_buffer) - 1):
            if heart_rate_buffer[i] > heart_rate_buffer[i - 1] and heart_rate_buffer[i] > heart_rate_buffer[i + 1]:
                peaks.append(i)
        
        if len(peaks) >= 2:
            # Compute intervals between all consecutive peaks
            #intervals helps to filter out the noise too
            intervals = [peaks[i+1] - peaks[i] for i in range(len(peaks)-1)]
        
            # Calculate the average of these intervals
            avg_interval = sum(intervals) / len(intervals)
        
            # Compute heart rate based on the average interval
            heart_rate_bpm = int(60 / (avg_interval / sample_rate))
            return heart_rate_bpm
        else:
            return None
#here will go function for detecting SpO2 levels
def detect_SpO2(red_buffer, ir_buffer):
    AC_red = max(red_buffer) - min(red_buffer)
    DC_red = sum(red_buffer) // len(red_buffer)
    
    AC_ir = max(ir_buffer) - min(ir_buffer)
    DC_ir = sum(ir_buffer) // len(ir_buffer)

    R_red = AC_red / DC_red
    R_ir = AC_ir / DC_ir

    R = R_red / R_ir

    # The empirical relation between SpO2 and R would go here. 
    # For this example, I'm just returning R. In a real-world application, 
    # you'd replace this with a calibration equation or lookup table.
    #SpO2 = (10.0002*R^3 )-(52.887*R^2 )+(26.871*R)+98.283 #formula
    return R

#and then we go into the main while loop
while True:
    LED_switch(WINDOW_SIZE)#send in the window size
    #after window size is done it will get out of the while loop
    #now we go to calculate the heart rate
    heart_rate = detect_peak(red_buffer)
    if heart_rate is not None:
        print("Heart Rate: ", heart_rate)
    else:
        print("Heart Rate: Not detected")
    #now we got to calculate the SpO2 levels
    print("SpO2 Ratio:", detect_SpO2(red_buffer, ir_buffer))
    
    #now clear the buffers
    red_buffer = []
    ir_buffer = []