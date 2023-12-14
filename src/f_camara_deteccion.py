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

colores = col.lista_colores() # [rojo, verde, azul, amarillo, fucsia, naranja, cian]
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

def ordenar_puntos(puntos):
    
    # Separo segun distancia en y, obtengo los dos puntos de arriba y los de abajo
    puntos_inferior = sorted(puntos, key=itemgetter(1), reverse=True)[:2]
    puntos_superior = sorted(puntos, key=itemgetter(1))[:2]
    
    # Ordeno segun la distancia en x respecto al origen (ordeno de izquierda a derecha)
    puntos_inferior = sorted(puntos_inferior, key=itemgetter(0))
    puntos_superior = sorted(puntos_superior, key=itemgetter(0))
        
    puntos_ordenados = puntos_superior + puntos_inferior
        
    return puntos_ordenados

# --------------------------------------------------------------------------

def interseccion(puntos):
    
    puntos_ordenados = ordenar_puntos(puntos)
    p1 = puntos_ordenados[0]
    p2 = puntos_ordenados[3]
    p3 = puntos_ordenados[2]
    p4 = puntos_ordenados[1]
    
    # Definir las ecuaciones de las rectas en la forma ax + by = c
    a1, b1, c1 = p2[1] - p1[1], p1[0] - p2[0], p1[0] * (p2[1] - p1[1]) - p1[1] * (p2[0] - p1[0])
    a2, b2, c2 = p4[1] - p3[1], p3[0] - p4[0], p3[0] * (p4[1] - p3[1]) - p3[1] * (p4[0] - p3[0])

    # Construir el sistema de ecuaciones lineales
    sistema_ecuaciones = np.array([[a1, b1], [a2, b2]])
    terminos_independientes = np.array([c1, c2])

    # Resolver el sistema de ecuaciones
    try:
        interseccion = np.linalg.solve(sistema_ecuaciones, terminos_independientes)
        return tuple(interseccion)
    except np.linalg.LinAlgError:
        # Las rectas son paralelas y no tienen intersección
        return None

# --------------------------------------------------------------------------

def centros(cont, oc):
    M = []
    if len(cont) >= 1:
        # Ordenar los contornos por área (de mayor a menor)
        list_cont = sorted(cont, key=cv2.contourArea, reverse=True)[:4]
        
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
        if len(cont) < 4:
            for i in range(4 - len(cont)):
                M.append(oc)
        return M
    else:
        for i in range(4):
            M.append(oc)
        return M

# --------------------------------------------------------------------------    
"""
def calibracion(frame, camara, color, ref, oc):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, color[0], color[1])
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    contours_sorted = sorted(contours, key=cv2.contourArea, reverse=True)[:2]
    for i in contours_sorted:
            area = cv2.contourArea(i)
            x, y, w, h = cv2.boundingRect(i)
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 1)
    
    l_contours = centros(contours_sorted, oc)# + [oc, oc]
    
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
"""
def calibracion(frame, ref, oc):
    
    def deteccion_rojo(f):
        
        hsv = cv2.cvtColor(f, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, rojo[0], rojo[1])
        contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        contours_sorted = sorted(contours, key=cv2.contourArea, reverse=True)[:4]
        
        for i in contours_sorted:
            area = cv2.contourArea(i)
            x, y, w, h = cv2.boundingRect(i)
            cv2.rectangle(f, (x, y), (x+w, y+h), (0, 255, 0), 1)
        
        return contours_sorted
        
    def unwarp(f, p):
        
        h, w = f.shape[:2]

        src = np.float32([puntos_ordenados[0],
                          puntos_ordenados[1],
                          puntos_ordenados[2],
                          puntos_ordenados[3]])
                          
        # print("Dimensiones wxh", w, "x", h)
        dst = np.float32([(w, 0),
                        (0, 0),
                        (w, h),
                        (0, h)])
                        
        M = cv2.getPerspectiveTransform(src, dst)

        warped = cv2.warpPerspective(f, M, (w, h), flags=cv2.INTER_LINEAR)
        
        resized_frame = cv2.resize(warped, (640, 640), interpolation = cv2.INTER_LINEAR)
        
        return resized_frame
    
    centros_puntos_calibracion = centros(deteccion_rojo(frame), oc)
    
    for c in centros_puntos_calibracion:
        cv2.circle(frame, c, 1, (0, 255, 255), -1)
    
    puntos_ordenados = ordenar_puntos(centros_puntos_calibracion)
    
    x = interseccion(puntos_ordenados)
    px_x = (int(x[0]), int(x[1]))
    
    frame_tr = unwarp(frame, puntos_ordenados)
    
    k = ref / frame_tr.shape[1]
    
    return k, px_x, frame_tr
    
# --------------------------------------------------------------------------
 
