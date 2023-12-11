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

def custom_min(values):
    try:
        # Check if the list is empty; if so, raise a ValueError
        if not values:
            raise ValueError("Empty list provided for min calculation.")
        min_value = values[0]  # Initialize min_value with the first element of the list
        for value in values:   # Iterate through each element in the list
            if value < min_value:  # If the current element is smaller than min_value
                min_value = value  # Update min_value to the current element
        return min_value  # Return the minimum value found
    except TypeError:
        # Handle the TypeError if elements in the list are not comparable
        print("TypeError encountered in custom_min: Non-comparable elements.")
        return None
    except ValueError as e:
        # Handle the ValueError if an empty list is passed
        print(f"ValueError in custom_min: {e}")
        return None

def custom_max(values):
    try:
        # Check if the list is empty; if so, raise a ValueError
        if not values:
            raise ValueError("Empty list provided for max calculation.")
        max_value = values[0]  # Initialize max_value with the first element of the list
        for value in values:   # Iterate through each element in the list
            if value > max_value:  # If the current element is greater than max_value
                max_value = value  # Update max_value to the current element
        return max_value  # Return the maximum value found
    except TypeError:
        # Handle the TypeError if elements in the list are not comparable
        print("TypeError encountered in custom_max: Non-comparable elements.")
        return None
    except ValueError as e:
        # Handle the ValueError if an empty list is passed
        print(f"ValueError in custom_max: {e}")
        return None

def custom_sum(numbers):
    try:
        total = 0  # Initialize total to 0
        for number in numbers:  # Iterate through each number in the list
            total += number  # Add each number to the total
        return total  # Return the sum of the numbers
    except TypeError:
        # Handle TypeError if a non-numeric value is encountered
        print("TypeError: Non-numeric value encountered in custom_sum.")
        return None

def custom_len(items):
    try:
        count = 0  # Initialize count to 0
        for _ in items:  # Iterate through each item in the iterable
            count += 1  # Increment count for each item
        return count  # Return the total number of items
    except TypeError:
        # Handle TypeError if the provided argument is not iterable
        print("TypeError: Provided argument is not iterable in custom_len.")
        return None

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
    if peak and custom_len(values) - peak[0] >= min_distance:
        peaks.append(peak)
    print("the length of peaks is: ", len(peaks))

    return peaks

def find_heart_rate(values):
    # Redefine the threshold and minimum distance
    threshold = 45000#according to matlab, threshold can change anytime
    min_distance = 40  # This corresponds to 0.6 seconds given a sampling rate of 100Hz

    # Find the peaks using the custom function with the new parameters
    peaks = find_peaks(values, threshold, min_distance)
    # Calculate the heart rates from the peaks
    heart_rates = []
    for i in range(1, custom_len(peaks)):
        try:
            # Calculate the time difference between peaks in seconds
            time_diff = (peaks[i][0] - peaks[i-1][0]) / 100.0  # Convert from samples to seconds
            # Calculate the heart rate from the time difference
            heart_rate = 60.0 / time_diff
            heart_rates.append(heart_rate)
        except ZeroDivisionError:
            # Handle the case where time_diff is zero, which causes division by zero
            print("Warning: Division by zero encountered in heart rate calculation.")
            continue #continue. this is a more forgiving approach
        
    # Safely calculate the average heart rate
    try:
        # Filter out heart rates below 50
        valid_heart_rates = [rate for rate in heart_rates if rate >= 50]
        average_heart_rate = custom_sum(valid_heart_rates) / custom_len(valid_heart_rates)
    except ZeroDivisionError:
        print("Error: Division by zero when calculating average heart rate.")
        return None
    except ValueError as e:
        print(f"ValueError in find_heart_rate(): {e}")
        return None
    
    # Create a string from the heart_rates list in the desired format
    heart_rates_str = '{' + ','.join(['{:.2f}'.format(rate) for rate in heart_rates]) + '}'
    # Print the heart rates in the desired format
    print(f"Heart rates are {heart_rates_str}")
    return average_heart_rate


def new_spo2(red_values, ir_values):
    try:
        max_red = custom_max(red_values)
        min_red = custom_min(red_values)
        max_ir = custom_max(ir_values)
        min_ir = custom_min(ir_values)

        if max_red is None or min_red is None or max_ir is None or min_ir is None:
            raise ValueError("Invalid values for SpO2 calculation.")

        R1 = (max_red - min_red) * min_ir
        R2 = (max_ir - min_ir) * min_red
        R = R1 / R2 #find the ratio
    except ZeroDivisionError:
        print("Error: Division by zero encountered. Cannot calculate SpO2.")
        return None
    except ValueError as e:
        print(f"ValueError in new_spo2: {e}")
        return None

    sqR = R**2
    cubeR = R**3
    spo2 = (100*cubeR)-(530*sqR)+(430*R)+97
    return spo2

def main():
    red_values, ir_values = LED_switch(WINDOW_SIZE)
    
    spo2 = new_spo2(red_values, ir_values)
    bpm = find_heart_rate(red_values)
    
    if bpm is None:
        print("An error occurred in Heart rate calculation.")
        oled.text("BPM Error", 0, 30)
        oled.show()
    else:
        print("bpm calculation successful.")
        oled.text("{:.2f} BPM".format(bpm), 0, 30)
        oled.show()
        print("Estimated heart rate: {:.2f} ".format(bpm))
        
    print("\n")
    
    if spo2 is None:
        oled.text("spo2 Error", 0, 0)
        oled.show()
        print("An error occurred in spo2 calculation.")
    else:
        print("spo2 calculation successful.")
        oled.text("{:.2f} %spo2".format(spo2), 0, 0)
        oled.show()
        print("Estimated SpO2 Level: {:.2f}% ".format(spo2))

    gc.collect()
    utime.sleep(2)
    
for _ in range(1):
    main()


