import machine
from machine import Pin, SPI, I2C
from ssd1306 import SSD1306_I2C
import utime
class MCP3008:
    def __init__(self, spi, cs, ref_voltage=3.3):
        """
        Creating MCP3008 instance
        
        cs:chip select pin
        ref_voltsge  is r
        spi: is the configured spi bus
        
        """
        self.cs = cs
        self.cs.value(1)  # ncs on
        self._spi = spi
        self._out_buf = bytearray(3)
        self._out_buf[0] = 0x01
        self._in_buf = bytearray(3)
        self._ref_voltage = ref_voltage

    def reference_voltage(self) -> float:
        """Returns the MCP3xxx's reference voltage as a float."""
        return self._ref_voltage

    def read(self, pin, is_differential=False):#here we will be reading from channel 0 or pin 0
        """
        read a voltage or voltage difference using the MCP3008.

        Args:
            pin: the pin to use
            is_differential: if true, return the potential difference between two pins,

        Returns:
            voltage in range [0, 1023] where 1023 = VREF (3V3)
        """
        self.cs.value(0)  # select and ready to communicate
        self._out_buf[1] = ((not is_differential) << 7) | (pin << 4)
        self._spi.write_readinto(self._out_buf, self._in_buf)
        self.cs.value(1)  # turn off or end communication
        return ((self._in_buf[1] & 0x03) << 8) | self._in_buf[2]
    
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
