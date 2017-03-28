#!/home/pi/Desktop/launcher.sh python
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import numpy as np
import math as mat
import os
import datetime
import sys
global boehmCode

import socket
from networktables import NetworkTables as nt
import logging
logging.basicConfig(level=logging.DEBUG)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#s.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF,16)
s.settimeout(0)
while 1:
    try:
        print 'searching...'
        ip = socket.gethostbyname('roboRIO-329-FRC.local')
        break
    except:
        pass

nt.initialize(server=ip)
sd = nt.getTable("SmartDashboard")


count = 0
frameCount = 0
cnt2 = 0
countB = 0

############CAMERA############
camera = PiCamera()
camera.resolution = (480,368)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(480,368))
time.sleep(0.1)

def calcDistance(center,cnts,width):
    try:
        global start
        disHorizontalPixels = 240-center
        #print (disHorizontalPixels, center)
        #sd.putNumber('px dis from center', disHorizontalPixels)
        end = time.time()
        #sd.putNumber('update time', end-start)
        #factor = 10.0/width
        #disHorizontal = factor*disHorizontalPixels-1
        
        if len(cnts)==1:
            factor = 1.9/(width)
            disHorizontal = factor*disHorizontalPixels
            disHorizontal=float(disHorizontal)
            if disHorizontal<0:
                #print("neg")
                disHorizontal=disHorizontal-6
            else:
                #print("pos")
                disHorizontal=disHorizontal+6
        if len(cnts)>1:
            factor = 9.5/width
            disHorizontal = factor*disHorizontalPixels

        #print(disHorizontal)
            
        '''
        disHorizontal = (1.33*0.03918429135*disHorizontalPixels)+1.33*0.402417488488848
        if len(cnts)==1:
            if disHorizontal<0:
                disHorizontal=disHorizontal-5.25#adjust 5.25 if field is not accurate (disatnce between tapes - 2in)/2
            else:
                disHorizontal=disHorizontal+5.25
        #print(disHorizontal)
        '''
        
        '''
        if(abs(disHoriztonal) > 1.25):
            if(disHorizontal > 0):
                disHorizontal = disHorizontal - 1
            else:
                disHorizontal = disHorizontal + 1
        '''
        disHorizontal = round(disHorizontal,1)
        if disHorizontal>14:
            disHorizontal = 14
        if disHorizontal<-14:
            disHorizontal = -14
        return (disHorizontal)
    except:
        pass
    

def calcDistanceB(centerX, height, maxY,minY,width):
    #try:
    pi = 3.1415926535897932384626433832795028841
    '''angle = 60
    pixelHeigtToShoot=45
    disVerticalPixels = pixelHeigtToShoot-minY
    factor = 2.6/height
    disVerticalInches = factor*368
    #disVerticalInches = factor*disVerticalPixels
    disVerticalDrive = disVerticalInches/mat.tan(pi * angle / 180)
    distAway = 78 + disVerticalDrive'''

    pixelHeigtToShoot=38
    disVerticalPixels = pixelHeigtToShoot-minY
    disVerticalDrive= disVerticalPixels * (16.0 / 52)
    distAway = 78 + disVerticalDrive

    factorTwo = 14.0/width
    inchestospin = (236-centerX)*factorTwo

    angle = mat.degrees(mat.atan(inchestospin/distAway))
    #print("distance: " + str(disVerticalDrive) + "  angle: " + str(angle)
        #+ '  maxY: '+ str(maxY) + '  DistVert:' +str(disVerticalPixels))
    ##print("angle",angle)
    
    
    #sd.putNumber('Boiler px off X', disHorizontal)
    #sd.putNumber('Boiler px off Y', disVertical)
    return (disVerticalDrive,angle)
    #except:
        #return (0,0)
        #print 'err'
        #pass


