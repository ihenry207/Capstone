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

WINDOW_SIZE = 2000 #needs to be big enough to accurately calculate heart rate

#function to pulse the leds
def LED_switch(Window_Size):
    IrLED.low()
    redLED.low()
    print("pulsing the leds now")
    
    pulse_duration = 0.0025  # 2.5ms for 200Hz
    for i in range(0, Window_Size-1):
        redLED.high()
        IrLED.low()
        value = mcp3008.read(0)#trying to capture it's effect right after
        red_buffer.append(value)
        utime.sleep(pulse_duration)  # sleep for 2.5ms
        
        redLED.low()
        IrLED.high()
        value2 = mcp3008.read(0)#trying to capture its effect right after
        ir_buffer.append(value2)
        utime.sleep(pulse_duration)  # sleep for 2.5ms
    #I want to print the values inside red_buffer to check if I'm getting the right nbrs
    #print("I'm going to now print the number in red_buffer")
    #for x in red_buffer:
        #print(x)
#might introduce a phase lag
def simple_moving_average(data, window_size): #lowpass filter
    """Compute the simple moving average."""
    #this code gives me memory allocation failure
    #it's 2000 for this algorithm
    return [sum(data[i:i+window_size]) / window_size for i in range(len(data) - window_size + 1)]
    
    
    #so let's optimize it
    #not sure if this works or not yet
    #it's 2500 maximum for this algorithm
    #result = []
    #running_total = sum(data[:window_size])
    #result.append(running_total / window_size)
    
    #for i in range(1, len(data) - window_size + 1):
    #    running_total = running_total - data[i - 1] + data[i + window_size - 1]
    #    result.append(running_total / window_size)
    #return result

#peak detection algorithm
#this peak detection algorithm is flawed.
#I think we need to have a threshold and when a number crosses that threshold it is regarded as a peak
def detect_peaks(data):
    """Detect peaks in the data and return their indices."""
    #we gonna use these indices to calculate the average distance between them
    peak_indices = []
    threshold = 2  # Adjust this threshold as needed
    for j in range(1, len(data)-1):
        if data[j] - data[j-1] > threshold and data[j] - data[j+1] > threshold:
            peak_indices.append(j)  # Storing the index, not the value
    return peak_indices

#from the peaks, calculate heart rate
def compute_heart_rate(peak_indices, sampling_rate):
    """Compute heart rate using the time between peaks."""
    if len(peak_indices) <= 1:
        print(len(peak_indices))
        return "Cannot compute heart rate with less than two peaks"
    # Calculate average distance between peaks
    #average_distance = sum([peaks[i+1] - peaks[i] for i in range(len(peaks) - 1)]) / (len(peaks) - 1)
    # Initialize a list to store distances between consecutive peaks
    distances_between_peaks = []

    # Calculate distances between consecutive peaks
    for i in range(len(peak_indices) - 1):
        distance = peak_indices[i+1] - peak_indices[i]
        distances_between_peaks.append(distance)

    # Calculate the sum of all distances
    total_distance = sum(distances_between_peaks)

    # Calculate the average distance between peaks
    average_distance = total_distance / len(distances_between_peaks)
    # Convert average distance into frequency (Hz)
    frequency = sampling_rate / average_distance
    
    # Convert frequency to BPM
    bpm = frequency * 60
    return bpm

def heart_rate_from_red_buffer(red_buffer, sampling_rate=200):
    """Calculate heart rate from red_buffer data."""
    # Smooth the data
    smoothed_data = simple_moving_average(red_buffer, 20)#global variable
    print("length of smoothed data: ", len(smoothed_data))#so the moving average function doesn't return anything
    #print("I'm now printing smoothed data\n")
    #for z in smoothed_data:
        #print(smoothed_data)
    # Detect peaks
    peaks = detect_peaks(smoothed_data)
    print("length of peaks:", len(peaks))
    #for y in peaks:
    #    print(y)
    
    # Compute heart rate
    heart_rate = compute_heart_rate(peaks, sampling_rate)#sampling rate of 200Hz
    
    return heart_rate

while True:
    #collect the data through pulsing of the led
    LED_switch(WINDOW_SIZE)#send in the window size
    heart_rate = heart_rate_from_red_buffer(red_buffer)
    print("Heart Rate:", heart_rate, "BPM")
    #free up the memory of buffers
    red_buffer = []
    ir_buffer = []
    utime.sleep(0.2)#to allow the system to breathe a little
