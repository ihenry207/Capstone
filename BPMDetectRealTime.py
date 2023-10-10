import machine
from machine import Pin, SPI, I2C
from ssd1306 import SSD1306_I2C
from mcp3008 import MCP3008
import utime
import time

average_bpm = 0.0  # Running average of BPM
bpm_count = 0  # Number of BPM values recorded

# Set up GPIO 14 and 15 as outputs for LED flashing
redLED = machine.Pin(14, machine.Pin.OUT)
IrLED = machine.Pin(15, machine.Pin.OUT)

spi = SPI(0, sck=Pin(2), mosi=Pin(3), miso=Pin(4), baudrate=100000)
cs = Pin(22, Pin.OUT)#can be any GPIO pins on the board
cs.value(1)  # disable chip at start
mcp3008 = MCP3008(spi, cs)

led = Pin('LED', Pin.OUT)
BPM_VALUE_HI = 512  # adjust these thresholds according to observations
BPM_VALUE_LO = 400  # and ADC's range. MCP3008's 10-bit ADC: 0-1023
MIN_BPM = 40 #used to removing any noise 
MAX_BPM = 240 #used for removing any noise

last_beat_time = 0  # keeps track of the last detected beat time
current_beat_time = 0
state = "WAITING_FOR_HIGH"  # can be "WAITING_FOR_HIGH", "WAITING_FOR_LOW"



WINDOW_SIZE = 2800 #needs to be big enough to accurately calculate heart rate

#function to pulse the leds in real time
def LED_switch(Window_Size):
    global average_bpm
    IrLED.low()
    redLED.low()
    print("pulsing the leds now")
    
    pulse_duration = 0.00125  # intended 2.5ms for 200Hz
    
    for i in range(0, Window_Size-1):
        # For red LED
        start_time_red = utime.ticks_ms()  # Record the start time
        
        redLED.high()
        IrLED.low()
        sample = mcp3008.read(0)
        process_sample(sample)  # Note: You're calling it but not doing anything with the return value
        
        # Adjust sleep to maintain frequency
        elapsed_time_red = utime.ticks_diff(utime.ticks_ms(), start_time_red)
        adjusted_sleep_red = max(0, pulse_duration * 1000 - elapsed_time_red) / 1000.0
        utime.sleep(adjusted_sleep_red)

        # For IR LED
        start_time_ir = utime.ticks_ms()
        
        redLED.low()
        IrLED.high()
        sample_ir = mcp3008.read(0)  # You can further process this sample if needed
        
        elapsed_time_ir = utime.ticks_diff(utime.ticks_ms(), start_time_ir)
        adjusted_sleep_ir = max(0, pulse_duration * 1000 - elapsed_time_ir) / 1000.0
        utime.sleep(adjusted_sleep_ir)

    

        
def get_current_time():
    """Get the current time in milliseconds."""
    return utime.ticks_ms()

def process_sample(value):
    global last_beat_time, current_beat_time, state, average_bpm, bpm_count
    
    if state == "WAITING_FOR_HIGH":
        if value >= BPM_VALUE_HI:
            current_beat_time = get_current_time()
            
            # If not the first beat, then calculate BPM
            if last_beat_time:
                period_ms = current_beat_time - last_beat_time
                bpm = 60000 / period_ms  # conversion to BPM
                
                if MIN_BPM <= bpm <= MAX_BPM:
                    # Update the running average
                    bpm_count += 1
                    average_bpm = (average_bpm * (bpm_count - 1) + bpm) / bpm_count
                    return bpm
                else:
                    # reset if out of realistic range
                    last_beat_time = 0
                    current_beat_time = 0
                    
            last_beat_time = current_beat_time
            state = "WAITING_FOR_LOW"
            
    elif state == "WAITING_FOR_LOW":
        if value <= BPM_VALUE_LO:
            state = "WAITING_FOR_HIGH"
            
    return None


while True:
    LED_switch(WINDOW_SIZE)
    # Print the average BPM after processing each window of samples
    print("Heart Rate:", average_bpm, "BPM")
     # Reset the buffer
    #red_buffer = []
    #ir_buffer = []
    utime.sleep(0.2)