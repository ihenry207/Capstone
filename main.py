from machine import Pin, I2C, SPI
from ssd1306 import SSD1306_I2C
import utime


WIDTH = 128
HEIGHT = 64

#max freq is 400K in fast mode
i2c = I2C(0, scl = Pin(17), sda = Pin(16), freq = 200000)
led = Pin('LED', Pin.OUT)


oled = SSD1306_I2C(WIDTH, HEIGHT, i2c)
t = 0
while(1):
    led.off()
    oled.fill(0) #clear whatever is there
    oled.show()
    utime.sleep(0.5)
    led.on()
    oled.text(f"Hello Henry: {t}", 0, 0) #top left of the led is the location
    oled.show()
    utime.sleep(0.5)
    t += 1
    

