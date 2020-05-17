# Piedroit

Turn a Raspberry Pi into a footswitch that emulates a USB keyboard.

# Instructions

Based on [Composite USB Gadgets on the Raspberry Pi Zero](https://www.isticktoit.net/?p=1383) from iSticktoit.net

Tested on a Rasperry Pi Zero W Rev 1.1.

## Step 1: Kernel modules

To make this work, we need to enable something called a **device tree overlay**, and then add two modules to `/etc/modules`:

```
echo "dtoverlay=dwc2" | sudo tee -a /boot/config.txt
echo "dwc2" | sudo tee -a /etc/modules
sudo echo "libcomposite" | sudo tee -a /etc/modules
```

(Check out [this Stack Exchange post](https://raspberrypi.stackexchange.com/questions/77059/what-does-dtoverlay-dwc2-really-do) if you want to understand what's really going on here. It's a bit gnarly.)

## Step 2: Config Stuff

Create a file `/usr/bin/piedroit_usb` with the following content:

```bash
#!/bin/bash
cd /sys/kernel/config/usb_gadget/
mkdir -p piedroit
cd piedroit
echo 0x1d6b > idVendor # Linux Foundation
echo 0x0104 > idProduct # Multifunction Composite Gadget
echo 0x0100 > bcdDevice # v1.0.0
echo 0x0200 > bcdUSB # USB2
mkdir -p strings/0x409 # 0x409 is the Language ID for English - United States
echo "fedcba9876543210" > strings/0x409/serialnumber
echo "Dylan Beattie" > strings/0x409/manufacturer
echo "Piedroit USB Footswitch" > strings/0x409/product
mkdir -p configs/c.1/strings/0x409
echo "Config 1: ECM network" > configs/c.1/strings/0x409/configuration
echo 250 > configs/c.1/MaxPower


# Function definition for emulating a USB keyboard
mkdir -p functions/hid.usb0
echo 1 > functions/hid.usb0/protocol
echo 1 > functions/hid.usb0/subclass
echo 8 > functions/hid.usb0/report_length
echo -ne \\x05\\x01\\x09\\x06\\xa1\\x01\\x05\\x07\\x19\\xe0\\x29\\xe7\\x15\\x00\\x25\\x01\\x75\\x01\\x95\\x08\\x81\\x02\\x95\\x01\\x75\\x08\\x81\\x03\\x95\\x05\\x75\\x01\\x05\\x08\\x19\\x01\\x29\\x05\\x91\\x02\\x95\\x01\\x75\\x03\\x91\\x03\\x95\\x06\\x75\\x08\\x15\\x00\\x25\\x65\\x05\\x07\\x19\\x00\\x29\\x65\\x81\\x00\\xc0 > functions/hid.usb0/report_desc
ln -s functions/hid.usb0 configs/c.1/
# END function definition for emulating a USB keyboard

ls /sys/class/udc > UDC
```

Make that file executable:

```
$ chmod 700 /usr/bin/piedroit_usb
```

Add these lines to `/etc/rc.local`, near the end of the file but BEFORE the `exit 0`:

```
# Enable Piedroit USB keyboard footswitch emulator
/usr/bin/piedroit_usb 
```

## Step 3: Test it

1. Make sure you are running your Pi off an isolated USB power supply connected to the POWER micro-USB port. **Do not connect the DATA micro USB port to anything yet**
2. Reboot your Pi 
3. Once it's up and running, connect the DATA micro-USB port to your host PC.
4. You should see Windows recognise and install a **"Piedroit USB Footswitch"** device.

Now run piedroit as sudo:

`$ sudo python ./piedroit.py`

Change focus on the host PC to a tool such as [PassMark KeyboardTest](https://www.passmark.com/products/keytest/).

Now connect GPIO pin 04 to GND - this should send the keystroke Ctrl-F1 to the host PC.

See the code in [piedroit.py](piedroit.py) to see how it works and change which GPIO pins send which keystrokes.

## Run it automatically

Add another line to `/etc/rc.local`, near the end of the file, AFTER the line that runs `/usb/bin/piedroit_usb` but BEFORE the `exit 0`:

```
# Start Piedroit USB keyboard footswitch emulator automatically
sudo python /home/pi/piedroit/piedroit.py &
```

Note the `&` at the end - this makes `piedroit` run in the background when the system boots.





