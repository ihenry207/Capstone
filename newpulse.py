"""this code is able to pulse LED using a single core at 100Hz as expected"""

import machine
import time
from machine import Pin, SPI, I2C, ADC
from ssd1306 import SSD1306_I2C
#from mcp3008 import MCP3008
import utime
#import math
import gc
 
# Initialize the ADC
adc = ADC(Pin(26))
WIDTH = 128
HEIGHT = 64
i2c = I2C(0, scl = Pin(17), sda = Pin(16), freq = 200000)
oled = SSD1306_I2C(WIDTH, HEIGHT, i2c)
# Define pins
pin1 = Pin(14, Pin.OUT)
pin2 = Pin(15, Pin.OUT)

WINDOW_SIZE = 1300 #needs to be big enough to accurately calculate heart rate
# Buffers and variable
red_buffer = [0] * WINDOW_SIZE
ir_buffer = [0] * WINDOW_SIZE #for blood oxygen levels
#new_red = []
#reading 3 values when red is on
def LED_switch(Window_Size):
    print("pulsing the leds now")
    i = 0
    while i < Window_Size:
        pin1.high()
        pin2.low()
        utime.sleep_us(1600) #wait for signal to get high
        red_buffer[i] =  adc.read_u16() 
        
        utime.sleep_us(3452)#100Hz 3262- (520+320+520+320+20(if stats)) = 1582 = 1600
     
        pin1.low()
        pin2.high()
        
        utime.sleep_us(1600) #sleep for half a pulse
        ir_buffer[i] = adc.read_u16()
        utime.sleep_us(3452) #plus 3262+ 500 +320 for the reading adc
        i += 1 #increment i
        
    # Number of readings to discard
    readings_to_discard = 300#since we are reading 3 times when it's high
    valid_red_buffer = red_buffer[readings_to_discard:]
    valid_ir_buffer = ir_buffer[readings_to_discard:]
    print("printing ir buffer numbers\n\n")
    print(valid_ir_buffer)
    print("\n\n\n")
    print("printing red buffer numbers\n\n\n")
    print(valid_red_buffer)
    return valid_red_buffer, valid_ir_buffer

# Let's redefine the peak detection with the new threshold and minimum distance parameters
def find_peaks(values, threshold, min_distance):
    peaks = []
    peak = None
    i = 0  # Initialize the counter manually

    for value in values:
        if value > threshold:
            if not peak:
                peak = (i, value)
            elif value > peak[1]:
                peak = (i, value)
        else:
            if peak and i - peak[0] >= min_distance:
                peaks.append(peak)
                peak = None
        i += 1  # Manually increment the counter

    # Check if the last peak is a valid peak and hasn't been added yet
    if peak and len(values) - peak[0] >= min_distance:
        peaks.append(peak)

    return peaks

def find_heart_rate(values):
    # Redefine the threshold and minimum distance
    threshold = 36000#according to matlab, threshold can change anytime
    min_distance = 60  # This corresponds to 0.6 seconds given a sampling rate of 100Hz

    # Find the peaks using the custom function with the new parameters
    peaks = find_peaks(values, threshold, min_distance)
    # Calculate the heart rates from the peaks
    heart_rates = []
    for i in range(1, len(peaks)):
        # Calculate the time difference between peaks in seconds
        time_diff = (peaks[i][0] - peaks[i-1][0]) / 100.0  # Convert from samples to seconds
        # Calculate the heart rate from the time difference
        heart_rate = 60.0 / time_diff
        heart_rates.append(heart_rate)

    # Calculate the average heart rate
    average_heart_rate = sum(heart_rates) / len(heart_rates)
    # Create a string from the heart_rates list in the desired format
    heart_rates_str = '{' + ','.join(['{:.2f}'.format(rate) for rate in heart_rates]) + '}'
    # Print the heart rates in the desired format
    print(f"Heart rates are {heart_rates_str}")
    return average_heart_rate
# Function to extract AC and DC components from the signals
def extract_ac_dc_components(signal):
    """
    Extracts the AC and DC components from the given PPG signal.
    The DC component is the average of the signal, and the AC component is the peak-to-peak amplitude.
    """
    dc_component = sum(signal) / len(signal)
    ac_component = max(signal) - min(signal)
    return ac_component, dc_component

# Function to calculate ROR (Ratio of Ratios)
def calculate_ror(red_ac, red_dc, ir_ac, ir_dc):
    """
    Calculates the Ratio of Ratios (ROR) for the given AC and DC components of red and infrared signals.
    """
    ror = (red_ac / red_dc) / (ir_ac / ir_dc)
    return ror

# Function to estimate SpO2
def estimate_spo2(ror):
    """
    Estimates the SpO2 based on the Ratio of Ratios (ROR) and empirical coefficients.
    Default values for A and B are chosen and does not reflect actual calibration values.
    """
    B = 1.5
    A = 98 + B * ror
    spo2 = A - B * ror
    return spo2


def find_spo2(red_values, ir_values):
    # Extract AC and DC components for both red and infrared signals
    red_ac, red_dc = extract_ac_dc_components(red_values)
    ir_ac, ir_dc = extract_ac_dc_components(ir_values)
    
    # Calculate the ROR
    ror = calculate_ror(red_ac, red_dc, ir_ac, ir_dc)

    # Estimate SpO2
    estimated_spo2 = estimate_spo2(ror)
    
    return estimated_spo2

def new_spo2(red_values, ir_values):
    R1 = (max(red_values) - min(red_values)) * (min(ir_values))
    R2 = (max(ir_values) - min(ir_values)) * (min(red_values))
     # Handle division by zero
    if R2 == 0:
        print("Error: Division by zero encountered. Cannot calculate SpO2.")
        return None

    R = R1 / R2
    sqR = R**2
    cubeR = R**3
    spo2 = (10*cubeR)-(53*sqR)+(43*R)+98
    return spo2

while True:
    red_values, ir_values = LED_switch(WINDOW_SIZE)
    
    spo2 = new_spo2(red_values, ir_values)
    #spo2 = find_spo2(red_values, ir_values)
    bpm = find_heart_rate(red_values)
    print("Estimated Heart Rate: {:.2f} BPM".format(bpm))
    print("Estimated SpO2 Level: {:.2f}% ".format(spo2))
    #find_spo2(red _values, red_peaks, ir_values, ir_peaks)
   # Display the heart rate on the OLED
    oled.fill(0)  # Clear the display
    oled.text("Heart Rate: ", 0, 0)  # Top left
    oled.text("{:.2f} BPM".format(bpm), 0, 30)  # Middle left
    oled.show()  # Show the display
    
    #red_buffer = []#clear the buffers
    #Ir_buffer = []
    gc.collect()
    break 

