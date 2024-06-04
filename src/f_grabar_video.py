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

def captura_video(indice, color, directorio, ref, check):
	salida = []
	objeto = []
	
	captura = cv2.VideoCapture(indice)

	date = time.strftime("%a, %d %b %Y %H:%M:%S", time.gmtime())
	nombre_archivo = date[5:7]+"-"+date[8:11]+"-"+date[12:16]+"_"+date[17:25]

	ruta_video = os.path.join(directorio, nombre_archivo + '.avi')
	salida = cv2.VideoWriter(ruta_video, cv2.VideoWriter_fourcc(*'XVID'),captura.get(cv2.CAP_PROP_FPS),(640,480))

	while captura.isOpened():
		
		ret, frame = captura.read()
		frame_mostrar = frame.copy() # No muestra el frame calibrado si quisiera
		# lista = fcd.deteccion_rojo(frame_mostrar)
		h, w = frame.shape[:2]
		oc = (int(w/2), int(h/2))
		k, o, frame_calibrado = fcd.calibracion(frame_mostrar, ref, oc, check)
		
		if ret:
			if cv2.waitKey(1) & 0xFF == ord('q'):
			 	break
			
			if check:
				objeto = fcd.deteccion_objeto(frame_calibrado, color)
				_, _, _, _, _ = fcd.seguimiento_objeto(frame_calibrado, color, o, k)
				cv2.imshow('camara', frame_calibrado)
			else:
				objeto = fcd.deteccion_objeto(frame_mostrar, color)
				_, _, _, _, _ = fcd.seguimiento_objeto(frame_mostrar, color, o, k)
				cv2.imshow('camara', frame_mostrar)

			print("llegue ac'a")
			salida.write(frame)
			
		else: 
			break
	
	salida.release()
	captura.release()
	cv2.destroyAllWindows()
	
	return ruta_video
