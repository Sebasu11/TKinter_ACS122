from guizero import App, Text,Picture,TextBox
#from gpiozero import Buzzer

import time

#import RPi.GPIO as GPIO

import urllib
import json
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
 
PIN_1=23
PIN_2=24
PIN_3=12

#GPIO.setmode(GPIO.BCM)
#GPIO.setup(PIN_1, GPIO.OUT)
#GPIO.setup(PIN_2, GPIO.OUT)

#GPIO.setup(PIN_3, GPIO.OUT)
#buzzer = Buzzer(PIN_3)


#import os

#base_folder = os.path.dirname(__file__)
#image_path = os.path.join(base_folder, 'MotoCroos_love')

image_path="Logo.jpg"

#Para modificar los tiempos de espera

TimepoBienvenida=1000
TimepoError=2000
TimepoVuelvaPronto=1000

def OPEN():
	print("OPEN")		
	GPIO.output(PIN_1,1)
	app.after(1000,CLOSE)
		
def CLOSE():
	print("CLOSE")
	GPIO.output(PIN_1,0)
		
def OPEN2():
	print("OPEN2")		
	GPIO.output(PIN_2,1)
	app.after(1000,CLOSE2)
		
def CLOSE2():
	print("CLOSE2")		
	GPIO.output(PIN_2,0)


def bg_green():
	app.bg="#8BC900"
	space1.bg="#8BC900"
	space1.text_color="#8BC900"
	Text_Response.value="Bienvenido"
	app.after(TimepoBienvenida,bg_grey)
	
def bg_blue():
	app.bg="#1128D0"
	space1.bg="#1128D0"
	space1.text_color="#1128D0"
	Text_Response.value="Regresa pronto"
	app.after(TimepoVuelvaPronto,bg_grey)
	
def bg_grey():
	app.bg="gray"
	space1.bg="gray"
	space1.text_color="gray"
	buzzer.off()
	BARCODE.enable()
	Text_Response.value=""
	

def ScanBarcode(event):
	BARCODE.disable()
	scan=BARCODE.get()
	print("BarCode  "+scan)
	valido=URL(scan)
	if(valido == 1):
		OPEN()
		#Text_Response.value=""
	elif(valido == 2):
				print("OPEN 2 !")
				OPEN2()   
	BARCODE.clear()
		

def URL(Barcode):
	url= ("http://sebastianvzapivalidar.appsource.com.co/api/Entradas_V_0_1/?token=3&codigo="+Barcode)
	req = Request(url)
	try:
		response = urlopen(req)
		#print(response) 
		data = json.loads(response.read().decode('utf-8'))   
		print(data)

		if (data['value']==1):
			Text_Response.value="Bienvenido"
			bg_green()
			return 1
		elif(data['value']==2):
			Text_Response.value="Regesa Pronto"
			bg_blue()
			return 2
		elif(data['value']==3):
			Text_Response.value="No valida"
			app.bg="#DF541e"
			space1.bg="#DF541e"
			space1.text_color="#DF541e"
			buzzer.on()
			app.after(TimepoError,bg_grey)
			return 3
		else:
			Text_Response.value="No Existe"
			app.bg="#DF541e"
			space1.bg="#DF541e"
			space1.text_color="#DF541e"
			buzzer.on()
			app.after(TimepoVuelvaPronto,bg_grey)
			return 3


	except URLError as e:
		print(e.reason)
		#print(str(e.reason))
		if(str(e.reason)=='[Errno -3] Temporary failure in name resolution'):
			Text_Response.value="Sin Conexion a Internet"
			app.bg="#FFFF00"
			app.after(TimepoError,bg_grey)
			return False

		elif(e.reason=='Not Found'):
			Text_Response.value="Error 404"
			app.bg="#FFFF00"
			space1.bg="#FFFF00"
			space1.text_color="#FFFF00"
			app.after(TimepoError,bg_grey)
			return False
		else:
			Text_Response.value=e.reason
			app.bg="#FFFF00"
			space1.bg="#FFFF00"
			space1.text_color="#FFFF00"
			app.after(TimepoError,bg_grey)
			return False

app = App(title="Sebas",height=420,width=480,layout="grid",bg="gray")
#app = App(title="Sebas",height=420,width=480)

space1 = Text(app, text="aaaaaaa", size=20, grid=[0,0],color="gray",bg="gray")
logo = Picture(app, image=image_path, grid=[1,0])
logo.height=250
logo.width=250

space2 = Text(app, text="", size=10, grid=[1,1])
Text_Response = Text(app, text="", size=28, grid=[1,2], font="Times New Roman", color="black")

space3 = Text(app, text="", size=10, grid=[1,3])
BARCODE = TextBox(app, height=64, width=36, grid=[1,4])

BARCODE.focus()

BARCODE.tk.bind('<Key-Return>', ScanBarcode)

app.display()

