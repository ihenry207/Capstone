from machine import SPI, Pin
import utime

spi = SPI(0, sck = Pin(2), mosi = Pin(3), miso = Pin(4))
led = Pin('LED', Pin.OUT) #to help out debug
channel = 0
#create a function that reads MCP3008
def read_mcp3008(channel):
    # MCP3008 operates in single-ended mode
    # Send start bit, single/differential bit (0), and channel (0-7) but we are using channel 0 here
    command = 0b11 << 6 | (channel & 0x07) << 3
    data = bytearray(3)
    spi.write_readinto(bytes([command, 0, 0]), data)
    # Extract and return the 10-bit ADC value
    return ((data[0] & 0x01) << 9) | (data[1] << 1) | (data[2] >> 7)

while True:
    led.on()
      #we are using channel 0 here
    value = read_mcp3008(channel)
    
    # Calculate the voltage using the ADC's reference voltage (3.3V)
    voltage = (value / 1023.0) * 3.3
    
    print("Channel {}: ADC Value = {}, Voltage = {:.2f}V".format(channel, value, voltage))
    
    utime.sleep(1)
    #led.off()
    #utime.sleep(1)