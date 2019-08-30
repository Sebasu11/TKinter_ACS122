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

# Default password is FF FF FF FF FF FF
AUTHENTICATE_READER=[0xFF, 0x82, 0x00, 0x00, 0x06, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]

# Authentica el sector del bloque 0x1F, es el que esta antes del 0x61
AUTHENTICATE_SECTOR_0 = [0xFF, 0x86, 0x00, 0x00, 0x05, 0x01, 0x00, 0x1F, 0x61, 0x00]

# Write 16 bytes in  block 29 -> 1C
WRITE_BLOCKS =   [0xFF, 0xD6, 0x00, 0x1C, 0x10] 
# Write 2 bytes in block 30 ->1D
WRITE_BLOCKS_2 = [0xFF, 0xD6, 0x00, 0x1D, 0x10]

WRITE_BLOCKS_NTAG_1 = [0xFF, 0xD6, 0x00, 0x1C, 0x04]
WRITE_BLOCKS_NTAG_2 = [0xFF, 0xD6, 0x00, 0x1D, 0x04]
WRITE_BLOCKS_NTAG_3 = [0xFF, 0xD6, 0x00, 0x1E, 0x04]
WRITE_BLOCKS_NTAG_4 = [0xFF, 0xD6, 0x00, 0x1F, 0x04]


# Posicion 4 es el bloque , l5 es el numero de bytes que boy a escribir, la pass son los ultimos 6 hex
PASSWORD_MIFARE = [0xFF, 0xD6, 0x00, 0x1F, 0x10, 0x00,0x00,0x00,0x00,0x00,0x00, 0xFF,0x0F,0x00,0x00, 0x0A,0x0B,0x0C,0x0D,0x0E,0x0F]
#PASSWORD = [0xFF, 0xD6, 0x00, 0x17, 0x10, 0x00,0x00,0x00,0x00,0x00,0x00, 0xFF,0x0F,0x00,0x00, 0xFF,0xFF,0xFF,0xFF,0xFF,0xFF]
#AUTHENTICATE_READER=[0xFF, 0x82, 0x00, 0x00, 0x06, 0x0A,0x0B,0x0C,0x0D,0x0E,0x0F]

PASSWORD_NTAG = [0xFF, 0x00, 0x00, 0x00, 0x07, 0xD4, 0x42, 0x1B, 0xAA, 0xBB, 0xCC, 0xDD]

#PASSWORD IS AA BB CC DD for NTAG213
SET_PWD_213 = [0xFF, 0xD6, 0x00, 0x2B, 0x04, 0xAA, 0xBB, 0xCC, 0xDD]
SET_PCK_213 = [0xFF, 0xD6, 0x00, 0x2C, 0x04, 0xAA, 0xBB, 00, 00]
SET_CF0_213 = [0xFF, 0xD6, 0x00, 0x29, 0x04, 0x00, 0x00, 0x00, 0x04]
SET_CF1_213 = [0xFF, 0xD6, 0x00, 0x2A, 0x04, 0x80, 0x05, 0x00, 0x00]

#PASSWORD IS AA BB CC DD for NTAG216
SET_PWD_216 = [0xFF, 0xD6, 0x00, 0xE5, 0x04, 0xAA, 0xBB, 0xCC, 0xDD]
SET_PCK_216 = [0xFF, 0xD6, 0x00, 0xE6, 0x04, 0xAA, 0xBB, 00, 00]
SET_CF0_216 = [0xFF, 0xD6, 0x00, 0xE3, 0x04, 0x00, 0x00, 0x00, 0x04]
SET_CF1_216 = [0xFF, 0xD6, 0x00, 0xE4, 0x04, 0x80, 0x05, 0x00, 0x00]

