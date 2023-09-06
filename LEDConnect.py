from machine import Pin, PWM
import utime

#constants
Freq = 50 #50Hz
Duty_Cycle = 50 #percent
#Corresponding to 50% duty cycle for 16-bit resolution of the pi pico 2^16 - 1 = 65535 50% is that nbr
High_Duty = 32767
Low_Duty = 0

# Initialize the two pins for PWM
ir_led = PWM(Pin(14))  # IR LED connected to GP0
red_led = PWM(Pin(15))  # Red LED connected to GP1

# Function to toggle the LEDs
def toggle_leds():
    if ir_led.duty_u16() == High_Duty:
        ir_led.duty_u16(Low_Duty)
        red_led.duty_u16(High_Duty)
    else:
        ir_led.duty_u16(High_Duty)
        red_led.duty_u16(Low_Duty)


# Start with IR LED on and Red LED off
ir_led.duty_u16(High_Duty)
red_led.duty_u16(Low_Duty)
led = Pin('LED', Pin.OUT)
while True:
    toggle_leds()
    utime.sleep(0.01)  # Sleep for 10ms, resulting in toggling at 50Hz