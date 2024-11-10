#!/usr/bin/env python3

"""

This process controls the light strings mounted under the hood.   Specifically, it
communicates with the Pico that does the real work.

There are 417 lights under the hood



       143 * *  144
          *   *
         *     *
        *       * 
       *         *
      *           *
     *             * 
     *  **********  *  287
    0  417     288



Modes for this process

Hood light

Charging indicator

LED 417   Red == No Signal, Green = 200V
LED 416   Red = 'OBC_Charge_Status': 'Plugged in waiting on timer',



Demo/light show

    lights move as it revs



"""

"""
from   helper.hlpApp import HlpApp
from   helper.sysIds import SysMessageIds
from   msgIds        import MessageIds, HelperIds
from   msgIds        import ProjParms as pps
import pandas as pd
import os, serial, socket, sys

from helper.hlpMsgBuffer import HlpMsgBuffer
from helper.hlpSocks     import HlpSocket
from helper.hlpMsg       import HlpMsg
import cantools
"""

import serial

import random


class UnderHoodLights1():
    """
    """


    def __init__(self):

        #helperName = HelperIds.LIGHTS_1
        #super().__init__(helperName, options)

        #self.parmCarMode = pps.CAR_MODE
        #self.parmSubscribe(self.parmCarMode)
        #self.parmCarMode.setCallbackOnUpdate(self.updateDirection)
        self.carMode = 'unknown'



        self.replyBuff = bytearray(1024)
        self.replyBuffIdx = 0
        self.seenStartChar = False
        self.seenEndChar = False
        self.bytesRecieved = 0
        self.numZeroReads  = 0
        self.lastCarMode = '?'

        self.nextToSend   = None
        self.readyToSend  = False
        self.repeatSend   = False
        self.pattern      = None

        self.openSerialPort()

        self.pat1PatIdx = 0
        self.pat1Offset = 0

        self.pattern1Dict = {}
        self.pattern1Dict[0] = dict(red =   5, green =   0, blue =   0, numDots = 5, base =   0, offset = 0)
        self.pattern1Dict[1] = dict(red =   0, green =   0, blue =   0, numDots = 5, base =   5, offset = 0)
        self.pattern1Dict[2] = dict(red =   0, green =   5, blue =   0, numDots = 5, base =  10, offset = 0)
        self.pattern1Dict[3] = dict(red =   0, green =   0, blue =   0, numDots = 5, base =  15, offset = 0)
        self.pattern1Dict[4] = dict(red =   0, green =   0, blue =   5, numDots = 5, base =  20, offset = 0)
        self.pattern1Dict[5] = dict(red =   0, green =   0, blue =   0, numDots = 5, base =  25, offset = 0)


        self.chargerCanIds = {0x390: 'pdm', 0x393 : 'statusBits', 0x679 : 'wakeUp', 0x1F2 : 'chargePower' }
        self.chargerDict = {'Unknown_393_1': None, 'Unknown_393_1Dt': None,  'Unknown_393_4': None, 'Unknown_393_4Dt': None, 'OBC_Charge_Power': None, 'OBC_Status_AC_Voltage': None, 'OBC_Flag_QC_Relay_On_Announcemen': None,
                            'OBC_Charge_Status': None, 'OBC_Flag_QC_IR_Sensor': None, 'OBC_Maximum_Charge_Power_Out': None, 'CommandedChargePower': None, 'dt' : None}
        self.ivtsCanIds = {0x521 : 'current', 0x522 : 'voltsU1', 0x525 : 'Temperature', 0x526 : 'Watts',  0x1da : 'Motor stats'}
        self.ivtsDict = dict(hv = 0.0, current = 0.0, lastRpm = 0)


        #self.dbc = cantools.database.Database()
        #self.dbc.add_dbc_file('/home/eMiata/ecar/eve1/data/EV-can_AZE0.dbc')
        #self.dbc.add_dbc_file('/home/eMiata/ecar/eve1/data/IVT-S_12082020.dbc')

        #self.motorPubPortNum   = options.motorCanPubPortNum
        #self.motorPubHost      = options.motorCanPublishHost
        #self.chargerPubPortNum = options.chargerCanPubPortNum
        #self.chargerPubHost    = options.chargerCanPublishHost
        self.lastRpm           = 0

        #self.initMotorCanSocket()
        #self.initChargerCanSocket()


    def openSerialPort(self):
        """
        """

        self.ser = serial.Serial('/dev/cu.usbmodem1424201', baudrate=115200)
        #self.hlpMsg.addInput(self.ser.fileno(), self.serialDataReady)


    def serialDataReady(self):
        """
        """
        numBytesAvail = self.ser.in_waiting
        if numBytesAvail == 0: 
