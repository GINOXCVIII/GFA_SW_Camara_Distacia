#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 29 19:18:48 2024

@author: imano-oh
"""

import cv2
import os
import sys
import time

import f_camara_deteccion as fcd

# ----------------------------------------------------------------------

def previsualizarVideo(cap, dimensiones, referencia, color, color_calibracion):
	ret, frame = cap.read()
	if ret:
		objeto = []
		frame_redimensionado = cv2.resize(frame, (dimensiones.width(), dimensiones.height()))
		frame_original = frame_redimensionado.copy()
		frame_original = cv2.cvtColor(frame_original, cv2.COLOR_BGR2RGB)
		oc = (int(dimensiones.width() / 2), int(dimensiones.height() / 2))
		k, o, _ = fcd.calibracion(frame_redimensionado, referencia, oc, color_calibracion, False)
		
		# frame_redimensionado = cv2.resize(frame, (dimensiones.width(), dimensiones.height()))
		objeto = fcd.deteccion_objeto(frame_redimensionado, color)
		_, _, _, _, _ = fcd.seguimiento_objeto(frame_redimensionado, color, o, k)
		frame_redimensionado = cv2.cvtColor(frame_redimensionado, cv2.COLOR_RGB2BGR)
		return frame_original, frame_redimensionado
	
