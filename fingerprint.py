# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

#import serial
import RPi.GPIO as GPIO
from datetime import datetime
import time
import board
from digitalio import DigitalInOut, Direction
import adafruit_fingerprint
import smtplib
import I2C_LCD_driver
import csv
from datetime import datetime


GPIO.setwarnings(False)  # Ignore warning for now
GPIO.setmode(GPIO.BCM)  # Use physical pin numbering
# Set pin 10 to be an input pin and set initial value to be pullcd low (off)
GPIO.setup(10, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)


lcd = I2C_LCD_driver.lcd()

lcd = DigitalInOut(board.D13)
lcd.direction = Direction.OUTPUT


# uart = busio.UART(board.TX, board.RX, baudrate=57600)

# If using with a computer such as Linux/RaspberryPi, Mac, Windows with USB/serial converter:
# import serial
uart = serial.Serial("/dev/ttyUSB0", baudrate=57600, timeout=1)

# If using with Linux/Raspberry Pi and hardware UART:
#uart = serial.Serial("/dev/ttyS0", baudrate=57600, timeout=1)

finger = adafruit_fingerprint.Adafruit_Fingerprint(uart)

##################################################


def get_fingerprint():
    """Get a finger print image, template it, and see if it matches!"""
    print("Waiting for image...")
    while finger.get_image() != adafruit_fingerprint.OK:
        pass
    print("Templating...")
    if finger.image_2_tz(1) != adafruit_fingerprint.OK:
        return False
    print("Searching...")
    if finger.finger_search() != adafruit_fingerprint.OK:
        return False
    return True


# pylint: disable=too-many-branches
def get_fingerprint_detail():
    """Get a finger print image, template it, and see if it matches!
    This time, print out each error instead of just returning on failure"""
    print("Getting image...", end="")
    i = finger.get_image()
    if i == adafruit_fingerprint.OK:
        print("Image taken")
    else:
        if i == adafruit_fingerprint.NOFINGER:
            print("No finger detected")
        elif i == adafruit_fingerprint.IMAGEFAIL:
            print("Imaging error")
        else:
            print("Other error")
        return False

    print("Templating...", end="")
    i = finger.image_2_tz(1)
    if i == adafruit_fingerprint.OK:
        print("Templated")
    else:
        if i == adafruit_fingerprint.IMAGEMESS:
            print("Image too messy")
        elif i == adafruit_fingerprint.FEATUREFAIL:
            print("Could not identify features")
        elif i == adafruit_fingerprint.INVALIDIMAGE:
            print("Image invalid")
        else:
            print("Other error")
        return False

    print("Searching...", end="")
    i = finger.finger_fast_search()
    # pylint: disable=no-else-return
    # This block needs to be refactored when it can be tested.
    if i == adafruit_fingerprint.OK:
        print("Found fingerprint!")
        return True
    else:
        if i == adafruit_fingerprint.NOTFOUND:
            print("No match found")
        else:
            print("Other error")
        return False


# pylint: disable=too-many-statements
def enroll_finger(location):
    """Take a 2 finger images and template it, then store in 'location'"""
    for fingerimg in range(1, 3):
        if fingerimg == 1:
            print("Place finger on sensor...", end="")
        else:
            print("Place same finger again...", end="")

        while True:
            i = finger.get_image()
            if i == adafruit_fingerprint.OK:
                print("Image taken")
                break
            if i == adafruit_fingerprint.NOFINGER:
                print(".", end="")
            elif i == adafruit_fingerprint.IMAGEFAIL:
                print("Imaging error")
                return False
            else:
                print("Other error")
                return False

        print("Templating...", end="")
        i = finger.image_2_tz(fingerimg)
        if i == adafruit_fingerprint.OK:
            print("Templated")
        else:
            if i == adafruit_fingerprint.IMAGEMESS:
                print("Image too messy")
            elif i == adafruit_fingerprint.FEATUREFAIL:
                print("Could not identify features")
            elif i == adafruit_fingerprint.INVALIDIMAGE:
                print("Image invalid")
            else:
                print("Other error")
            return False

        if fingerimg == 1:
            print("Remove finger")
            time.sleep(1)
            while i != adafruit_fingerprint.NOFINGER:
                i = finger.get_image()

    print("Creating model...", end="")
    i = finger.create_model()
    if i == adafruit_fingerprint.OK:
        print("Created")
    else:
        if i == adafruit_fingerprint.ENROLLMISMATCH:
            print("Prints did not match")
        else:
            print("Other error")
        return False

    print("Storing model #%d..." % location, end="")
    i = finger.store_model(location)
    if i == adafruit_fingerprint.OK:
        print("Stored")
    else:
        if i == adafruit_fingerprint.BADLOCATION:
            print("Bad storage location")
        elif i == adafruit_fingerprint.FLASHERR:
            print("Flash storage error")
        else:
            print("Other error")
        return False

    return True


##################################################


def get_num():
    """Use input() to get a valid number from 1 to 127. Retry till success!"""
    i = 0
    while (i > 127) or (i < 1):
        try:
            i = int(input("Enter ID # from 1-127: "))
        except ValueError:
            pass
    return i


# for leds
GPIO.setup(11, GPIO.OUT)
GPIO.setup(13, GPIO.OUT)

# for email
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()

id = 0
text = ""
server_address = 'http://192.168.0.108:5000'
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

server.login('muneesh1512@gmail.com', 'fhsjtotezlevisdg')

with open ('student.csv', 'w', newline='') as f:
        coloumn = ['Name', 'Date', 'Time']
        thewriter = csv.DictWriter (f, fieldnames = coloumn)
        thewriter.writeheader ()


def send_email(student):
    if (student == "Pallvi"):
        server.sendmail('teacherdemochitkara@gmail.com',
                        'mailto:pallvi4824.be21@chitkara.edu.in', 'Attendance Granted')

    elif (student == "Muneesh"):
        server.sendmail('teacherdemochitkara@gmail.com',
                        'muneesh4812.be21@chitkara.edu.in', 'Attendance Granted')
    elif (student == "Sakshi"):
        server.sendmail('teacherdemochitkara@gmail.com',
                        'sakshi4818.be21@chitkara.edu.in', 'Attendance Granted')
    elif (student == "Devanshu"):
        server.sendmail('teacherdemochitkara@gmail.com',
                        'devanshu4820.be21@chitkara.edu.in', 'Attendance Granted')
    thewriter.writerow({'Name': student,'Date':datetime.datetime.now()})

def send_post_to_server(json_text):
    requests.post(server_address, data=json_text, headers=headers)


def make_attendance():
    while True:  # Run forever
        data = []
        lcd.lcd_display_string_pos("==* WEL-COME *==", 1, 0)
        lcd.lcd_display_string_pos(">>Push Thumb<<", 2, 0)
        if (get_fingerprint()):
            lcd.lcd_clear()
            if (finger.finger_id() == 1):
                name = "Pallvi"
            elif (finger.finger_id() == 2):
                name = "Sakshi"
            elif (finger.finger_id() == 3):
                name = "Muneesh"
            elif (finger.finger_id() == 4):
                name = "Devanshu"
                data.append(finger.finger_id)
            send_email(name)
            lcd.lcd_display_string_pos("==* SUCCESS *== ", 1, 0)
            GPIO.output(25, True)
            time.sleep(2)
            lcd.lcd_clear()
        else:
            lcd.lcd_display_string_pos(">>Failed<<", 1,0)
            GPIO.output(25, False)
            GPIO.output(12, True)
            time.sleep(2)
            GPIO.output(12, False)
        time.sleep(1)
        return data

make_attendance()
