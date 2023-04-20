import cv2
from cvzone.HandTrackingModule import HandDetector
import mouse
import threading
import numpy as np
import time

frameR = 100
cam_w, cam_h = 640, 480
cap = cv2.VideoCapture(1)
cap.set(3, cam_w)
cap.set(4, cam_h)
detector = HandDetector(detectionCon=0.9, maxHands=1)

l_delay = 0
r_delay = 0
double_delay = 0

def l_clk_delay():
    global l_delay
    global l_clk_thread
    time.sleep(1)
    l_delay = 0
    l_clk_thread = threading.Thread(target=l_clk_delay)

def r_clk_delay():
    global r_delay
    global r_clk_thread
    time.sleep(1)
    r_delay = 0
    r_clk_thread = threading.Thread(target=r_clk_delay)

def double_clk_delay():
    global double_delay
    global double_clk_thread
    time.sleep(2)
    double_delay = 0
    double_clk_thread = threading.Thread(target=double_clk_delay)

l_clk_thread = threading.Thread(target=l_clk_delay)
r_clk_thread = threading.Thread(target=r_clk_delay)
double_clk_thread = threading.Thread(target=double_clk_delay)

while True:
    success, img = cap.read()
    if success:
        img = cv2.flip(img, 1)
        hands, img = detector.findHands(img ,flipType=False)
        cv2.rectangle(img, (frameR, frameR), (cam_w - frameR, cam_h - frameR), (255, 0, 255), 2)
        if hands:
            lmlist = hands[0]['lmList']
            ind_x, ind_y = lmlist[8][0], lmlist[8][1]
            mid_x, mid_y = lmlist[12][0], lmlist[12][1]
            cv2.circle(img, (ind_x, ind_y), 5, (0, 255, 255), 2)
            cv2.circle(img, (mid_x, mid_y), 5, (0, 255, 255), 2)
            fingers = detector.fingersUp(hands[0])
    
            # Mouse movement
            if fingers[1] == 1 and fingers[2] == 0 and fingers[0]==1:
                conv_x = int(np.interp(ind_x, (frameR,cam_w-frameR),(0, 1536)))
                conv_y = int(np.interp(ind_y, (frameR,cam_h-frameR),(0, 864)))
                mouse.move(conv_x,conv_y)
                print(conv_x,conv_y)
    
            # Mouse Button Clicks
            if fingers[1] == 1 and fingers[2] == 1 and fingers[0] == 1:
                if abs(ind_x-mid_x) < 25 :
                    # Left Click
                    if fingers[4] == 0 and l_delay == 0:
                        mouse.click(button = "left")
                        l_delay = 1
                        l_clk_thread.start()
                    # Right Click
                    if fingers[4] == 1 and r_delay == 0:
                        mouse.click(button = "right")
                        r_delay = 1
                        r_clk_thread.start()
            # Mouse Scrolling
            if fingers[1] == 1 and fingers[2] == 1 and fingers[0] == 0 and fingers[4] == 0:
                if abs(ind_x-mid_x) < 25:
                    mouse.wheel(delta=-1)
            if fingers[1] == 1 and fingers[2] == 1 and fingers[0] == 0 and fingers[4] == 1:
                if abs(ind_x - mid_x) < 25:
                    mouse.wheel(delta=1)
    
            # Double Mouse Click
            if fingers[1] == 1 and fingers[2] == 0 and fingers[0] == 0 and fingers[4] == 0 and double_delay == 0:
                double_delay =1
                mouse.double_click(button="left")
                double_clk_thread.start()
    
        cv2.imshow("Camera Feed", img)
        cv2.waitKey(1)