def calcProperties(cnts):
    global boehmCode
    area = 0

    too_small=[]
    if Pi=="b":
        ar = 200
    else:
        ar = 500
    
    ################    '''for ct in range(len(cnts)):
    ################        minX = min(a[0][0] for a in cnts[ct])#Min X of Obj
    ################        maxX = max(a[0][0] for a in cnts[ct])#Max X of Obj
    ################        maxY = max(b[0][1] for b in cnts[ct])#MAx Y of Obj
    ################        minY = min(b[0][1] for b in cnts[ct])#Min Y of Obj
    ################        area = abs(maxX-minX)*abs(maxY-minY)
    ################        #print ('area',area)'''
    try:
        for ct in range(len(cnts)):
            contours=[]
            contours = np.vstack(cnts[ct]).squeeze()
            area=cv2.contourArea(contours)
            #print(area,len(cnts))
            if area < ar:
                too_small.append(ct)
        for c in range(1, len(too_small) + 1):
            del cnts[too_small[-c]]
        print(len(cnts))
    except:
        pass
    if len(cnts)==2:
        #print("two obj")
        minX1 = min(a[0][0] for a in cnts[0])#Min X of Obj 1
        maxX1 = max(a[0][0] for a in cnts[0])#Max X of Obj 1
        maxY1 = max(b[0][1] for b in cnts[0])#MAx Y of Obj 1
        minY1 = min(b[0][1] for b in cnts[0])#Min Y of Obj 1
        
        minX2 = min(x[0][0] for x in cnts[1])#Max X of Obj 2
        maxX2 = max(x[0][0] for x in cnts[1])#Max X of Obj 2
        minY2 = min(y[0][1] for y in cnts[1])#Min Y of Obj 2
        maxY2 = max(y[0][1] for y in cnts[1])#Max Y of Obj 2

        if minX1<minX2:
            #print('X normal?')
            xAvg1 = (minX1+maxX1)/2
            xAvg2 = (minX2+maxX2)/2
            if  sd.getString('Pi_Stuff')=="b":    
                #print('BOILER')
                #cv2.imshow("mask", mask)
                #cv2.imshow("hsv", image)
                calcBoiler(cnts, minX1, maxX2, minY1, maxY1, minY2, maxY2, minX2, maxX1)
                return
            else:
                #print(minX1, maxX2, minY1, maxY1, minY2, maxY2, minX2)
                calcGear(cnts, minX1, maxX2, minY1, maxY1, minY2, maxY2, minX2)
                return
        else:
            #print('X backwards?')
            xAvg1 = (minX1+maxX1)/2
            xAvg2 = (minX2+maxX2)/2
            if  sd.getString('Pi_Stuff')=="b":     
                #print('BOILER')
                #cv2.imshow("mask", mask)
                #cv2.imshow("hsv", image)
                calcBoiler(cnts, minX2, maxX1, minY2, maxY2, minY1, maxY1, minX1, maxX2)
                return
            else:
                #print('GEARS')
                calcGear(cnts, minX2, maxX1, minY2, maxY2, minY1, maxY1, minX1)
                return

    if len(cnts)==1:
        #print("one obj")
        minX1 = min(a[0][0] for a in cnts[0])#Min X of Obj 1
        maxX2 = max(a[0][0] for a in cnts[0])#Max X of Obj 1
        maxY1 = max(b[0][1] for b in cnts[0])#MAx Y of Obj 1
        minY1 = min(b[0][1] for b in cnts[0])#Min Y of Obj 1
        maxX1 = max(a[0][0] for a in cnts[0])#Max X of Obj 1
        minX2 = min(x[0][0] for x in cnts[0])#Max X of Obj 2
        minY2 = min(y[0][1] for y in cnts[0])#Min Y of Obj 2
        maxY2 = max(y[0][1] for y in cnts[0])#Max Y of Obj 2
        xAvg1 = (minX1+maxX2)/2
        xAvg2 = (minX1+maxX2)/2

        if sd.getString('Pi_Stuff')=="b":        
            #print('BOILER')
            #cv2.imshow("mask", mask)
            #cv2.imshow("hsv", image)
            calcBoiler(cnts, minX1, maxX2, minY1, maxY1, minY2, maxY2, minX2, maxX1)
            return
        else:
            #print('GEARS')
            calcGear(cnts, minX1, maxX2, minY1, maxY1, minY2, maxY2, minX2)
            return

def calcBoiler(cnts, minX1,maxX2, minY1, maxY1, minY2, maxY2, minX2, maxX1):
    if maxY1<minY2:
        minY2 = min(b[0][1] for b in cnts[1])
        maxY1 = max(y[0][1] for y in cnts[0])
        
   
    
    width = maxX1 - minX2
    
    height = maxY1 - minY2

    centerX = (maxX1+minX1)/2
    #centerY = maxY1+minY2)


    
    #print('width: '+str(width))
    #print('height: '+str(height))
    #center1=(maxX1+minX1)/2
    #center2=(maxX2+minX2)/2
    #width1=maxX1-minX1
    
    ##print('width diff: '+str(abs(width1-width2)))
    ##print('center diff: '+str(abs(center2-center1)))


    hObjOne = maxY1 - minY1
    hObjTwo = maxY2 - minY2
    if minY1 < minY2:
        minY=minY1
    else:
        minY=minY2
    
    
    try:
        xDist,Angle=calcDistanceB(centerX, height, maxY1,minY,width)
        sd.putNumber('Boiler Drive (in)', xDist)
        sd.putNumber('Angle', angle)
    except:
        pass
    global countB
    countB = countB+1
        #sd.putNumber('Count Boiler', countB)
        #hAvg = (hObjOne + hObjTwo)/2
        #heightDif = hObjTwo - hAvg
        #center2=(maxX2+minX2)/2
        #centerDif=center2-320
        #print ('BOILER')
        #print ('disAvg:        '+str(disAvg))
        #print ('height One:     '+str(hObjOne))
        #print ('height Two:     '+str(hObjTwo))
        #print ('disAngle:      '+str(disAngle))
        #print ('widthTar:      '+str(center2))
        #print ('widthDif:      '+str(centerDif))
    #except:
        #print('ERR: boiler')
        #pass