#            import pdb; pdb.set_trace() # this shouldn't happen, something wrong with serial driver. but it does happen.  Ignore and go on with life..
            self.numZeroReads  += 1
            return

        self.bytesRecieved += numBytesAvail
        #startReadTime = pd.Timestamp.now()
        theBytes = self.ser.read(numBytesAvail)
        #endReadTime = pd.Timestamp.now()
        #diffTime = endReadTime - startReadTime
        #if diffTime.total_seconds() > .05:
        #    self.stalledRead  += 1 

        for eachByte in theBytes:
            self.processSerialByte(eachByte) 

    def processSerialByte(self, aByte):
        """
        """
        
        print('%d, %c'%(aByte, aByte))
        self.replyBuff[self.replyBuffIdx] = aByte
        if not self.seenStartChar:
            if aByte == ord('$'):
                self.seenStartChar = True
                self.replyBuffIdx += 1
                print('Saw $')
            else:
                print('Still looking for start char')
                pass
            return

        else:
            self.replyBuffIdx += 1
#            print('adding Char to buff')

        if not self.seenEndChar:
            if aByte == ord('\n') or aByte == ord('\r'):
                self.seenEndChar = True
                self.processReply()

    def processReply(self):
        """
        """
        print("process Reply")
        text = self.replyBuff[0:self.replyBuffIdx].decode()
        text = text.rstrip('\r\n')
        print(text)
        self.seenEndChar = False
        self.seenStartChar = False
        self.replyBuffIdx = 0
        self.replyBuff = bytearray(1024)
        if text == '$OK':
            self.readyToSend = True
            print("Ready for next msg")
            if self.repeatSend:
                self.sendNext()

        else:
            print(text)
            #            import pdb; pdb.set_trace()
            pass


    def sendNext(self):
        """
        """

        print("Send next")

        self.nextToSend = None

        if self.lastCarMode == 'charge':
            if self.chargerDict['OBC_Status_AC_Voltage'] == 'No Signal':
                toSend = '$range,%d,%d,%d,%d,%d'%(417, 1, 0, 50, 0 )
            elif self.chargerDict['OBC_Status_AC_Voltage'] == '200V':
                toSend = '$range,%d,%d,%d,%d,%d'%(417, 1, 50, 0, 0 )
            else:
                toSend = '$range,%d,%d,%d,%d,%d'%(417, 1, 0, 0, 50 )

            toSend += '\n'
            bytesToSend = toSend.encode('utf-8')
            #print("sending Charge status bytes")
            #print(bytesToSend)
            ret = self.ser.write(bytesToSend)
            #print(ret)


            return


        if self.pattern == 1:
            self.doNextPatternOne()
            self.readyToSend = False


        elif self.pattern == 2:

            chanceOfDark = random.randint(0,100)
            if chanceOfDark < 30:
                toSend = '$range,%d,%d,%d,%d,%d'%(random.randint(0,410), random.randint(1,5), 0, 0, 0 )
            elif chanceOfDark >=30 and chanceOfDark < 35: # green
                toSend = '$range,%d,%d,%d,%d,%d'%(random.randint(0,410), random.randint(1,5), random.randint(20,255), 0,  0 )
            elif chanceOfDark >=35 and chanceOfDark < 40: # red
                toSend = '$range,%d,%d,%d,%d,%d'%(random.randint(0,410), random.randint(1,5), 0, random.randint(20,255),  0 )
            elif chanceOfDark >=40 and chanceOfDark < 45: # blue
                toSend = '$range,%d,%d,%d,%d,%d'%(random.randint(0,410), random.randint(1,5), 0, 0, random.randint(20,255) )
            elif chanceOfDark >=45 and chanceOfDark < 50: # red & green
                toSend = '$range,%d,%d,%d,%d,%d'%(random.randint(0,410), random.randint(1,5), random.randint(20,255), random.randint(20,255), 0 )
            elif chanceOfDark >=50 and chanceOfDark < 55: # green & blue
                toSend = '$range,%d,%d,%d,%d,%d'%(random.randint(0,410), random.randint(1,5), random.randint(20,255), 0, random.randint(20,255) )
            elif chanceOfDark >=55 and chanceOfDark < 60: # red & blue
                toSend = '$range,%d,%d,%d,%d,%d'%(random.randint(0,410), random.randint(1,5), 0, random.randint(20,255), random.randint(20,255) )
            elif chanceOfDark >=60 and chanceOfDark < 70: # more green
                toSend = '$range,%d,%d,%d,%d,%d'%(random.randint(0,410), random.randint(1,5), random.randint(20,255), 0,  0 )

            else:
                toSend = '$range,%d,%d,%d,%d,%d'%(random.randint(0,410), random.randint(1,5), random.randint(0,255), random.randint(0,255), random.randint(0,255) )

            toSend += '\n'
            bytesToSend = toSend.encode('utf-8')

#            print("sending bytes")
#            print(bytesToSend)
            ret = self.ser.write(bytesToSend)
            print(ret)

        elif self.pattern == 3:

            perc = int(self.lastRpm/100)
            if perc > 100:
                perc = 100
            toSend = '$meter,%d'%(perc) 

            toSend += '\n'
            bytesToSend = toSend.encode('utf-8')

            #print("sending bytes")
            #print(bytesToSend)
            ret = self.ser.write(bytesToSend)
            #print(ret)




    def doNextPatternOne(self):
        """
        """

