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

def captura_video(color, directorio, flg_guardar):
	salida = []
	objeto = []
	
	captura = cv2.VideoCapture(0)

	date = time.strftime("%a, %d %b %Y %H:%M:%S", time.gmtime())
	nombre_archivo = date[5:7]+"-"+date[8:11]+"-"+date[12:16]+"_"+date[17:25]

	ruta_video = os.path.join(directorio, nombre_archivo + '.avi')
	salida = cv2.VideoWriter(ruta_video, cv2.VideoWriter_fourcc(*'XVID'),captura.get(cv2.CAP_PROP_FPS),(640,480))

	while captura.isOpened():
		ret, frame = captura.read()
		frame_mostrar = frame.copy() # No muestra el frame calibrado si quisiera
		objeto = fcd.deteccion_objeto(frame_mostrar, color)
		lista = fcd.deteccion_rojo(frame_mostrar)
		# print (captura.get(cv2.CAP_PROP_FPS))
		if ret:
			cv2.imshow('camara', frame_mostrar)
			if flg_guardar:
				salida.write(frame)
			
			if cv2.waitKey(1) & 0xFF == ord('q'):
				break
		else: 
			break
	
	return ruta_video
	
	salida.release()
	captura.release()
	cv2.destroyAllWindows()