NTAG_PWD = True

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
        
        def set_password_MIFARE(self, command):
                print("Setting pass...")
                for iteration in range(1):
                        try:
                                response_s, value_s = self.send_command(AUTHENTICATE_SECTOR_0)
                                print(response_s)
                                response_p, value_p = self.send_command(PASSWORD_MIFARE)
                                print(response_p)
                                AUTHENTICATE_READER=[0xFF, 0x82, 0x00, 0x00, 0x06, 0x0A,0x0B,0x0C,0x0D,0x0E,0x0F]
                                response, value = self.send_command(AUTHENTICATE_READER)
                                print(response)
                                response_s, value_s = self.send_command(AUTHENTICATE_SECTOR_0)
                                print(response_s)
                                
                        except SystemError:
                                print ("Error setting password")
                        time.sleep(1)
                print("-----------OK-------------\n")
                return

        def set_password_NTAG213(self, command):
                print("Setting pass...")
                
                for iteration in range(1):
                        try:
                                response_s, value_s = self.send_command(SET_PWD_213)
                                print(response_s)
                                response_p, value_p = self.send_command(SET_PCK_213)
                                print(response_p)                                
                                response_s, value_s = self.send_command(SET_CF0_213)
                                print(response_s)
                                response_s, value_s = self.send_command(SET_CF1_213)
                                print(response_s)
                                
                        except SystemError:
                                print ("Error setting password")
                        time.sleep(1)
                print("-----------OK-------------\n")
                return

        def set_password_NTAG216(self, command):
                print("Setting pass...")
                
                for iteration in range(1):
                        try:
                                response_s, value_s = self.send_command(SET_PWD_216)
                                print(response_s)
                                response_p, value_p = self.send_command(SET_PCK_216)
                                print(response_p)                                
                                response_s, value_s = self.send_command(SET_CF0_216)
                                print(response_s)
                                response_s, value_s = self.send_command(SET_CF1_216)
                                print(response_s)

                                response_PWD, value_PWD = self.send_command(PASSWORD_NTAG)
                                print(response_PWD)

                        except SystemError:
                                print ("Error setting password")
                        time.sleep(1)
                print("-----------Finished-------------\n")
                return 


        def write_data_MIFARE(self, string):
                int_array = map(ord, string)
                print("Writing data: " + str(int_array))
                # If the string is greater than 18 characters, break.
                # Descomentar para set de contrasena 
                self.set_password_MIFARE(PASSWORD_MIFARE)
                
                if(len(int_array) > 18):
                        print ("Maximo 18 characters por ahora")
                        return 

                if(len(int_array) <= 0):
                        print (" Please provide a valid string.")
                        return 
                
                if(len(int_array)==18):
                        # Add the converted string to hex blocks to the APDU command.
                        for value in int_array[0:16]:
                                #print ('Value lenght : ' + str(value))
                                WRITE_BLOCKS.append(value)

                        for value2 in int_array[16:18]:
                                #print ('Value lenght 2 : ' + str(value2))
                                WRITE_BLOCKS_2.append(value2)

                if(len(int_array)<=16):
                        # Add the converted string to hex blocks to the APDU command.
                        for value in int_array[0:16]:
                                #print ('Value lenght : ' + str(value))
                                WRITE_BLOCKS.append(value)

                # Authenticate with the specified block with the APDU authenticate command.
                response_s, value_s = self.send_command(AUTHENTICATE_SECTOR_0)
                
                if(response_s == [144, 0]):
                        print("Authentication sector 0 successful.")

                        if(len(int_array) == 18):
                                print("Writing data 1" )
                                result1, value1=self.send_command(WRITE_BLOCKS)
                                print result1
                                print("Writing data 2" )
                                result2, value2=self.send_command(WRITE_BLOCKS_2)
                                print result2

                        if(len(int_array) <=16):
                                print("Writing data 1" )
                                result1, value1=self.send_command(WRITE_BLOCKS)
                                print result1
                                
                else:
                        print("Please provide a valid string.")


        def write_data_NTAG(self, string):
                int_array = map(ord, string)
                print("Writing data: " + str(int_array))
                # If the string is greater than 18 characters, break.
                # Descomentar para set de contrasena 
                #self.set_password_NTAG213(SET_PWD_213)
                #self.set_password_NTAG216(SET_PWD_216)

                if (NTAG_PWD==True):
                        response_P, sw1_P = self.send_command(PASSWORD_NTAG)
                
                if(len(int_array) > 18):
                        print ("Maximo 18 characters por ahora")
                        return 

                if(len(int_array) <= 0):
                        print (" Please provide a valid string.")
                        return 
                
                if(len(int_array)==18):
                        # Add the converted string to hex blocks to the APDU command.
                        for value in int_array[0:16]:
                                #print ('Value lenght : ' + str(value))
                                WRITE_BLOCKS.append(value)

                        for value2 in int_array[16:18]:
                                #print ('Value lenght 2 : ' + str(value2))
                                WRITE_BLOCKS_2.append(value2)

                        print("Writing in NTAG data 1" )
                        result1, value1=self.send_command(WRITE_BLOCKS_NTAG_1)
                        result2, value2=self.send_command(WRITE_BLOCKS_NTAG_2)
                        result3, value3=self.send_command(WRITE_BLOCKS_NTAG_3)
                        result4, value4=self.send_command(WRITE_BLOCKS_NTAG_4)
                        result5, value5=self.send_command(WRITE_BLOCKS_2)
                        

                if(len(int_array)<=16):
                        # Add the converted string to hex blocks to the APDU command.
                        index=0
                        for value in int_array[0:16]:
                                #print ('Value lenght : ' + str(value))
                                
                                if(index>=0 and index<4):
                                        WRITE_BLOCKS_NTAG_1.append(value)
                                if(index>=4 and index<8):
                                        WRITE_BLOCKS_NTAG_2.append(value)
                                if(index>=8 and index<12):
                                        WRITE_BLOCKS_NTAG_3.append(value)
                                if(index>=12 and index<16):
                                        WRITE_BLOCKS_NTAG_4.append(value)
                                index=index+1

                        print("Writing in NTAG data 1" )
                        result1, value1=self.send_command(WRITE_BLOCKS_NTAG_1)
                        result2, value2=self.send_command(WRITE_BLOCKS_NTAG_2)
                        result3, value3=self.send_command(WRITE_BLOCKS_NTAG_3)
                        result4, value4=self.send_command(WRITE_BLOCKS_NTAG_4)
                                
                                
                

                print result1,result2,result3,result4
                                

if __name__ == '__main__':
        # 1. Create an NFC_Reader
        reader = NFC_Reader()

        #reader.write_data("223620180601135923")
        reader.write_data_NTAG("ABCabc1234")
        #reader.write_data_MIFARE("DEFdef5678")
        #reader.write_data_MIFARE("GHIghi9012")
        #reader.write_data_NTAG("GHIghi9012")
        
        # Read the data blocks to verify they were written correctly.
        #value, value2 = reader.read_data()
        
