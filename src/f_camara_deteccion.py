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

import f_busqueda_camaras as bc

low_green = np.array([36, 50, 70])
high_green = np.array([89, 255, 255])

low_red = np.array([0, 100, 100])
high_red = np.array([10, 255, 255])

# low_blue = np.array([110, 100, 100])
# high_blue = np.array([130, 255, 255])
low_blue = np.array([90, 50, 70])
high_blue = np.array([128, 255, 255])

# Tuplas colores
verde = (low_green, high_green)
rojo = (low_red, high_red)
azul = (low_blue, high_blue)

video_path = "/home/imano-oh/poo.mp4"

cap = 0
fps_limite = 60.0
frame_delay = 1.0 / fps_limite

prev_y = 0
reference_point = (320, 240)  # Coordenadas del punto de referencia. Es el centro de la imagen pues la resolucion es 640x480
referencia_cm = 1

# cte_proporcion_cm_px = 0

Ts = 0.3

# --------------------------------------------------------------------------

def punto_referencia():
    return reference_point

# --------------------------------------------------------------------------

def centros(cont):
    M = []
    if len(cont) >= 2:
        # Ordenar los contornos por área (de mayor a menor)
        list_cont = sorted(cont, key=cv2.contourArea, reverse=True)[:2]
        
        for c in list_cont:
            # Calcular centro de cada contorno
            Mc = cv2.moments(c)
            if Mc['m00'] == 0:
                cx = 320
                cy = 240
            else:
                cx = int(Mc['m10'] / Mc['m00'])
                cy = int(Mc['m01'] / Mc['m00'])
            M.append([cx, cy])
        return M
    else:
        return [reference_point, reference_point]
    
# --------------------------------------------------------------------------    
    
