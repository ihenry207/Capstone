import machine
from machine import Pin, SPI, I2C
from ssd1306 import SSD1306_I2C
from mcp3008 import MCP3008
import utime

    
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

def Format_Voltage(value):#formats the adc value back into voltage for reference
    voltage = (value / 1023.0) * 3.3
    voltage_str = "{:.2f}".format(voltage)
    formatted_Voltage = float(voltage_str)
    return formatted_Voltage

while True:
    led.off()#turn off the LED. it is to make sure the code is working andf for debugging purposes
    value = mcp3008.read(0)
    formatted_Voltage = Format_Voltage(value)
    oled.text(f"ADC Value: {value}",0,0)
    oled.text(f"Voltage: {formatted_Voltage}", 0, 30)#middle left
    oled.show()
    utime.sleep(0.5)
    led.on()
    oled.fill(0) #clear whatever is there
    oled.show()
    value = mcp3008.read(0)
    formatted_Voltageb = Format_Voltage(value)
    oled.text(f"ADC Value: {value}",0,0)#top left
    oled.text(f"Voltage: {formatted_Voltage}", 0, 30)#middle left
    oled.show()
    utime.sleep(0.5)
    oled.fill(0) #clear whatever is there
    oled.show()
