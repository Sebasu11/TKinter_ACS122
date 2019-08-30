from __future__ import print_function
from time import sleep

from smartcard.CardMonitoring import CardMonitor, CardObserver
from smartcard.util import *

# replace by your favourite apdu
AUTHENTICATE_NTAG213 = [0xFF, 0x00, 0x00, 0x00, 0x07, 0xD4, 0x42, 0x1B, 0xAA, 0xBB, 0xCC, 0xDD]

AUTHENTICATE_READER_MIFARE=[0xFF, 0x82, 0x00, 0x00, 0x06, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]

AUTHENTICATE_SECTOR_MIFARE = [0xFF, 0x86, 0x00, 0x00, 0x05, 0x01, 0x00, 0x05, 0x61, 0x00]

VERSION=[0x90, 0x60, 0x00, 0x00, 0x00]

READ_NTAG=[0xFF, 0xB0, 0x00, 0x04, 0x10]

#Read Sector 0, Block 1, 16 bytes
READ= [0xFF, 0xB0, 0x00, 0x04, 0x10]
#Read Sector 0, Block 2, 2 bytes
READ_2 = [0xFF, 0xB0, 0x00, 0x05, 0x02]


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
                print((card.atr[14]))
                if(card.atr[13]==0 and card.atr[14]==1):
                    response_r, sw1_r, sw2_r = card.connection.transmit(AUTHENTICATE_READER_MIFARE)
                    response_s, sw1_s, sw2_s = card.connection.transmit(AUTHENTICATE_SECTOR_MIFARE)
                    print (sw1_r,sw1_r)
                    print (sw1_s,sw2_s)
                    if (sw1_s==144 and sw2_s==0):
                        response_1, sw1_1, sw2_1 = card.connection.transmit(READ)
                        response_2, sw1_2, sw2_2 = card.connection.transmit(READ_2)
                        #print ('sw1 + sw2')
                        #print("%.2x %.2x" % (sw1_r, sw2_r))
                        print ('Response')
                        print (response_1)
                        print (response_2)
                    
                    else:
                        print('Authentication failed MIFARE')
                elif (card.atr[13]==0 and card.atr[14]==3):
                    print("VERSION NTAG")
                    
                    response_1, sw1_1, sw2_1 = card.connection.transmit(READ)
                    response_2, sw1_2, sw2_2 = card.connection.transmit(READ_2)
                    
                    response_1, sw1_1, sw2_1 = card.connection.transmit(READ_NTAG)
                    print ('Response')
                    print (response_1)
                    
                else:
                    print('Not allowed Card')

        for card in removedcards:
            print("-Removed: ", toHexString(card.atr))
            if card in self.cards:
                self.cards.remove(card)

if __name__ == '__main__':
    print("Insert or remove a smartcard in the system.")
    print("This program will exit in 100 seconds")
    print("")
    cardmonitor = CardMonitor()
    cardobserver = transmitobserver()
    cardmonitor.addObserver(cardobserver)

    sleep(100)