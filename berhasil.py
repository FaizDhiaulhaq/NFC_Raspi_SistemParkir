#!/usr/bin/env python
import time
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import re
from gpiozero import Buzzer
import requests
pinBuzzer = 27                      #pin buzzer
pinServo = 21                       #pin servo
TRIG1 = 18                          #pin trig HCSR-04
ECHO1 = 24                          #pin ECHO HCSR-04
GPIO.setwarnings(False)
GPIO.cleanup()
GPIO.setmode(GPIO.BCM)
GPIO.setup(pinServo, GPIO.OUT)
GPIO.setup(pinBuzzer, GPIO.OUT)
GPIO.setup(TRIG1, GPIO.OUT)
GPIO.setup(ECHO1, GPIO.IN)
p = GPIO.PWM(pinServo, 50)
p.start(2.5)
API_ENDPOINT = "http://192.168.0.129:8000/api/parkir"

def read_RFID():                    #pembacaan RFID
    reader = SimpleMFRC522()
    id, text = reader.read()
    time.sleep(0.75)
    print(id)
    return id


def unlock_gate():                  #membuka Gerbang
    p.ChangeDutyCycle(7.5)

    
def lock_gate():                    #menutup Gerbang
    p.ChangeDutyCycle(2.5)
 
def jarak():                        #source code HCSR-04 membaca jarak
    gerbang = True
    while gerbang :
        GPIO.output(TRIG1, False)
        #print ("Waiting For Sensor1 To Settle") 
        time.sleep(.1)
        GPIO.output(TRIG1, True)
        time.sleep(0.00001)
        GPIO.output(TRIG1, False)

        while GPIO.input(ECHO1) == 0:
            pass
            pulse_start1 = time.time()
             
        while GPIO.input(ECHO1) == 1:
            pass
            pulse_end1 = time.time()

        pulse_duration1 = pulse_end1 - pulse_start1

        distance1 = pulse_duration1 * 17150
        distance1= round(distance1, 2)
        print ("Distance1:",distance1, "cm")
        time.sleep(0.5)
        if distance1 < 6 :
            lock_gate()
            gerbang = False
            print("Tutup")
            

def beep():                     #source code membunyikan buzzer
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pinBuzzer, GPIO.OUT)
    GPIO.output(pinBuzzer,GPIO.HIGH)
    time.sleep(0.5)
    GPIO.output(pinBuzzer,GPIO.LOW)

try :
    while True:
        output = read_RFID()                                #RFID membaca kartu
        print("No Kartu : {}".format(output))               #menampilkan nomor kartu pembacaan RFID
        data = {'nomor_kartu': output}                      #data nomor kartu yang diikirm ke API
        r = requests.post(url = API_ENDPOINT, data = data)  #request data dari API endpoint
        response = r.json()                                 #mengambil data dari API dalam bentuk json
        if response['error'] != True :                      #jika respons tidak error maka menjalankan perintah selanjutnya
            print(response['message'])                      #mencatak respons dari API
            beep()                                          #menjalankan perintah bunyikan buzzer
            unlock_gate()                                   #menjalankan perintah buka gerbang
            print("buka")                                   #menampilkan tulisan buka gerbang
            jarak()                                         #menjalankan perintah pembacaan jarak HCSR-04
        print(response['message'])                          #menampilkan pesan respons dari API
        time.sleep(2)                                       #dellay proses selama 2 detik
except KeyboardInterrupt:                                   #menjalan kan perintah ketika menekan "ctrl+c"
    p.stop()                                                #memnghentikan proses
    GPIO.cleanup()                                          #membersihkan perintah yang ada pada GPIO
 
finally :
    p.stop()
    GPIO.cleanup()
