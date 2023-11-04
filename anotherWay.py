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
    while i < Window_Size+400:
        #charging the capacitors
        if i < 400:#might need to change this to make it wait less
            # Turn on the LEDs for 5 ms
            pin1.high()
            pin2.low()
            utime.sleep_us(5000)  # This function is more appropriate for small delays

            # Turn off the LEDs for the remaining 5 ms
            pin1.low()
            pin2.high()
            utime.sleep_us(5000)

            # Move to the next cycle
            i += 1
        
        # Perform the readings
        else: #since we are reading 2 times a cycle don't record the first 600 samples
            pin1.high()
            pin2.low()
            for _ in range(1):#3 reading per cycle
                if i >= (Window_Size+400):
                    break  # Prevent writing beyond the buffer size

                utime.sleep_us(500) #wait for signal to get high
                red_buffer[i-400] = mcp3008.read(0) #read from the sensor
                i += 1  # Move to the next buffer position
            utime.sleep_us(2520)#100Hz 3262- (520+320+520+320+20(if stats)) = 1582 = 1600
     
            pin1.low()
            pin2.high()
        
            #utime.sleep_us(500) #sleep for half a pulse
            #ir_buffer[i] = mcp3008.read(0)
            utime.sleep_us(4900) #plus 3262+ 500 +320 for the reading adc
    
     
    print("red_buffer_values = [" + ", ".join(map(str, red_buffer)) + "];")#for matlab plottign


# a more efficient way to calculate moving average filter
def efficient_moving_average(data, window):
    if window_size < 1:
        raise ValueError("Window size must be at least 1.")

    if window_size > len(data):
        raise ValueError("Window size is larger than input data size.")

    moving_averages = []
    cum_sum = 0

    for i in range(len(data)):
        cum_sum += data[i]
        
        if i >= window_size:
            # Subtract the sample that's falling out of the window
            cum_sum -= data[i - window_size]
        
        if i >= window_size - 1:
            # Now we have enough points to fill the window
            moving_averages.append(cum_sum / window_size)

    return moving_averages


def find_peaks(data):
    """Basic peak detection algorithm."""
    peaks = []
    threshold = max(data) / 2  # for simplicity, might need adjustment based on your signal characteristics
    for i in range(1, len(data)-1):
        # Basic peak detection: previous point is lower, next point is lower
        if data[i-1] < data[i] > data[i+1] and data[i] > threshold:
            peaks.append(i) #we've found a peak
    return peaks

def calculate_diff(values):
    return [values[i+1] - values[i] for i in range(len(values)-1)]

def calculate_mean(values):
    return sum(values) / len(values) if values else 0  # Prevent division by zero

def calculate_heart_rate(peaks, sample_rate):
    """Calculate heart rate from peak positions and sample rate."""
    # Time between peaks
    peak_intervals = calculate_diff(peaks)  # in number of samples

    # Convert to time intervals using the sample rate
    time_intervals = peak_intervals / sample_rate  # in seconds

    # Calculate heart rate: the average number of beats per minute (BPM)
    if len(time_intervals) == 0:
        return 0  # Prevent division by zero; handle error as appropriate for your application
    average_time_interval = calculate_mean(time_intervals)  # in seconds
    heart_rate = 60 / average_time_interval  # in BPM

    return heart_rate

while True:
    LED_switch(WINDOW_SIZE)
    red_buffer = []
    gc.collect()#to reclaim some memory
    break #first need to test the output of red_buffer
    # Assuming the data collection is at 100 Hz
    sample_rate = 600.0  # Hz#i'm sampling at 3 times every high so about 300 i think

    # Step 1: Smooth the signal
    smoothed = simple_moving_average(red_buffer, window=5)
    
    gc.collect()#to reclaim some memory
    
    # Step 2: Find peaks
    peaks = find_peaks(smoothed)

    # Step 3: Calculate heart rate
    heart_rate = calculate_heart_rate(peaks, sample_rate)

    print("Estimated Heart Rate: {:.2f} BPM".format(heart_rate))
    red_buffer = []#clear the buffers
    
    gc.collect()#reclaim some memory
    #Ir_buffer = []
    #break #I'll remove if it's giving right results
