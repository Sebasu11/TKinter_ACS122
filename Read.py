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

'''
RFID/NFC Reader/Writer: ACR122U-A9
Supported Frequency: 13.56MHz
Supported ISO: 14443-4A/B, ISO 18092.
Additional Supported Standards: Mifare, FeliCa, four types of NFC.
Documentation: http://downloads.acs.com.hk/drivers/en/API-ACR122U-2.02.pdf
Definitions:
ISO/IEC 14443 Identification cards -- Contactless integrated circuit cards -- Proximity cards is an international standard that defines proximity cards used for identification, and the transmission protocols for communicating with it.
(ATR) Answer To Reset: is a message output by a contact Smart Card conforming to ISO/IEC 7816 standards, following electrical reset of the card's chip by a card reader.
PCD: proximity coupling device (the card reader)
PICC: proximity integrated circuit card
'''
VERBOSE = False

attributes = {
	SCARD_ATTR_ATR_STRING: 'SCARD_ATTR_ATR_STRING',
	SCARD_ATTR_CHANNEL_ID: 'SCARD_ATTR_CHANNEL_ID',
	SCARD_ATTR_CHARACTERISTICS: 'SCARD_ATTR_CHARACTERISTICS',
	SCARD_ATTR_CURRENT_BWT: 'SCARD_ATTR_CURRENT_BWT',
	SCARD_ATTR_CURRENT_CWT: 'SCARD_ATTR_CURRENT_CWT',
	SCARD_ATTR_CURRENT_EBC_ENCODING: 'SCARD_ATTR_CURRENT_EBC_ENCODING',
	SCARD_ATTR_CURRENT_F: 'SCARD_ATTR_CURRENT_F',
	SCARD_ATTR_CURRENT_IFSC: 'SCARD_ATTR_CURRENT_IFSC',
	SCARD_ATTR_CURRENT_IFSD: 'SCARD_ATTR_CURRENT_IFSD',
	SCARD_ATTR_CURRENT_IO_STATE: 'SCARD_ATTR_CURRENT_IO_STATE',
	SCARD_ATTR_DEFAULT_DATA_RATE: 'SCARD_ATTR_DEFAULT_DATA_RATE',
	SCARD_ATTR_DEVICE_FRIENDLY_NAME_A: 'SCARD_ATTR_DEVICE_FRIENDLY_NAME_A',
	SCARD_ATTR_DEVICE_FRIENDLY_NAME_W: 'SCARD_ATTR_DEVICE_FRIENDLY_NAME_W',
	SCARD_ATTR_DEVICE_SYSTEM_NAME_A: 'SCARD_ATTR_DEVICE_SYSTEM_NAME_A',
	SCARD_ATTR_DEVICE_SYSTEM_NAME_W: 'SCARD_ATTR_DEVICE_SYSTEM_NAME_W',
	SCARD_ATTR_DEVICE_UNIT: 'SCARD_ATTR_DEVICE_UNIT',
	SCARD_ATTR_ESC_AUTHREQUEST: 'SCARD_ATTR_ESC_AUTHREQUEST',
	SCARD_ATTR_EXTENDED_BWT: 'SCARD_ATTR_EXTENDED_BWT',
	SCARD_ATTR_ICC_INTERFACE_STATUS: 'SCARD_ATTR_ICC_INTERFACE_STATUS',
	SCARD_ATTR_ICC_PRESENCE: 'SCARD_ATTR_ICC_PRESENCE',
	SCARD_ATTR_ICC_TYPE_PER_ATR: 'SCARD_ATTR_ICC_TYPE_PER_ATR',
	SCARD_ATTR_MAXINPUT: 'SCARD_ATTR_MAXINPUT',
	SCARD_ATTR_MAX_CLK: 'SCARD_ATTR_MAX_CLK',
	SCARD_ATTR_MAX_DATA_RATE: 'SCARD_ATTR_MAX_DATA_RATE',
	SCARD_ATTR_POWER_MGMT_SUPPORT: 'SCARD_ATTR_POWER_MGMT_SUPPORT',
	SCARD_ATTR_SUPRESS_T1_IFS_REQUEST: 'SCARD_ATTR_SUPRESS_T1_IFS_REQUEST',
	SCARD_ATTR_USER_AUTH_INPUT_DEVICE: 'SCARD_ATTR_USER_AUTH_INPUT_DEVICE',
	SCARD_ATTR_USER_TO_CARD_AUTH_DEVICE:
		'SCARD_ATTR_USER_TO_CARD_AUTH_DEVICE',
	SCARD_ATTR_VENDOR_IFD_SERIAL_NO: 'SCARD_ATTR_VENDOR_IFD_SERIAL_NO',
	SCARD_ATTR_VENDOR_IFD_TYPE: 'SCARD_ATTR_VENDOR_IFD_TYPE',
	SCARD_ATTR_VENDOR_IFD_VERSION: 'SCARD_ATTR_VENDOR_IFD_VERSION',
	SCARD_ATTR_VENDOR_NAME: 'SCARD_ATTR_VENDOR_NAME',
}

