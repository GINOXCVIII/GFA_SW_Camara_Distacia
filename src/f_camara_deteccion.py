#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 30 17:03:40 2023

@author: imano-oh
"""

import cv2
import numpy as np
import pyautogui

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
# cap = cv2.VideoCapture(3) # Revisar el tema de los indices de camara; cambian por alguna razón
# cap = cv2.VideoCapture(video_path)

prev_y = 0
reference_point = (320, 240)  # Coordenadas del punto de referencia. Es el centro de la imagen pues la resolucion es 640x480
referencia_cm = 1

cte_proporcion_cm_px = 0

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
        
    while True:
        
        start_time = cv2.getTickCount()
        
        ret, frame = cap.read()
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        #mask = cv2.inRange(hsv, lower_pink, upper_pink)
        mask = cv2.inRange(hsv, color[0], color[1]) # _, lower, higher
        contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Agarro solo los dos más grandes, si no me explota la PC
        contours_sorted = sorted(contours, key=cv2.contourArea, reverse=True)[:2]
    
        for i in contours_sorted:
            area = cv2.contourArea(i)
            if area > 500:
                x, y, w, h = cv2.boundingRect(i)
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                if y < p_y:
                    pyautogui.press('space')
                p_y = y
    
        cv2.circle(frame, reference_point, 5, (0, 0, 255 ), -1)
        
        l_contours = centros(contours)
        
        c1 = l_contours[0]
        c2 = l_contours[1]
        # Marcar centro del marco (+ centro de la imagen)
        cv2.circle(frame, (c1[0], c1[1]), 3, (0, 255, 0), -1)
        cv2.circle(frame, (c2[0], c2[1]), 3, (0, 255, 0), -1)
        
        # Mostrar posicion centro de los 2 rectangulos mas grandes
        cv2.putText(frame, f"cx1 : {c1[0] - reference_point[0]} px, cy1 : {-1*(c1[1] - reference_point[1])} px", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)
        cv2.putText(frame, f"cx2 : {c2[0] - reference_point[0]} px, cy2 : {-1*(c2[1] - reference_point[1])} px", (10, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 255), 1)
    
        dist_c1_c2 = np.sqrt((c1[0] - c2[0])**2 + (c1[1] - c2[1])**2)
        # Imprimir en pantalla distancia entre c1 y c2
        cv2.putText(frame, f"Distancia c1 a c2 : {dist_c1_c2} px", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0  ), 1)
        
        # Calibracion
        cte_proporcion_cm_px = calibracion(frame, cap, rojo, ref) # Fijado para hacer calibracion con rojo
        dist_c1_c2_cm = dist_c1_c2 * cte_proporcion_cm_px
        cv2.putText(frame, f"Distancia c1 a c2 : {dist_c1_c2_cm} cm", (10, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0  ), 1)
        
        cv2.putText(frame, "Oprimir 'q' para salir", (10, 475), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)
    
        # cv2.imshow('frame', frame)
        
        # Calculo FPS de reproduccion
        time_taken = (cv2.getTickCount() - start_time) / cv2.getTickFrequency()
        fps = 1.0 / time_taken
        # print(f"FPS: {fps:.2f}")
        cv2.putText(frame, f"FPS: {fps:.2f}", (560, 475), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)
        
        cv2.imshow('frame', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            cap.release()
            cv2.destroyAllWindows()
            break
        
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
