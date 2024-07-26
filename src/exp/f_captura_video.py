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

def previsualizarVideo(cap, dimensiones, referencia, color, color2, color_calibracion, dos_objetos):
	ret, frame = cap.read()
	if ret:
		objeto = []
		objetos2 = []
		frame_redimensionado = cv2.resize(frame, (dimensiones.width(), dimensiones.height()))
		frame_original = frame_redimensionado.copy()
		frame_original = cv2.cvtColor(frame_original, cv2.COLOR_BGR2RGB)
		oc = (int(dimensiones.width() / 2), int(dimensiones.height() / 2))
		k, o, _ = fcd.calibracion(frame_redimensionado, referencia, oc, color_calibracion, False)
		
		# frame_redimensionado = cv2.resize(frame, (dimensiones.width(), dimensiones.height()))
		if dos_objetos:
			if (color[0] == color2[0]).all() and (color[1] == color2[1]).all():
				objeto = fcd.deteccion_objeto(frame_redimensionado, color, dos_objetos)
				_, _, _, _, _ = fcd.seguimiento_objeto(frame_redimensionado, color, o, k, dos_objetos)
			else:
				objeto = fcd.deteccion_objeto(frame_redimensionado, color, not dos_objetos)
				_, _, _, _, _ = fcd.seguimiento_objeto(frame_redimensionado, color, o, k, not dos_objetos)
				objeto2 = fcd.deteccion_objeto(frame_redimensionado, color2, not dos_objetos)
				_, _, _, _, _ = fcd.seguimiento_objeto(frame_redimensionado, color2, o, k, not dos_objetos)
		else:
			objeto = fcd.deteccion_objeto(frame_redimensionado, color, dos_objetos)
			_, _, _, _, _ = fcd.seguimiento_objeto(frame_redimensionado, color, o, k, dos_objetos)
		
		
		frame_redimensionado = cv2.cvtColor(frame_redimensionado, cv2.COLOR_RGB2BGR)
		
		return frame_original, frame_redimensionado
	