def calibracion(frame, camara, color, ref):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, color[0], color[1])
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    l_contours = centros(contours)
    
    c1 = l_contours[0]
    c2 = l_contours[1]

    dist_c1_c2 = np.sqrt((c1[0] - c2[0])**2 + (c1[1] - c2[1])**2)
    
    cv2.circle(frame, (c1[0], c1[1]), 3, (0, 255, 0), -1)
    cv2.circle(frame, (c2[0], c2[1]), 3, (0, 255, 0), -1)
    
    # Proporcion
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
    
    print("color:", color, "cap:", cap, "ref:", ref)
    print("color bajo:", color[0], "color alto:", color[1])
    
    """
    def validar_color(color):
        if len(color) == 1:
            if color == "r": 
                return rojo
            elif color == "v": 
                return verde
            elif color == "a":
                return azul
        else:
            return color
    
    color = validar_color(color)
    """
    
    while True:
        
        tic = time.time()
        
        start_time = cv2.getTickCount()
        
        ret, frame = cap.read()
        
        if not ret:
            print("tiempo total proceso: ", tiempo_acumulado)
            print("objeto 1: ", posicion_obj1, "cantidad puntos", len(posicion_obj1))
            # print("objeto 2: ", posicion_obj2, "cantidad puntos", len(posicion_obj2))
            guardar_coordenadas_txt(tiempo_acumulado, cte_proporcion_cm_px, posicion_obj1, posicion_obj2)
            cap.release()
            cv2.destroyAllWindows()
            break
        
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        #mask = cv2.inRange(hsv, lower_pink, upper_pink)
        mask = cv2.inRange(hsv, color[0], color[1]) # _, lower, higher
        contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Agarro solo los dos más grandes, si no me explota la PC
        # ¿Pasar por parametros cuantos objetos quiero?
        contours_sorted = sorted(contours, key=cv2.contourArea, reverse=True)[:2]
        
        # [:1] para que solo remarque el primer elemento, que seria el mas grande
        for i in contours_sorted[:1]:
            area = cv2.contourArea(i)
            # ¿Achicar o agrandar el area a remarcar?
            if area > 250:
                x, y, w, h = cv2.boundingRect(i)
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                #if y < p_y:
                #    pyautogui.press('space')
                #p_y = y
        #
    
        cv2.circle(frame, reference_point, 5, (0, 0, 255 ), -1)
        
        l_contours = centros(contours)
        
        c1 = l_contours[0]
        # c2 = l_contours[1]
        # Para medir la distancia de un solo objeto de color respecto al centro de coordenadas, puesto en el centro del frame
        c2 = reference_point
        
        # Marcar centro del marco (+ centro de la imagen)
        cv2.circle(frame, (c1[0], c1[1]), 3, (0, 255, 0), -1)
        cv2.circle(frame, (c2[0], c2[1]), 3, (0, 255, 0), -1)
        
        # Mostrar posicion centro de los 2 rectangulos mas grandes
        cv2.putText(frame, f"cx1 : {c1[0] - reference_point[0]} px, cy1 : {reference_point[1] - c1[1]} px", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)
        #cv2.putText(frame, f"cx2 : {c2[0] - reference_point[0]} px, cy2 : {reference_point[1] - c2[1]} px", (10, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 255), 1)
    
        dist_c1_c2 = np.sqrt((c1[0] - c2[0])**2 + (c1[1] - c2[1])**2)
        # Imprimir en pantalla distancia entre c1 y c2
        cv2.putText(frame, f"Distancia c1 a c2 : {dist_c1_c2} px", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0  ), 1)
        
        # Calibracion. Optimizar para que calibre por cambios muy bruscos
        cte_proporcion_cm_px = calibracion(frame, cap, rojo, ref) # Fijado para hacer calibracion con rojo
        dist_c1_c2_cm = dist_c1_c2 * cte_proporcion_cm_px
        cv2.putText(frame, f"Distancia c1 a c2 : {dist_c1_c2_cm} cm", (10, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0  ), 1)
        
        cv2.putText(frame, "Oprimir 'q' para salir", (10, 475), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)
    
        # cv2.imshow('frame', frame)
        
        # Calculo FPS de reproduccion y limite
        time_taken = (cv2.getTickCount() - start_time) / cv2.getTickFrequency()
        #fps = 1.0 / time_taken
        retardo_limite_fps = max(0, frame_delay, time_taken)

        time.sleep(retardo_limite_fps)
        time_taken = (cv2.getTickCount() - start_time) / cv2.getTickFrequency()
        fps = 1.0 / time_taken
        cv2.putText(frame, f"FPS: {fps:.2f}", (560, 475), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)
        
        cv2.imshow('frame', frame)
        
        toc = time.time()

        # Muestreo
        
        tiempo_proceso = toc - tic
        tiempo_acumulado += tiempo_proceso
        tiempo_muestreo += tiempo_proceso
        
        # Podria ser > Ts...
        if tiempo_muestreo > 1:
            tiempo_muestreo = 0
            
        print(tiempo_proceso, tiempo_acumulado, round(tiempo_muestreo, 1))
        
        if round(tiempo_muestreo, 1) == Ts:
            tiempo_muestreo = 0
            posicion_obj1.append((round(tiempo_acumulado, 2), c1[0] - reference_point[0], reference_point[1] - c1[1], (c1[0] - reference_point[0])*cte_proporcion_cm_px, (reference_point[1] - c1[1])*cte_proporcion_cm_px))
            # posicion_obj2.append((tiempo_acumulado, c2[0] - reference_point[0], reference_point[1] - c2[1], (c2[0] - reference_point[0])*cte_proporcion_cm_px, (reference_point[1] - c2[1])*cte_proporcion_cm_px))
            
        if (cv2.waitKey(1) & 0xFF == ord('q')) or (not ret):
            print("tiempo total proceso: ", tiempo_acumulado)
            print("objeto 1: ", posicion_obj1, "Cantidad puntos", len(posicion_obj1))
            #print("objeto 2: ", posicion_obj2, "Cantidad puntos", len(posicion_obj2))
            guardar_coordenadas_txt(round(tiempo_acumulado, 2), cte_proporcion_cm_px, posicion_obj1, posicion_obj2)
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
                archivo.write("Tiempo      X(px)      Y(px)      X(cm)      Y(cm)\n")
                for tupla in lista_1:
                    archivo.write(f"{tupla[0]} {tupla[1]} {tupla[2]} {tupla[3]} {tupla[4]}\n")
                """
                archivo.write("\nCoordenadas objeto 2: \n")
                archivo.write("Tiempo      X(px)      Y(px)      X(cm)      Y(cm)\n")
                for tupla in lista_2:
                    archivo.write(f"{tupla[0]} {tupla[1]} {tupla[2]} {tupla[3]} {tupla[4]}\n")
                """
                    
            print(f"Texto guardado en '{ruta_archivo}' con éxito.")
        except Exception as e:
            print(f"Error al guardar el texto en '{ruta_archivo}': {str(e)}")
    else:
        print("No se ha seleccionado una carpeta de destino.")

# --------------------------------------------------------------------------

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
            iniciar_deteccion(rojo, cap, prev_y, referencia_cm)
            break
        elif color == "a":
            iniciar_deteccion(azul, cap, prev_y, referencia_cm)
            break
        elif color == "v":
            iniciar_deteccion(verde, cap, prev_y, referencia_cm)
            break
        else:
            print("Ingreso no valido\n")
            
    return cap
   # cap.release()
   # cv2.destroyAllWindows()
#cap.closeAllWindow()
