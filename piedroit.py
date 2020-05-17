#!/usr/bin/env python
# piedroit: translate GPIO pin inputs into USB keystrokes
# https://github.com/dylanbeattie/piedroit

import RPi.GPIO as GPIO
import modifier_keys

NULL_CHAR = chr(0)

def send_data_to_usb(data):
    with open('/dev/hidg0', 'rb+') as fd:
        fd.write(data.encode())

def get_key_code(gpio_pin):
    # USB key codes are defined at https://www.usb.org/sites/default/files/documents/hut1_12v2.pdf
    # Physical switches are wired to GPIO pins 4-11
    # I want footswitch #1 (GPIO pin 04) to send F1, #2 > GPIO02 > F2, etc.
    # F1 has USB key code 58 (0x3A), F2 is 59, etc. 
    # So we can get the key code we need by adding 54 to the GPIO pin number.
    return(gpio_pin + 54)

def send_key_down(key_code):
    # USB key events are an 8-byte struct containing:
    # - a one-byte bitfield of modifier keys 
    # - a null byte
    # - Up to six key codes. (USB allows you to press up to six keys simultaneously)
    #
    # This code will always send Ctrl+{key}
    modifiers = modifier_keys.LEFT_CTRL
    key_data = chr(modifiers) + NULL_CHAR + chr(key_code) + NULL_CHAR*5
    send_data_to_usb(key_data)

def release_all_keys():
    send_data_to_usb(NULL_CHAR*8)

def send_key_for_gpio_pin(gpio_pin):
    key_code = get_key_code(gpio_pin)
    send_key_down(key_code)

# This code will support GPIO pins 4-21, although 
# only pins 4-11 are actually connected in my device
FIRST_GPIO_PIN = 4
FINAL_GPIO_PIN  = 21
ALL_PINS = range(FIRST_GPIO_PIN,FINAL_GPIO_PIN)

# Tell the Pi which numbering mode we're using to talk to the GPIO pins
# https://raspberrypi.stackexchange.com/questions/12966/what-is-the-difference-between-board-and-bcm-for-gpio-pin-numbering
GPIO.setmode(GPIO.BCM)

for pin in ALL_PINS:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Remember closing a switch connects the GPIO pin to ground (GND)
# so GPIO.input(pin) will return 0 ("grounded") or 1 ("not grounded")
SWITCH_CLOSED = 0

# Now we just sit in an infinite loop, reading all the GPIO pin states 
# every time we loop, and watching to see if any pin state has changed.
previous_states = [1] * FINAL_GPIO_PIN

while True:
    for pin in ALL_PINS:
        state = GPIO.input(pin)
        previous_state = previous_states[pin]
        if (state != previous_state):
            if (state == SWITCH_CLOSED):
                print("GPIO PIN {} now CLOSED".format(pin))
                send_key_for_gpio_pin(pin)
            else:
                print("GPIO PIN {} now OPEN".format(pin))
                release_all_keys()

            previous_states[pin] = state
 
# This is good practice, but since we're going to sit in our loop
# until we kill the process or disconnect the power, we'll never
# actually get here. But in this scenario, that's OK.
for pin in ALL_PINS:
    GPIO.cleanup(pin)
