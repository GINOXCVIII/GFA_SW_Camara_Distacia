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
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from operator import itemgetter, attrgetter
from tkinter import filedialog

import f_busqueda_camaras as bc
import f_colores as col

colores = col.lista_colores()
rojo = colores[0]

cap = 0

referencia_cm = 1

# --------------------------------------------------------------------------

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

def centros(cont, oc):
    M = []
    if len(cont) >= 1:
        # Ordenar los contornos por área (de mayor a menor)
        list_cont = sorted(cont, key=cv2.contourArea, reverse=True)[:3]
        
        for c in list_cont:
            # Calcular centro de cada contorno
            Mc = cv2.moments(c)
            if Mc['m00'] == 0:
                cx = oc[0]
                cy = oc[1]
            else:
                cx = int(Mc['m10'] / Mc['m00'])
                cy = int(Mc['m01'] / Mc['m00'])
            M.append((cx, cy))
        return M
    else:
        return [oc]
    
# --------------------------------------------------------------------------    
    
def calibracion(frame, camara, color, ref, oc):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, color[0], color[1])
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    contours_sorted = sorted(contours, key=cv2.contourArea, reverse=True)[:2]
    for i in contours_sorted:
            area = cv2.contourArea(i)
            x, y, w, h = cv2.boundingRect(i)
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 1)
    
    l_contours = centros(contours, oc) + [oc, oc]
    
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

def iniciar_deteccion(color, cap, ref, check):
    
    posicion_obj1 = []
    
    tiempo_proceso = 0
    tiempo_acumulado = 0
    cte_proporcion_cm_px = 0
        
    while True:
        
        tic = time.time()
        start_time = cv2.getTickCount()
        
        ret, frame = cap.read()
        
        if not ret:
            guardar_coordenadas_txt(tiempo_acumulado, cte_proporcion_cm_px, posicion_obj1)
            graficar(t, x, y)
            cap.release()
            cv2.destroyAllWindows()
            break
            
        try:
            h, w = frame.shape[:2]
            origen_coordenadas = (int(w/2), int(h/2))
        except AttributeError:
            print("frame None", origen_coordenadas)
        
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, color[0], color[1]) # _, lower, higher
        
        cte_proporcion_cm_px = calibracion(frame, cap, rojo, ref, origen_coordenadas) # Fijado para hacer calibracion con rojo
        
        # Dibujo del contorno de la figura más grande
        contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        contours_sorted = sorted(contours, key=cv2.contourArea, reverse=True)
        if len(contours_sorted) != 0:
            area = cv2.contourArea(contours_sorted[0])
            nuevoContorno = cv2.convexHull(contours_sorted[0])
            cv2.drawContours(frame, [nuevoContorno], -1, (200,5,255), 2)
        
        # Marcar el centro de la imagen (resolución fija 640x480)
        cv2.circle(frame, origen_coordenadas, 5, (0, 0, 255 ), -1)
        
        # Marcar centro de la figura
        c1 = centros(contours_sorted[:1], origen_coordenadas)[0]
        cv2.circle(frame, (c1[0], c1[1]), 3, (0, 255, 255), -1)
        
        cv2.putText(frame, f"Posicion x : {c1[0] - origen_coordenadas[0]} px, Posicion y : {origen_coordenadas[1] - c1[1]} px", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)
    
        # Calibracion. Optimizar para que calibre por cambios muy bruscos
        dist_c1_c2 = int(np.sqrt((c1[0] - origen_coordenadas[0])**2 + (c1[1] - origen_coordenadas[1])**2))
        
        # cte_proporcion_cm_px = calibracion(frame, cap, rojo, ref) # Fijado para hacer calibracion con rojo
        dist_c1_c2_cm = round(dist_c1_c2 * cte_proporcion_cm_px, 4)
        
        # Imprimir en pantalla distancia entre c1 y c2
        cv2.putText(frame, f"Distancia al centro : {dist_c1_c2} px  {dist_c1_c2_cm} cm", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0  ), 1)
         
        cv2.putText(frame, "Oprimir 'q' para salir", (10, 475), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)
        
        # Calculo FPS reproduccion
        time_taken = (cv2.getTickCount() - start_time) / cv2.getTickFrequency()
        time_taken = (cv2.getTickCount() - start_time) / cv2.getTickFrequency()
        fps = 1.0 / time_taken
        cv2.putText(frame, f"FPS: {fps:.2f}", (560, 475), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)
        
        tiempo_proceso = time.time() - tic

        tiempo_acumulado += tiempo_proceso
        
        cv2.imshow('frame', frame)
        
        # Revisar el tiempo. El tiempo acumulado no es el mismo que la duracion de un video
        t, x, y = [], [], []
        posicion_obj1.append((round(tiempo_acumulado, 2), c1[0] - origen_coordenadas[0], origen_coordenadas[1] - c1[1], (c1[0] - origen_coordenadas[0])*cte_proporcion_cm_px, (origen_coordenadas[1] - c1[1])*cte_proporcion_cm_px, dist_c1_c2, dist_c1_c2_cm))
        for p in posicion_obj1:
            t.append(p[0])
            x.append(p[3])
            y.append(p[4])
            
        if (cv2.waitKey(1) & 0xFF == ord('q')) or (not ret):
            guardar_coordenadas_txt(round(tiempo_acumulado, 2), cte_proporcion_cm_px, posicion_obj1)
            graficar(t, x, y)
            cap.release()
            cv2.destroyAllWindows()
            break
        
# --------------------------------------------------------------------------

def guardar_coordenadas_txt(tiempo_a, cte_cal, lista_1):
    root = tk.Tk()
    root.withdraw()
    
    directorio_destino = filedialog.askdirectory(title="Selecciona una carpeta de destino")
    
    date = time.strftime("%a, %d %b %Y %H:%M:%S", time.gmtime())
    nombre_archivo = date[5:7]+"-"+date[8:11]+"-"+date[12:16]+" "+date[17:25]+".txt"
    print(nombre_archivo)
    
    if directorio_destino:
        nombre_archivo = nombre_archivo
        ruta_archivo = f"{directorio_destino}/{nombre_archivo}"
        
        try:
            with open(ruta_archivo, 'w') as archivo:
                archivo.write(f"{date}\n")
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

    fig.align_labels()

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
            iniciar_deteccion(colores[0], cap, referencia_cm)
            break
        elif color == "a":
            iniciar_deteccion(colores[2], cap, referencia_cm)
            break
        elif color == "v":
            iniciar_deteccion(colores[1], cap, referencia_cm)
            break
        else:
            print("Ingreso no valido\n")
            
    return cap

# --------------------------------------------------------------------------

def hard_inicio(c, r, check):
    cap = cv2.VideoCapture(0)
    iniciar_deteccion(c, cap, r, check)

# --------------------------------------------------------------------------

# hard_inicio(rojo, 10)

   # cap.release()
   # cv2.destroyAllWindows()
#cap.closeAllWindow()
