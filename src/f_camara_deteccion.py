#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 30 17:03:40 2023

@author: imano-oh
"""

import cv2
import numpy as np
import time
import tkinter as tk
from tkinter import filedialog
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

import f_busqueda_camaras as bc
import f_colores as col

"""
# ¿importar los colores de un archivo?
# low_green = np.array([36, 50, 70])
# high_green = np.array([89, 255, 255])
low_green = np.array([50, 100, 100])
high_green = np.array([70, 255, 255])

# ¿corregir rojo?
# low_red = np.array([0, 100, 100])
# high_red = np.array([10, 255, 255])
low_red = np.array([159, 50, 70])
high_red = np.array([180, 255, 255])

# Funciona
low_blue = np.array([110, 50, 50])
high_blue = np.array([130, 255, 255])

# Tuplas colores
verde = (low_green, high_green, "Verde")
rojo = (low_red, high_red, "Rojo")
azul = (low_blue, high_blue, "Azul")
"""

colores = col.lista_colores()
# colores = [rojo, verde, azul, amarillo, fucsia, naranja, cian]
rojo = colores[0]

video_path = "/home/imano-oh/poo.mp4"

cap = 0
fps_limite = 60.0
frame_delay = 1.0 / fps_limite

prev_y = 0
reference_point = (320, 240)  # Coordenadas del punto de referencia. Es el centro de la imagen pues la resolucion es 640x480
referencia_cm = 1

# cte_proporcion_cm_px = 0

Ts = 0.3

m = 1500

# --------------------------------------------------------------------------

def get_punto_referencia():
    return reference_point

def get_lista_colores():
    return colores
    
def get_colores_nombre():
    lista_nombres = []
    for c in colores:
        lista_nombres.append(c[2])
    return lista_nombres
    
def get_colores_matices():
    lista_matices = []
    for c in colores:
        lista_matices.append((c[0], c[1]))
    return lista_matices

# --------------------------------------------------------------------------

def centros(cont):
    M = []
    if len(cont) >= 1:
        # Ordenar los contornos por área (de mayor a menor)
        list_cont = sorted(cont, key=cv2.contourArea, reverse=True)[:3]
        
        for c in list_cont:
            # Calcular centro de cada contorno
            Mc = cv2.moments(c)
            if Mc['m00'] == 0:
                cx = 320
                cy = 240
            else:
                cx = int(Mc['m10'] / Mc['m00'])
                cy = int(Mc['m01'] / Mc['m00'])
            M.append((cx, cy))
        return M
    else:
        return [reference_point, reference_point]
    
# --------------------------------------------------------------------------    
    
def calibracion(frame, camara, color, ref):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, color[0], color[1])
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    contours_sorted = sorted(contours, key=cv2.contourArea, reverse=True)[:2]
    for i in contours_sorted:
            area = cv2.contourArea(i)
            x, y, w, h = cv2.boundingRect(i)
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 1)
    
    l_contours = centros(contours) + [reference_point, reference_point]
    
    c1 = l_contours[0]
    c2 = l_contours[1]

    dist_c1_c2 = np.sqrt((c1[0] - c2[0])**2 + (c1[1] - c2[1])**2)
    
    cv2.circle(frame, (c1[0], c1[1]), 3, (0, 255, 0), -1)
    cv2.circle(frame, (c2[0], c2[1]), 3, (0, 255, 0), -1)
    
    # Proporcion
    if dist_c1_c2 == 0:
        k = 99999 # error
    else:
        k = ref / dist_c1_c2
    
    return k
    
# --------------------------------------------------------------------------

def iniciar_deteccion(color, cap, p_y, ref):
    
    posicion_obj1 = []
    posicion_obj2 = []
    
    tiempo_proceso = 0
    tiempo_acumulado = 0
    tiempo_muestreo = 0
    cte_proporcion_cm_px = 0
        
    while True:
        
        tic = time.time()
        
        start_time = cv2.getTickCount()
        
        ret, frame = cap.read()
        
        if not ret:
            # print("tiempo total proceso: ", tiempo_acumulado)
            # print("objeto 1: ", posicion_obj1, "cantidad puntos", len(posicion_obj1))
            guardar_coordenadas_txt(tiempo_acumulado, cte_proporcion_cm_px, posicion_obj1, posicion_obj2)
            graficar(t[-m:], x[-m:], y[-m:])
            cap.release()
            cv2.destroyAllWindows()
            break
        
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, color[0], color[1]) # _, lower, higher
        
        cte_proporcion_cm_px = calibracion(frame, cap, rojo, ref) # Fijado para hacer calibracion con rojo
        contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        contours_sorted = sorted(contours, key=cv2.contourArea, reverse=True)[:2]
        
        # [:1] para que solo remarque el primer elemento, que seria el mas grande
        for i in contours_sorted[:1]:
            area = cv2.contourArea(i)
            nuevoContorno = cv2.convexHull(i)
            # dibujo contorno
            cv2.drawContours(frame, [nuevoContorno], -1, (200,5,255), 2)
                
            # x, y, w, h = cv2.boundingRect(i)
            # cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
    
        cv2.circle(frame, reference_point, 5, (0, 0, 255 ), -1)
        
        l_contours = centros(contours)
        
        c1 = l_contours[0]
        
        # Marcar centro del marco (+ centro de la imagen)
        cv2.circle(frame, (c1[0], c1[1]), 3, (0, 255, 255), -1)
        
        # Mostrar posicion centro rectangulo del objeto
        cv2.putText(frame, f"Posicion x : {c1[0] - reference_point[0]} px, Posicion y : {reference_point[1] - c1[1]} px", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)
    
        # Calibracion. Optimizar para que calibre por cambios muy bruscos
        dist_c1_c2 = int(np.sqrt((c1[0] - reference_point[0])**2 + (c1[1] - reference_point[1])**2))
        
        # cte_proporcion_cm_px = calibracion(frame, cap, rojo, ref) # Fijado para hacer calibracion con rojo
        dist_c1_c2_cm = round(dist_c1_c2 * cte_proporcion_cm_px, 4)
        
        # Imprimir en pantalla distancia entre c1 y c2
        cv2.putText(frame, f"Distancia al centro : {dist_c1_c2} px  {dist_c1_c2_cm} cm", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0  ), 1)
         
        cv2.putText(frame, "Oprimir 'q' para salir", (10, 475), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)
        
        # Calculo FPS de reproduccion y limite
        time_taken = (cv2.getTickCount() - start_time) / cv2.getTickFrequency()
        #fps = 1.0 / time_taken
        retardo_limite_fps = max(0, frame_delay, time_taken)

        time.sleep(retardo_limite_fps)
        time_taken = (cv2.getTickCount() - start_time) / cv2.getTickFrequency()
        fps = 1.0 / time_taken
        cv2.putText(frame, f"FPS: {fps:.2f}", (560, 475), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)
        
        cv2.imshow('frame', frame)
        
        tiempo_proceso = time.time() - tic

        tiempo_acumulado += tiempo_proceso
        
        # Revisar el tiempo. El tiempo de proceso no es mismo que el tiempo de reproduccion
        
        t, x, y = [], [], []
        posicion_obj1.append((round(tiempo_acumulado, 2), c1[0] - reference_point[0], reference_point[1] - c1[1], (c1[0] - reference_point[0])*cte_proporcion_cm_px, (reference_point[1] - c1[1])*cte_proporcion_cm_px, dist_c1_c2, dist_c1_c2_cm))
        for p in posicion_obj1:
            t.append(p[0])
            x.append(p[3])
            y.append(p[4])
            
        if (cv2.waitKey(1) & 0xFF == ord('q')) or (not ret):
            # print("tiempo total proceso: ", tiempo_acumulado)
            # print("objeto 1: ", posicion_obj1, "Cantidad puntos", len(posicion_obj1))
            guardar_coordenadas_txt(round(tiempo_acumulado, 2), cte_proporcion_cm_px, posicion_obj1, posicion_obj2)
            graficar(t[-m:], x[-m:], y[-m:])
            cap.release()
            cv2.destroyAllWindows()
            break
        
# --------------------------------------------------------------------------

def guardar_coordenadas_txt(tiempo_a, cte_cal, lista_1, lista_2):
    root = tk.Tk()
    root.withdraw()
    
    directorio_destino = filedialog.askdirectory(title="Selecciona una carpeta de destino")
    
    if directorio_destino:
        nombre_archivo = "coordenadas.txt"
        ruta_archivo = f"{directorio_destino}/{nombre_archivo}"
        
        try:
            with open(ruta_archivo, 'w') as archivo:
                archivo.write(f"Tiempo total del proceso: {tiempo_a}\n")
                archivo.write("\nCoordenadas objeto 1: \n")
                archivo.write("Tiempo      X(px)      Y(px)      X(cm)      Y(cm)      Dist. centro (px)      Dist. centro (cm)\n")
                for tupla in lista_1:
                    archivo.write(f"{tupla[0]} {tupla[1]} {tupla[2]} {tupla[3]} {tupla[4]} {tupla[5]} {tupla[6]}\n")
                                    
            print(f"Texto guardado en '{ruta_archivo}' con éxito.")
        except Exception as e:
            print(f"Error al guardar el texto en '{ruta_archivo}': {str(e)}")
    else:
        print("No se ha seleccionado una carpeta de destino.")

# --------------------------------------------------------------------------

def graficar(t, x, y):
    fig = plt.figure(tight_layout=True)
    gs = gridspec.GridSpec(1, 2)

    plot = [(t, x), (t, y)]
    titles = ['x(t)', 'y(t)']

    for i in range(2):
        p = plot[i]       
        ax = fig.add_subplot(gs[0, i])
        ax.grid(True, linestyle='-.')
        ax.plot(p[0], p[1])
        ax.set_xlabel('t')
        ax.set_ylabel(titles[i])

    fig.align_labels()  # same as fig.align_xlabels(); fig.align_ylabels()

    plt.show()
# --------------------------------------------------------------------------

# No se usa
def menu():
    camaras = bc.camaras_disponibles()
    camaras_nombre = bc.camaras_nombres()
    i = 0
    print("-- MENU --\n")
    if len(camaras) > 0:
        print(" ")
        print("Cámaras disponibles:")
        for camara in camaras:
            print(f"    Cámara {camara}: {camaras_nombre[i]}")
            i += 1
            #print(camara)
    else:
        print("No se encontraron cámaras disponibles.")
    
    while True:
        try:
            id_camara = input("Ingrese numero de camara: ")
            id_camara_int = int(id_camara)
            if id_camara_int in camaras:
                cap = cv2.VideoCapture(id_camara_int)
                break
            else:
                print("Camara no disponible")
        except ValueError:
            if id_camara == "videopath":
                print("videopath activado")
                cap = cv2.VideoCapture(video_path)
                break
            else:
                print("Ingreso no valido. No es numero\n")
            
    while True:
        try:
            i = input("Ingresar referencia para calibracion (centimetros) para calibracion: ")
            x = float(i)
            referencia_cm = x
            break
        except ValueError:
            print("Ingreso no valido. No es numero\n")
    
    while True:
        color = input("Ingrese color a medir (rojo (r) | azul (a) | verde (v)): ")
        if color == "r":
            iniciar_deteccion(colores[0], cap, prev_y, referencia_cm)
            break
        elif color == "a":
            iniciar_deteccion(colores[2], cap, prev_y, referencia_cm)
            break
        elif color == "v":
            iniciar_deteccion(colores[1], cap, prev_y, referencia_cm)
            break
        else:
            print("Ingreso no valido\n")
            
    return cap

# --------------------------------------------------------------------------

def hard_inicio(c, r):
    cap = cv2.VideoCapture(0)
    iniciar_deteccion(c, cap, prev_y, r)

# --------------------------------------------------------------------------

# hard_inicio(rojo, 10)

   # cap.release()
   # cv2.destroyAllWindows()
#cap.closeAllWindow()
