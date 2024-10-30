from machine import Pin, ADC
from time import sleep

# Constants for LCD commands
LCD_CMD = 0
LCD_CHR = 1
LCD_CLR = 0x01  # Clear display
LCD_HOME = 0x02  # Return home

# Pin assignments
RS = Pin(14, Pin.OUT)
EN = Pin(15, Pin.OUT)
D4 = Pin(16, Pin.OUT)
D5 = Pin(17, Pin.OUT)
D6 = Pin(18, Pin.OUT)
D7 = Pin(19, Pin.OUT)

# ADC for onboard temperature sensor
sensor_temp = ADC(4)
conversion_factor = 3.3 / (65535)  # Conversion factor for 16-bit ADC to voltage

# Send command or character to the LCD
def lcd_write(bits, mode):
    RS.value(mode)  # RS = 0 for command, 1 for character
    for pin, value in zip((D4, D5, D6, D7), ((bits >> 4) & 1, (bits >> 5) & 1, (bits >> 6) & 1, (bits >> 7) & 1)):
        pin.value(value)
    lcd_toggle_enable()
    
    for pin, value in zip((D4, D5, D6, D7), (bits & 1, (bits >> 1) & 1, (bits >> 2) & 1, (bits >> 3) & 1)):
        pin.value(value)
    lcd_toggle_enable()

def lcd_toggle_enable():
    EN.value(1)
    sleep(0.0005)
    EN.value(0)
    sleep(0.0005)

def lcd_init():
    lcd_write(0x33, LCD_CMD)
    lcd_write(0x32, LCD_CMD)
    lcd_write(0x28, LCD_CMD)  # 4-bit mode, 2 lines, 5x7 font
    lcd_write(0x0C, LCD_CMD)  # Display on, no cursor
    lcd_write(0x06, LCD_CMD)  # Increment cursor
    lcd_write(LCD_CLR, LCD_CMD)
    sleep(0.002)

def lcd_string(message, line):
    if line == 1:
        lcd_write(0x80, LCD_CMD)
    elif line == 2:
        lcd_write(0xC0, LCD_CMD)

    for char in message:
        lcd_write(ord(char), LCD_CHR)

# Function to read temperature
def read_temperature():
    reading = sensor_temp.read_u16() * conversion_factor  # Convert to voltage
    temperature_c = 27 - (reading - 0.706) / 0.001721  # Convert voltage to Celsius
    return temperature_c

# Main Program
lcd_init()
lcd_string("Temperature:", 1)

while True:
    temperature_c = read_temperature()
    lcd_string("Temp: {:.2f} C".format(temperature_c), 2)
    sleep(1)  # Update every second
