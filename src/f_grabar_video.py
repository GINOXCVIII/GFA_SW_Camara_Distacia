#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  29 19:18:48 2024

@author: imano-oh
"""

import cv2
import os
import sys
import tkinter as tk
from tkinter import filedialog

import f_camara_deteccion as fcd

# ----------------------------------------------------------------------

def captura_video(color, flg_guardar):
	salida = []
	objeto = []
	
	captura = cv2.VideoCapture(0)
	
	if flg_guardar:
		directorio = guardar_video()
		nombre_archivo = "videoTest"

		ruta_video = os.path.join(directorio, nombre_archivo + '.avi')
		salida = cv2.VideoWriter(ruta_video, cv2.VideoWriter_fourcc(*'XVID'),captura.get(cv2.CAP_PROP_FPS),(640,480))

	while (captura.isOpened()):
		ret, frame = captura.read()
		objeto = fcd.deteccion_objeto(frame, color)
		# print (captura.get(cv2.CAP_PROP_FPS))
		if ret:
			cv2.imshow('camara', frame)
			if flg_guardar:
				salida.write(frame)
			
			if cv2.waitKey(1) & 0xFF == ord('q'):
				break
		else: break
	
	if flg_guardar:
		salida.release()
	captura.release()
	cv2.destroyAllWindows()

# ----------------------------------------------------------------------

def guardar_video():
	
	ventana = tk.Tk()
	ventana.title("Guardar Video")
    
	directorio = filedialog.askdirectory(title="Selecciona una carpeta de destino")
	print(directorio)
	
	return directorio

# Prueba
color = fcd.colores[3]
guardar = False
captura_video(color, guardar)
