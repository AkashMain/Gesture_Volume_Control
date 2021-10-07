import cv2 as cv   
import mediapipe as mp 
import numpy as np
import time
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

cap = cv.VideoCapture(0)

mpHands = mp.solutions.hands
hands = mpHands.Hands(False,2,0.7)
mpDraw = mp.solutions.drawing_utils 

l1=[]
l2=[]
ctime=0
ptime=0
i1,a1,b1,i2,a2,b2=0,0,0,0,0,0

wcam,hcam = (640,480)
cap.set(3,wcam)
cap.set(4,hcam)


devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
#volume.GetMute()
#volume.GetMasterVolumeLevel()
volrange = (volume.GetVolumeRange())


minvol = volrange[0]
maxvol = volrange[1]
vol=0
volbar=370
volpercent=0

while True:
    k,frame = cap.read()
    imgRGB = cv.cvtColor(frame,cv.COLOR_BGR2RGB)
    results = hands.process(imgRGB)

    if results.multi_hand_landmarks:

        for handlandmarks in results.multi_hand_landmarks:

            for id,lm in enumerate(handlandmarks.landmark):
            
                h,w,c = frame.shape
                cx,cy = int(lm.x*w),int(lm.y*h)   # coordinates of 21 landmarks 
                #print(id,cx,cy)
                    
                if id==4:
                    i1=id
                    a1=cx
                    b1=cy
                    l1.append(i1)
                    l1.append(a1)
                    l1.append(b1)
                    #print(l1,'\n')
                    #print(id,cx,cy)

                if id==8:
                    i2=id
                    a2=cx
                    b2=cy
                    l2.append(i2)
                    l2.append(a2)
                    l2.append(b2)
                    #print(l2,'\n')
                    #print(id,cx,cy)

                a3=(a1+a2)//2
                b3=(b1+b2)//2

                length = math.hypot(a2-a1,b2-b1)
                #print(length)

                # Hand Range--> 20-250
                # Volume Range--> -65-0
                # VolumeBar Range--> 370,100
                # VolumePercentage Range--> 0-100

                vol = np.interp(length,[20,250],[minvol,maxvol])
                volbar = np.interp(length,[20,250],[370,100])
                volpercent = np.interp(length,[20,250],[0,100])
                print(length,vol,volpercent)
                volume.SetMasterVolumeLevel(vol, None)

                cv.circle(frame,(a1,b1),10,(255,0,255),-1)
                cv.circle(frame,(a2,b2),10,(255,0,255),-1)
                cv.line(frame,(a1,b1),(a2,b2),(0,0,255),3)
                cv.circle(frame,(a3,b3),10,(255,0,255),-1)

                if length<20:
                    cv.circle(frame,(a3,b3),10,(255,0,0),-1)
                else:
                    cv.circle(frame,(a3,b3),10,(255,0,255),-1)    
                    

            mpDraw.draw_landmarks(frame, handlandmarks, mpHands.HAND_CONNECTIONS)

    cv.rectangle(frame,(20,100),(50,370),(0,255,255),3)
    cv.rectangle(frame,(20,int(volbar)),(50,370),(0,255,255),-1)
    cv.putText(frame,str(int(volpercent))+"%",(10,430),cv.FONT_HERSHEY_SIMPLEX,1,(0,255,255),3)


    ctime=time.time()
    fps = 1/(ctime-ptime)
    ptime=ctime

    cv.putText(frame,"FPS: "+str(int(fps)),(10,50),cv.FONT_HERSHEY_SIMPLEX,1,(0,255,0),3)

    cv.imshow('Frame',frame)
    if cv.waitKey(1) & 0xff==ord('e'):
        break

cap.release()
cv.destroyAllWindows()