def calcGear(cnts, minX, maxX, minY1, maxY1, minY2, maxY2, minX2):
    if maxX<minX and len(cnts)==2:
        minX = min(a[0][0] for a in cnts[1])
        maxX = min(x[0][0] for x in cnts[0])

        
    hObjOne = maxY1 - minY1
    hObjTwo = maxY2 - minY2
    width=maxX-minX
    
    try:
        center = (minX+maxX)/2
        disHorizontal=calcDistance(center,cnts,width)
        global count
        count = count+1
        #sd.putNumber('Gear Dist', disAvg)
        sd.putNumber('Horizontal Dist', disHorizontal)
        #print(disHorizontal)
        #sd.putNumber('Angle Dist', disAngle)
        #sd.putNumber('Height Difference', hObjOne-hObjTwo)
        sd.putNumber('Count', count)
    except:
       #print('ERR: gear')
       pass
    
    #return (minX,maxX,minY,maxY,height)
    return

for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    start = time.time()
    frameCount = frameCount + 1
    sd.putNumber('Frame Count', frameCount)
    image = frame.array
    #sd.putNumber('Gear Finder', 100)
    #sd.putNumber('GearTarget or BoilerTarget',100)
    #if sd.getNumber('GearTarget or BoilerTarget') != 1:
    hsv = cv2.cvtColor(image,cv2.COLOR_BGR2HSV)
    '''
    hueMin = sd.getNumber('Hue Min')
    hueMax = sd.getNumber('Hue Max')
    satMin = sd.getNumber('Sat Min')
    satMax = sd.getNumber('Sat Max')
    valMin = sd.getNumber('Val Min')
    valMax = sd.getNumber('Val Max')
    low=np.array([hueMin,satMin,valMin])
    high=np.array([hueMax,satMax,valMax])
    '''


    if sd.getString('Pi_Stuff')=="g":
        low=np.array([65,10,180])#GEAR green 50,50,150 or 25,100,200  50,75,100
        high=np.array([90,255,255])#GEAR green 100.255,255 or 85-255-255
    else:
        low=np.array([75,120,145])#green 50,50,150 or 25,100,200  50,75,100
        high=np.array([90,255,241])#green 100.255,255 or 85-255-255
    mask = cv2.inRange(hsv, low, high)
    if sd.getString('Pi_Stuff')=="g":
        kernel = np.ones((6,6), np.uint8)
        mask = cv2.erode(mask, None, iterations=4)
        mask = cv2.dilate(mask, None, iterations=4)
    else:
        kernel = np.ones((6,6), np.uint8)
        mask = cv2.GaussianBlur(mask,(7,7),0)
        mask = cv2.erode(mask, None, iterations=4)
        mask = cv2.dilate(mask, None, iterations=5)
    '''
    mask = cv2.inRange(hsv, low, high)
    kernel = np.ones((6,6), np.uint8)
    mask = cv2.erode(mask, None, iterations=2)
    '''
    #opening = cv2.morphologyEx(mask, cv2.MORPH_OPEN,kernel)

    #mask = cv2.GaussianBlur(mask,(7,7),0)
    #res = cv2.bitwise_and(frame,frame, mask= mask)
    #mask = cv2.inRange(BW, low,high)
    #edges = cv2.Canny(mask,100,200)
    
    #mask = cv2.dilate(mask, None, iterations=2)
    #cv2.imshow('Edges',edges)

    #TEMP
    #cv2.imshow("mask", mask)
    #cv2.imshow("hsv", image)


    #cv2.imshow("opening", opening)
    #################################
    ##############################
    #################################
    ##############################
    #time.sleep(2) #Remove in production code makes values readible#
    ###############################
    #################################
    #################################
    ##############################
    key = cv2.waitKey(1) & 0xFF
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
##    try:
##            
##        too_small=[]
##        
##        for ct in range(len(cnts)):
##            minX = min(a[0][0] for a in cnts[ct])#Min X of Obj
##            maxX = max(a[0][0] for a in cnts[ct])#Max X of Obj
##            maxY = max(b[0][1] for b in cnts[ct])#MAx Y of Obj
##            minY = min(b[0][1] for b in cnts[ct])#Min Y of Obj
##            area = abs(maxX-minX)*abs(maxY-minY)
##            #print ('area',area)
##            
##            if area < 500:
##                too_small.append(ct)
##
##        for c in range(1, len(too_small) + 1):
##            del cnts[too_small[-c]]
##
##        #print ('cnts',len(cnts))
##    except:
##        pass #print sys.exc_info()[0]
    if len(cnts)==0:
        sd.putNumber('Horizontal Dist', 32767)
        sd.putNumber('Boiler Drive (in)', 32767)
        sd.putNumber('Angle', 32767)
    
    calcProperties(cnts)

    rawCapture.truncate(0)
     
