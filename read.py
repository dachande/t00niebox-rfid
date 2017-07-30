#!/usr/bin/env python

import RPi.GPIO as GPIO
import MFRC522
import signal
import time
import subprocess

read_loop = True
online = False
rfid_status = 0
rfid_read = 0
card_uid = None
client_error = 0

# Capture SIGINT for cleanup when the script is aborted
def end_read(signal, frame):
    global read_loop
    global online
    print "Exiting read loop."
    read_loop = False
    online = False
    GPIO.cleanup()

# Hook the SIGINT
signal.signal(signal.SIGINT, end_read)

# Create Reader
Reader = MFRC522.MFRC522()

# This loop is checking for chips
while read_loop:
    (status, tag_type) = Reader.MFRC522_Request(Reader.PICC_REQIDL)

    if status == Reader.MI_OK:
        rfid_read = 0
        online = True

        while online:
            (rfid_status, uid) = Reader.MFRC522_Anticoll()

            if rfid_status == Reader.MI_OK:
                if rfid_read == 0:
                    rfid_read = 1
                    client_error = 1

                    card_uid = format(uid[0], "x") + format(uid[1], "x") + format(uid[2], "x") + format(uid[3], "x")

                    print "Card detected."
                    print "Card UID: " + card_uid
                    print "Calling t00niebox client script"
                    print "-----"
                    try:
                        response = subprocess.check_output(["/home/t00niebox/t00niebox-client/dispatch", card_uid])
                        client_error = 0
                    except subprocess.CalledProcessError:
                        client_error = 1
                        print "-----"
                        print "t00niebox script returned an error."
                    print "-----"
            else:
                online = False

                print "Card removed."
                if client_error == 0:
                    print "Calling t00niebox client script"
                    print "-----"
                    try:
                        response = subprocess.check_output(["/home/t00niebox/t00niebox-client/dispatch", "00000000"])
                    except subprocess.CalledProcessError:
                        print "-----"
                        print "t00niebox client script returned an error."
                    print "-----"
                else:
                    print "Skipping pause command due to t00niebox client script error."
    time.sleep(1 / 4)
