import machine
from machine import Pin, SPI, I2C
import time
from mcp3008 import MCP3008

# Configuration
spi = SPI(0, sck=Pin(2), mosi=Pin(3), miso=Pin(4), baudrate=100000)
cs = Pin(22, Pin.OUT)#can be any GPIO pins on the board, Chip read
cs.value(1)  # disable chip at start
mcp3008 = MCP3008(spi, cs)
sample_rate = 25  # 25 Hz sample rate (0.04 seconds between samples)
heart_rate_window_size = 15 #for heart window size is usually between 10 to 20 samples.
#the more the samples the more delay
spo2_window_size = 30 #for SpO2 is btn 20 to 50 samples
heart_rate_buffer = []
spo2_buffer = [] 

led = Pin('LED', Pin.OUT)#for troubleshooting

while True:
    adc_value = mcp3008.read(0)#read the adc value
    heart_rate_buffer.append(adc_value)
    spo2_buffer.append(adc_value)
    
    # Maintain rolling buffers for heart rate and SpO2
    if len(heart_rate_buffer) > heart_rate_window_size:
        heart_rate_buffer.pop(0)
    
    if len(spo2_buffer) > spo2_window_size:
        spo2_buffer.pop(0)
    
    # Calculate heart rate periodically
    if len(heart_rate_buffer) == heart_rate_window_size:
        # Peak detection for heart rate
        peaks = []
        for i in range(1, len(heart_rate_buffer) - 1):
            if heart_rate_buffer[i] > heart_rate_buffer[i - 1] and heart_rate_buffer[i] > heart_rate_buffer[i + 1]:
                peaks.append(i)
        
        if len(peaks) >= 2:
            peak_interval = (peaks[-1] - peaks[0]) / (sample_rate * (len(peaks) - 1))
            heart_rate_bpm = int(60 / peak_interval)
            print("Heart Rate:", heart_rate_bpm, "bpm")
    
    # Calculate SpO2 periodically
    if len(spo2_buffer) == spo2_window_size:
        # Simple SpO2 estimation
        ac_sum = sum(spo2_buffer) - len(spo2_buffer) * sum(spo2_buffer) / len(spo2_buffer)
        dc_sum = sum(spo2_buffer) / len(spo2_buffer)
        spo2 = 100 * (ac_sum / dc_sum)  # Adjust based on your sensor's characteristics
        print("SpO2:", spo2, "%")
    
    time.sleep(1 / sample_rate)  # Maintain the desired sample rate