#        import pdb; pdb.set_trace()

        #print("doNextPatternOne")

        retDict = self.pattern1Dict[self.pat1PatIdx]
        self.pat1PatIdx += 1
        if self.pat1PatIdx >= len(self.pattern1Dict):
            self.pat1PatIdx = 0

        endPix = retDict['base'] + retDict['offset'] + retDict['numDots']
        if endPix > 417:
            #print("reached end of pixels, handle this")
            if retDict['base'] + retDict['offset'] >= 417:
                retDict['offset'] = 0
            else:
                retDict['offset'] += 1  # we have to move it forward
                bytesToSend = self.setRangeMsg(0, 1, random.randint(0,255), random.randint(0,255), random.randint(0,255) )
                ret = self.ser.write(bytesToSend)
                self.nextToSend = bytesToSend


                return


        
        bytesToSend = self.setRangeMsg(retDict['base'] + retDict['offset'], retDict['numDots'], retDict['red'], retDict['green'], retDict['blue'] )
        ret = self.ser.write(bytesToSend)
        self.nextToSend = bytesToSend
        retDict['offset'] += 1



    def updateDirection(self):
        """
        """

        self.lastCarMode = self.parmCarMode.data['theMode']
        #print("Got a new carMode, %s"%(self.lastCarMode))

        if self.lastCarMode == 'charge':
            if self.chargerDict['OBC_Status_AC_Voltage'] == 'No Signal':
                toSend = '$range,%d,%d,%d,%d,%d'%(417, 1, 0, 50, 0 )
            elif self.chargerDict['OBC_Status_AC_Voltage'] == '200V':
                toSend = '$range,%d,%d,%d,%d,%d'%(417, 1, 50, 0, 0 )
            else:
                toSend = '$range,%d,%d,%d,%d,%d'%(417, 1, 0, 0, 50 )



            toSend += '\n'
            bytesToSend = toSend.encode('utf-8')

            if self.readyToSend:

                #print("sending Charge status bytes")
                #print(bytesToSend)
                ret = self.ser.write(bytesToSend)
                #print(ret)





    def doShutdown(self, msg):
        """
        send the proper signals out to shut down the motor
        Probably can just cut off power, but might be best to bring motor to stop if it isn't

        then disconnect mains and 12V power.

        """
        
        self.repeatSend = False
        self.pattern    = None
        self.nextToSend = self.setRangeMsg(0, 417, 0, 0, 0)
        if self.readyToSend:
            self.sendNext()

        print("Got shutdown msg")
#        import pdb; pdb.set_trace()



    def setRangeMsg(self, start = 0, number = 417, red = 0, green = 0, blue = 0):
        """
        return the bytes to send
        """
        toSend = '$range,%d,%d,%d,%d,%d'%(start, number, green, red, blue )
        toSend += '\n'
        bytesToSend = toSend.encode('utf-8')
        return bytesToSend



    def startCom(self):
        """
        """
        toSend = '$range,0,417,0,0,0'
        toSend += '\n'
        bytesToSend = toSend.encode('utf-8')
        
        print("sending bytes")
        print(bytesToSend)
        ret = self.ser.write(bytesToSend)
        print(ret)


    def doLumos(self, msg):
        """
        """

        self.repeatSend = False
        self.pattern    = None
        self.nextToSend = self.setRangeMsg(0, 417, msg['redVal'], msg['greenVal'], msg['blueVal'])
        if self.readyToSend:
            ret = self.ser.write(self.nextToSend)
            self.readyToSend = False
       
    def doPattern1(self, msg):
        """
        """

#        import pdb; pdb.set_trace()

        self.repeatSend = True
        self.pattern      = 1
        self.nextToSend = self.setRangeMsg(0, 417, 0, 0, 0)
        if self.readyToSend:
            self.sendNext()
       

    def doPattern2(self, msg):
        """
        """

        self.repeatSend = True
        self.pattern      = 2
        self.nextToSend = self.setRangeMsg(0, 417, 0, 0, 0)
        if self.readyToSend:
            self.sendNext()
       

    def doRpmMode(self, msg):
        """
        """

        self.repeatSend = True
        self.pattern      = 3
        self.nextToSend = self.setRangeMsg(0, 417, 0, 0, 0)
        if self.readyToSend:
            self.sendNext()
       

    def run(self):
        """
        """
        msg = ""
        self.startCom()
        #self.doLumos(msg)
        #self.doPattern1(msg)
        self.doPattern2(msg)   
        #self.doRpmMode(msg)   

        #self.doCanMotor(msg)
        #self.doCanCharger(msg)

        #self.doShutdown(msg)

        while True:
            self.serialDataReady()

if __name__ == '__main__':


    uhl = UnderHoodLights1()
    uhl.run()

