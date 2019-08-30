#Librerias NFC
#--------------------------------

from __future__ import print_function
from time import sleep

from smartcard.CardMonitoring import CardMonitor, CardObserver
from smartcard.util import *

from smartcard.scard import *
from smartcard.util import toHexString
import smartcard.util
from smartcard.ATR import ATR
from smartcard.CardType import AnyCardType
from smartcard.CardRequest import CardRequest
from smartcard.CardConnectionObserver import CardConnectionObserver
import time
import struct
import array

Read=10

#AUTHENTICATE_READER=[0xFF, 0x82, 0x00, 0x00, 0x06, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
AUTHENTICATE_READER=[0xFF, 0x82, 0x00, 0x00, 0x06, 0x0A,0x0B,0x0C,0x0D,0x0E,0x0F]

AUTHENTICATE_SECTOR_0 = [0xFF, 0x86, 0x00, 0x00, 0x05, 0x01, 0x00, 0x1F, 0x61, 0x00]

#Read Sector 0, Block 1, 16 bytes
READ= [0xFF, 0xB0, 0x00, 0x1C, 0x10]
#Read Sector 0, Block 2, 2 bytes
READ_2 = [0xFF, 0xB0, 0x00, 0x1D, 0x02]

PASSWORD_NTAG = [0xFF, 0x00, 0x00, 0x00, 0x07, 0xD4, 0x42, 0x1B, 0xAA, 0xBB, 0xCC, 0xDD]

NTAG_PWD = True

def print_data(value,value2):
    code =''
    code2=''
    if (len(value)!=16 or len(value2)!=2):
        return
    for byte8 in range(0,16):
        code = code + str(unichr(value[byte8]))
        #print (code)
    for byte8 in range(0,2):
        code2 = code2 + str(unichr(value2[byte8]))
        #print (code2)

    return code+code2

def print_data(value):
		code =''
		for byte8 in range(0,10):
			code = code + str(unichr(value[byte8]))
			#print code
		return code
#--------------------------------
#librerias GUI y GPIO
#--------------------------------
import Tkinter as tk
from Tkinter import *
from PIL import ImageTk, Image

#from gpiozero import Buzzer

import time

#import RPi.GPIO as GPIO

import urllib2
import json
from urllib2 import urlopen
from urllib2 import URLError, HTTPError
 
PIN_1=23
PIN_2=24
PIN_3=12

#GPIO.setmode(GPIO.BCM)
#GPIO.setup(PIN_1, GPIO.OUT)
#GPIO.setup(PIN_2, GPIO.OUT)

#GPIO.setup(PIN_3, GPIO.OUT)
#buzzer = Buzzer(PIN_3)


import os

base_folder = os.path.dirname(__file__)
image_path = os.path.join(base_folder, 'Inicial')
image_path2 = os.path.join(base_folder, 'Valida')
image_path3 = os.path.join(base_folder, 'NoValida')
image_path4 = os.path.join(base_folder, 'Regrese')
image_path5 = os.path.join(base_folder, 'Error')
image_path6 = os.path.join(base_folder, 'Naranja')

#image_path="Inicial"
#image_path2="Valida"
#image_path3="NoValida"
#image_path4="Regrese"
#image_path5="Error"
#image_path6="Naranja"

#Para modificar los tiempos de espera

HIGH = 1
LOW=0

TimepoBienvenida=1000
TimepoError=1000
TimepoVuelvaPronto=1000
TiempoAbierto = 1000

def OPEN():
        print("OPEN")           
        #GPIO.output(PIN_1,HIGH)
        app.after(TiempoAbierto,CLOSE)
                
def CLOSE():
        print("CLOSE")
        #GPIO.output(PIN_1,LOW)
                
def OPEN2():
        print("OPEN2")          
        #GPIO.output(PIN_2,HIGH)
        app.after(TiempoAbierto,CLOSE2)
                
def CLOSE2():
        print("CLOSE2")         
        GPIO.output(PIN_2,LOW)

def bg_valida():
        img = ImageTk.PhotoImage(Image.open(image_path2))
        panel.configure(image=img)
        panel.photo = img
        app.after(TimepoBienvenida,bg_ini)
        
def bg_regrese():
        img = ImageTk.PhotoImage(Image.open(image_path4))
        panel.configure(image=img)
        panel.photo = img
        app.after(TimepoVuelvaPronto,bg_ini)

def bg_novalido():
        img = ImageTk.PhotoImage(Image.open(image_path3))
        panel.configure(image=img)
        panel.photo = img
        #buzzer.on()
        app.after(TimepoVuelvaPronto,bg_ini)
def bg_nopuede():
        img = ImageTk.PhotoImage(Image.open(image_path6))
        panel.configure(image=img)
        panel.photo = img
        buzzer.on()
        app.after(TimepoVuelvaPronto,bg_ini)

def bg_error():
        img = ImageTk.PhotoImage(Image.open(image_path5))
        panel.configure(image=img)
        panel.photo = img
        app.after(TimepoVuelvaPronto,bg_ini)
        
def bg_ini():
        img = ImageTk.PhotoImage(Image.open(image_path))
        panel.configure(image=img)
        panel.photo = img
        #buzzer.off()
        BARCODE.config(state='normal')
        
def ScanBarcode(event):
        BARCODE.config(state='disabled')
        scan=BARCODE.get()
        print("BarCode  "+scan)
        valido=URL(scan)
        if(valido == 1):
                OPEN()
        elif(valido == 2):
                OPEN2()   
        BARCODE.config(state='normal')
        BARCODE.delete(0, 'end')