AUTHENTICATE_READER=[0xFF, 0x82, 0x00, 0x00, 0x06, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
#AUTHENTICATE_READER=[0xFF, 0x82, 0x00, 0x00, 0x06, 0x0A,0x0B,0x0C,0x0D,0x0E,0x0F]


# Modificar el bloque del sector para autentificar , es el que esta antes del 0x61
AUTHENTICATE_SECTOR_0 = [0xFF, 0x86, 0x00, 0x00, 0x05, 0x01, 0x00, 0x1F, 0x61, 0x00]

READ_BLOCKS_RECENTLY_UPDATED = [0xFF, 0xB0, 0x00, 0x1C, 0x10]
READ_BLOCKS_RECENTLY_UPDATED_2 = [0xFF, 0xB0, 0x00, 0x1D, 0x02]

Read = 10

class NFC_Reader():
	def __init__(self, uid = ""):
		self.uid = uid
		self.hresult, self.hcontext = SCardEstablishContext(SCARD_SCOPE_USER)
		self.hresult, self.readers = SCardListReaders(self.hcontext, [])
		assert len(self.readers) > 0
		self.reader = self.readers[0]
		print("Found reader: " +  str(self.reader))
		
		self.hresult, self.hcard, self.dwActiveProtocol = SCardConnect(
				self.hcontext,
				self.reader,
				SCARD_SHARE_SHARED,
				SCARD_PROTOCOL_T0 | SCARD_PROTOCOL_T1)
		self.data_blocks = []
		response, value = self.send_command(AUTHENTICATE_READER)

	def send_command(self, command):
		#print("Sending command...")
		for iteration in range(1):
			try:
				self.hresult, self.response = SCardTransmit(self.hcard,self.dwActiveProtocol,command)
				value = toHexString(self.response, format=0)
				if(VERBOSE):
					print("Value: " + value +  " , Response:  " + str(self.response) + " HResult: " + str(self.hresult))
			except SystemError:
				print ("No Card Found")
			time.sleep(1)
		#print("------------------------\n")
		return self.response, value
	def read_data(self):
		response, value = self.send_command(AUTHENTICATE_SECTOR_0)
		#print("Reading data from card...")
		#print (response)
		if(response == [144, 0]):
			print("Authentication  successful.")
			result, value = self.send_command(READ_BLOCKS_RECENTLY_UPDATED)
			result_2, value_2 = self.send_command(READ_BLOCKS_RECENTLY_UPDATED_2)
			return result, result_2
		else:
			print("Please provide a valid string.")
		#else:
		#	print("Unable to authenticate.")

	def print_data(self,value,value2):
		code =''
		code2=''

		for byte8 in range(0,16):
			code = code + str(unichr(value[byte8]))
			#print code

		for byte8 in range(0,2):
			code2 = code2 + str(unichr(value2[byte8]))
			
		return code+code2
		
	def print_data(self,value):
		code =''
		for byte8 in range(0,10):
			code = code + str(unichr(value[byte8]))
			#print code
		return code
		

if __name__ == '__main__':
	# 1. Create an NFC_Reader
	reader = NFC_Reader()


	# 2. Read the data from the card.
	if(Read==10):
		value=reader.read_data()
		print value
		code=reader.print_data(value[0])
		print "Code is : " + code

	if(Read==18):
		value, value2 = reader.read_data()
		code=reader.print_data(value,value2)
		print "Code is : " + code
