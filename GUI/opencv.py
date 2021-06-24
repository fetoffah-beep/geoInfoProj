# -*- coding: utf-8 -*-
"""
Created on Wed Mar 17 01:05:29 2021

@author: 39351
"""
# pip install opencv-pythonl
import cv2
import numpy as np
from matplotlib import pyplot as plt
# read an image
#img = cv2.imread('capture.jpg', 1)

img = np.zeros((512,512,3), np.uint8)
# Draw a diagonal blue line with thickness of 5 px
# img = cv2.line(img,(0,0),(511,511),(255,0,0),5)
# img = cv2.circle(img,(447,63), 63, (0,0,255), -1)
# img = cv2.rectangle(img,(384,0),(510,128),(0,255,0),3)
# img = cv2.ellipse(img,(256,256),(100,50),0,0,180,255,-1)
# pts = np.array([[10,5],[20,30],[70,20],[50,10]], np.int32)
# pts = pts.reshape((-1,1,2))
# img = cv2.polylines(img,[pts],True,(0,255,255))
# font = cv2.FONT_HERSHEY_SIMPLEX
# cv2.putText(img,'OpenCV',(10,500), font, 4,(255,255,255),2,cv2.LINE_AA)
#display the image in a window

# # mouse callback function
# def draw_circle(event,x,y,flags,param):
#     if event == cv2.EVENT_LBUTTONDBLCLK:
#         cv2.circle(img,(x,y),10,(255,0,0),-1)
# # Create a black image, a window and bind the function to window
# img = np.zeros((512,512,3), np.uint8)
# cv2.namedWindow('image')
# cv2.setMouseCallback('image',draw_circle)
# while(1):
#     cv2.imshow('image',img)
#     if cv2.waitKey(20) & 0xFF == 27:
#         break
# cv2.destroyAllWindows()

# cv2.namedWindow('image', cv2.WINDOW_NORMAL)
# cv2.imshow('image', img)
# k=cv2.waitKey(0)
# if k == 27:
#     cv2.destroyAllWindows()
# elif k==ord('s'):
#     cv2.imwrite('kofi.png', img)
#     cv2.destroyAllWindows

# # plt.imshow(img, cmap = 'gray', interpolation = 'bicubic')
# # plt.xticks([]), plt.yticks([])
# # plt.show()
drawing = False # true if mouse is pressed
mode = True # if True, draw rectangle. Press 'm' to toggle to curve
ix,iy = -1,-1
# mouse callback function
def draw_circle(event,x,y,flags,param):
    global ix,iy,drawing,mode
    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix,iy = x,y
    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing == True:
            if mode == True:
                cv2.rectangle(img,(ix,iy),(x,y),(0,255,0),1)
            else:
                cv2.circle(img,(x,y),5,(0,0,255),-1)
    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        if mode == True:
            cv2.rectangle(img,(ix,iy),(x,y),(0,255,0),1)
        else:
            cv2.circle(img,(x,y),5,(0,0,255),1)
img = np.zeros((512,512,3), np.uint8)
cv2.namedWindow('image')
cv2.setMouseCallback('image',draw_circle)
while(1):
    cv2.imshow('image',img)
    k = cv2.waitKey(1) & 0xFF
    if k == ord('m'):
        mode = not mode
    elif k == 27:
        break
cv2.destroyAllWindows()