def NFCcode(string):
        NFC=string
        #print("NFC Code  "+NFC)
        valido=URL(NFC)
        if(valido == 1):
                OPEN()
        elif(valido == 2):
                OPEN2()   
                

def URL(Barcode):
        url= ("http://sebastianvzapivalidar.appsource.com.co/api/Entradas_V_0_1/?token=3&codigo="+Barcode)
        #req = Request(url)
        print (url)
        try:
                #response = urlopen(req)
                response = urlopen(url)
                data = json.loads(response.read().decode('utf-8'))   
                if (data['value']==1):
                        bg_valida()
                        return 1
                elif(data['value']==2):
                        bg_regrese()
                        return 2
                elif(data['value']==3):
                        bg_novalido()
                        return 3
                elif(data['value']==4):
                        bg_nopuede()
                        return 4
                else:
                        bg_novalido()
                        return 3

        except URLError as e:
                print(e.reason)
                print(str(e.reason))
                if(str(e.reason)=='[Errno -3] Temporary failure in name resolution'):
                        #Text_Response.value="Sin Conexion a Internet"
                        print('Sin Conexion a Internet0')
                        bg_error()
                        return False

                elif(e.reason=='Not Found'):
                        #Text_Response.value="Error 404"
                        print('Error 404')
                        bg_error()
                        return False
                else:
                        #Text_Response.value=e.reason
                        print('Error')
                        bg_novalido()
                        return False

app = tk.Tk()
app.title('Verficador')
app.attributes("-fullscreen",True)

img = ImageTk.PhotoImage(Image.open(image_path))
panel = tk.Label(app, image = img)
panel.place(x=0,y=0)

BARCODE = Entry(app,bd=4)
BARCODE.place(x=175,y=250)

BARCODE.focus()

BARCODE.bind('<Key-Return>', ScanBarcode)

#app.mainloop()

class transmitobserver(CardObserver):
    """A card observer that is notified when cards are inserted/removed
    from the system, connects to cards and SELECT DF_TELECOM """

    def __init__(self):
        self.cards = []

    def update(self, observable, actions):
        (addedcards, removedcards) = actions
        for card in addedcards:
            if card not in self.cards:
                self.cards += [card]
                print("+Inserted: ", toHexString(card.atr))
                card.connection = card.createConnection()
                card.connection.connect()
                if(card.atr[13]==0 and card.atr[14]==1):
                	response_r, sw1_r, sw2_r = card.connection.transmit(AUTHENTICATE_READER)
                	response_s, sw1_s, sw2_s = card.connection.transmit(AUTHENTICATE_SECTOR_0)
                	if (sw1_s==144 and sw2_s==0):
                		response_1, sw1_1, sw2_1 = card.connection.transmit(READ)
                    	response_2, sw1_2, sw2_2 = card.connection.transmit(READ_2)
                    	#print ('sw1 + sw2')
                    	#print("%.2x %.2x" % (sw1_r, sw2_r))
                    	print ('Response')
                    	print (response_1)
                    	print ('Response 2')
                    	print (response_2)
                    	if(Read==18):
                    		try:
                    			Tag=print_data(response_1,response_2)
                    			print ("Code is : " + Tag)
                    			NFCcode(Tag)
                    		except:
                    			print("Error Reading MIFARE 18")
                    			bg_novalido()

                    	if(Read==10):
                    		try:
                    			Tag=print_data(response_1)
                           		print ("Code is : " + Tag)
                           		NFCcode(Tag)
                    		except:
                    			print("Error Reading MIFARE 16")
                    			bg_novalido()
                elif (card.atr[13]==0 and card.atr[14]==3):
                    print("VERSION NTAG")

                    if (NTAG_PWD==True):
                    	response_P, sw1_P, sw2_P = card.connection.transmit(PASSWORD_NTAG)

                    
                    response_1, sw1_1, sw2_1 = card.connection.transmit(READ)
                    response_2, sw1_2, sw2_2 = card.connection.transmit(READ_2)

                    print ('Response')
                    print (response_1)

                    if(Read==18):
                    	try:
                    		Tag=print_data(response_1,response_2)
                    		print ("Code is : " + Tag)
                    		NFCcode(Tag)
                    	except:
                    		print("Error Reading NTAG 18")
                    		bg_novalido()

                    if(Read==10):
                    	try:
                    		Tag=print_data(response_1)
                           	print ("Code is : " + Tag)
                           	NFCcode(Tag)
                    	except:
                    		print("Error Reading 16")
                    		bg_novalido()
                    
                else:
                    print('Not allowed Card')
                    bg_novalido()                
        for card in removedcards:
            print("-Removed: ", toHexString(card.atr))
            if card in self.cards:
                self.cards.remove(card)

if __name__ == '__main__':

    print("Insert or remove a smartcard in the system.")
    print("This program will exit in 10 days")
    print("")

    cardmonitor = CardMonitor()
    cardobserver = transmitobserver()
    cardmonitor.addObserver(cardobserver)
    app.mainloop()

    sleep(1000000)

        #app.update_idletasks()
        #app.update()
        #print("Insert or remove a smartcard in the system.")
        #cardmonitor = CardMonitor()
        #cardobserver = transmitobserver()
        #cardmonitor.addObserver(cardobserver)
        
