#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep  5 10:43:01 2023

@author: imano-oh
"""

import cv2
import numpy
from PyQt5.QtMultimedia import QCameraInfo

# Me da los indices de las camaras
def camaras_indices():
    
    cam_disp = []
    
    for i in range(10):  # Probar los primeros 10 números de dispositivo
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            cam_disp.append(i)
            cap.release()
    #print(cam_disp)
    return cam_disp

# Usa QtMultimedia para encontrar los nombres de las camaras
def camaras_nombres():

    lista = []
    
    camaras = QCameraInfo.availableCameras()
    camaras_disp = [c.description() for c in camaras]
    #camaras_disp.reverse()

    for i in range(0,len(camaras_disp)):
        lista.append(camaras_disp[i])

    return lista
    