def interfaz_texto(frame, pos, pos_cm, d, d_cm, fps, px_x, oc_t, co, fc):
    h, w = frame.shape[:2]
    
    cv2.putText(frame, f"Posicion x: {pos[0]} y: {pos[1]} px  x: {pos_cm[0]} y: {pos_cm[1]} cm", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)
    cv2.putText(frame, f"Distancia al centro : {d} px  {d_cm} cm", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0  ), 1)
    
    cv2.putText(frame, "'Q' para salir", (10, h - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)
    cv2.putText(frame, f"FPS: {fps:.2f}", (w - 80, h - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)
    
    if fc:
        cv2.circle(frame, oc_t, 5, (0, 0, 255 ), -1)
        # cv2.putText(frame, f"{oc_t}", oc_t, cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)
        return 0
    else:
        cv2.circle(frame, px_x, 5, (0, 0, 255 ), -1)
        # cv2.putText(frame, f"{px_x}", px_x, cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)
        return 0
    
# --------------------------------------------------------------------------
def iniciar_deteccion(color, cap, ref, check):
    
    def filtro_color(frame, color):
        mask = cv2.inRange(frame, color[0], color[1]) # _, lower, higher
        mask = cv2.erode(mask, None, iterations = 1)
        mask = cv2.dilate(mask, None, iterations = 1)
        
        return mask
    
    posicion_objeto = []
    
    tiempo_proceso = 0
    tiempo_acumulado = 0
    cte_proporcion_cm_px = 0
    origen_coordenadas = (0, 0)
        
    while True:
        
        # tic = time.time()
        start_time = cv2.getTickCount()
        
        ret, frame = cap.read()
        
        # Condicion de corte
        if (cv2.waitKey(1) & 0xFF == ord('q')) or (not ret):
            t, x, y = [], [], []
            for p in posicion_objeto:
                t.append(p[0])
                x.append(p[3])
                y.append(p[4])
            guardar_coordenadas_txt(tiempo_acumulado, proporcion, posicion_objeto)
            graficar(t, x, y)
            cap.release()
            cv2.destroyAllWindows()
            break
            
        try:
            h, w = frame.shape[:2]
            origen_coordenadas = (int(w/2), int(h/2))
        except AttributeError:
            print("frame None", origen_coordenadas)
        
        # Calibracion: obtengo frame calibrado
        proporcion, centro_plano, frame_calibrado = calibracion(frame, ref, origen_coordenadas) # Fijado para hacer calibracion con rojo
        origen_transformado = (int(frame_calibrado.shape[0]/2), int(frame_calibrado.shape[1]/2))
        
        # Deteccion del objeto (por color)
        hsv = cv2.cvtColor(frame_calibrado, cv2.COLOR_BGR2HSV)
        mask = filtro_color(hsv, color)
        
        # Dibujo del contorno de la figura más grande
        contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours_sorted = sorted(contours, key=cv2.contourArea, reverse=True)
        
        if len(contours_sorted) > 0:
            area = cv2.contourArea(contours_sorted[0])
            nuevoContorno = cv2.convexHull(contours_sorted[0])
            cv2.drawContours(frame_calibrado, [nuevoContorno], -1, (200,5,255), 1)
        
        # Centro del objeto
        centro_objeto = centros(contours_sorted, origen_transformado)[0]
        cv2.circle(frame_calibrado, centro_objeto, 2, (50, 255, 0), -1)

        # Mido posicion y distancia con el centro del frame calibrado
        posicion = (centro_objeto[0] - origen_transformado[0], origen_transformado[1] - centro_objeto[1])
        posicion_cm = (round(posicion[0] * proporcion, 4), round(posicion[1] * proporcion, 4))
           
        distancia_centro = int(np.sqrt(posicion[0]**2 + posicion[1]**2))
        distancia_centro_cm = round(distancia_centro * proporcion, 4)
               
        # Calculo FPS reproduccion
        time_taken = (cv2.getTickCount() - start_time) / cv2.getTickFrequency()
        fps = 1.0 / time_taken
        
        # tiempo_proceso = time.time() - tic
        tiempo_proceso = fps ** (-1)

        tiempo_acumulado += tiempo_proceso

        if check == False:
            jajaja = interfaz_texto(frame, posicion, posicion_cm, distancia_centro, distancia_centro_cm, fps, centro_plano, origen_transformado, centro_objeto, False)
            cv2.imshow('frame', frame)
        else:
            jajaja = interfaz_texto(frame_calibrado, posicion, posicion_cm, distancia_centro, distancia_centro_cm, fps, centro_plano, origen_transformado, centro_objeto, True)
            cv2.imshow('frame', frame_calibrado)            
        
        # Revisar el tiempo. El tiempo acumulado no es el mismo que la duracion de un video
        posicion_objeto.append((round(tiempo_acumulado, 2), posicion[0], posicion[1], posicion_cm[0], posicion_cm[1], distancia_centro, distancia_centro_cm))
        
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
    date = time.strftime("%a, %d %b %Y %H:%M:%S", time.gmtime())
    nombre_plot = date[5:7]+"-"+date[8:11]+"-"+date[12:16]+" "+date[17:25]
    
    fig = plt.figure(tight_layout = True)
    gs = gridspec.GridSpec(1, 2)

    plot = [(t, x), (t, y)]
    titles = ['x(t)', 'y(t)']

    for i in range(2):
        p = plot[i]       
        ax = fig.add_subplot(gs[0, i])
        ax.grid(True, linestyle = '-.')
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
