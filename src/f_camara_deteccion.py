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
from operator import itemgetter
from tkinter import filedialog
from scipy.signal import argrelmin

import f_colores as col

colores = col.lista_colores() # [negro, rojo, verde, azul, amarillo, fucsia, naranja, cian]
rojo = colores[1]

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
def deteccion_color_calibracion(f, color):
        
    brightness = 8
    contrast = 1.3
        
    hsv = cv2.cvtColor(f, cv2.COLOR_BGR2HSV)
    # Hay que ver que tan util es
    mask = cv2.addWeighted(hsv, contrast, np.zeros(hsv.shape, hsv.dtype), 0, brightness)
    mask = cv2.inRange(hsv, color[0], color[1])
        
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
    contours_sorted = sorted(contours, key=cv2.contourArea, reverse=True)[:4]
        
    for i in contours_sorted:
        area = cv2.contourArea(i)
        x, y, w, h = cv2.boundingRect(i)
        cv2.rectangle(f, (x, y), (x+w, y+h), (0, 255, 0), 1)

    return contours_sorted

def calibracion(frame, ref, oc, colcal, mostrar_calibrado):

    def unwarp(f, p):
        
        h, w = f.shape[:2]

        src = np.float32([puntos_ordenados[0],
                          puntos_ordenados[1],
                          puntos_ordenados[2],
                          puntos_ordenados[3]])

        dst = np.float32([(w, 0),
                        (0, 0),
                        (w, h),
                        (0, h)])
                        
        M = cv2.getPerspectiveTransform(src, dst)

        warped = cv2.warpPerspective(f, M, (w, h), flags=cv2.INTER_LINEAR)
        
        resized_frame = cv2.resize(warped, (350, 350), interpolation = cv2.INTER_LINEAR)
        
        return resized_frame
    
    # ----------------------------------------------------------------------
    
    centros_puntos_calibracion = centros(deteccion_color_calibracion(frame, colcal), oc)
    
    for c in centros_puntos_calibracion:
        cv2.circle(frame, c, 1, (0, 255, 255), -1)
    
    puntos_ordenados = ordenar_puntos(centros_puntos_calibracion)

    if mostrar_calibrado:
        frame_tr = unwarp(frame, puntos_ordenados)        
        k = (ref[0] / frame_tr.shape[1], ref[1] / frame_tr.shape[0]) 
        frame_tr = cv2.flip(frame_tr, 1)
        centro_frame = (int(frame_tr.shape[1]/2), int(frame_tr.shape[0]/2))
        
        cv2.circle(frame_tr, centro_frame, 5, (0, 0, 255 ), -1)
        
        return k, centro_frame, frame_tr
    
    else:
        x = interseccion(puntos_ordenados)
        
        if x != None:
            centro_frame = (int(x[0]), int(x[1]))
        else:
            centro_frame = (int(frame.shape[1]/2), int(frame.shape[0]/2))
        
        vector_puntos_inferiores = (puntos_ordenados[2][0] - puntos_ordenados[3][0], puntos_ordenados[2][1] - puntos_ordenados[3][1])
        vector_puntos_lado_izquierdo = (puntos_ordenados[0][0] - puntos_ordenados[2][0], puntos_ordenados[0][1] - puntos_ordenados[2][1]) 
        
        distancia_h = np.sqrt(vector_puntos_inferiores[0]**2 + vector_puntos_inferiores[1]**2)
        distancia_v = np.sqrt(vector_puntos_lado_izquierdo[0]**2 + vector_puntos_lado_izquierdo[1]**2)
        
        k = (ref[0] / distancia_h, ref[1] / distancia_v)
        
        cv2.circle(frame, centro_frame, 5, (0, 0, 255 ), -1)
        
        return k, centro_frame, frame

# --------------------------------------------------------------------------

def deteccion_objeto(frame, c, dos_objetos):
    # Vale la pena usarla? Es mucha la mejora a cambio de reducir el rendimiento?
    def filtro_color(frame, color):
        mask = cv2.inRange(frame, color[0], color[1]) # _, lower, higher
        mask = cv2.erode(mask, None, iterations = 1)
        mask = cv2.dilate(mask, None, iterations = 1)
            
        return mask
        
    # Deteccion del objeto (por color)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = filtro_color(hsv, c)
    # mask = cv2.inRange(frame, color[0], color[1])

    # Dibujo del contorno de la figura más grande
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours_sorted = sorted(contours, key=cv2.contourArea, reverse=True)
        
    # Quiero remarcar mas de un objeto
    if len(contours_sorted) > 0:
        area = cv2.contourArea(contours_sorted[0])
        nuevoContorno = cv2.convexHull(contours_sorted[0])
        cv2.drawContours(frame, [nuevoContorno], -1, (200,5,255), 1)

        if len(contours_sorted) > 1 and dos_objetos:
            area2 = cv2.contourArea(contours_sorted[1])
            nuevoContorno2 = cv2.convexHull(contours_sorted[1])
            cv2.drawContours(frame, [nuevoContorno2], -1, (200,5,255), 1)

    return contours_sorted

# --------------------------------------------------------------------------

def seguimiento_objeto(frame, c, origen, proporcion, dos_objetos):
    contours_sorted = deteccion_objeto(frame, c, dos_objetos)

    # Centro del objeto
    centro_objeto = centros(contours_sorted, origen)[0]
    cv2.circle(frame, centro_objeto, 2, (50, 255, 0), -1)

    # Mido posicion y distancia respecto al centro del frame
    posicion = (centro_objeto[0] - origen[0], origen[1] - centro_objeto[1])
    posicion_cm = (round(posicion[0] * proporcion[0], 4), round(posicion[1] * proporcion[1], 4))

    distancia_centro = int(np.sqrt(posicion[0]**2 + posicion[1]**2))
    distancia_centro_cm = round(distancia_centro * proporcion[0], 4)
            
    return centro_objeto, posicion, posicion_cm, distancia_centro, distancia_centro_cm

# --------------------------------------------------------------------------

def iniciar_deteccion(color, color2, colcal, cap, ref, mostrar_calibrado, mostrar_frame, directorio_fuente, dos_objetos):
    
    def interfaz_texto(frame, pos, pos_cm, d, d_cm, ct):
        h, w = frame.shape[:2]
        
        cv2.putText(frame, f"Posicion x: {pos[0]} y: {pos[1]} px  x: {pos_cm[0]} y: {pos_cm[1]} cm", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)
        cv2.putText(frame, f"Distancia al centro : {d} px  {d_cm} cm", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0  ), 1)
        
        cv2.putText(frame, "'Q' para salir", (10, h - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)
        # cv2.putText(frame, f"FPS: {fps:.2f}", (w - 80, h - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)
        
        # cv2.circle(frame, ct, 5, (0, 0, 255 ), -1)
        
    # ----------------------------------------------------------------------
    posicion_objeto = []
    posicion_objeto2 = []
    
    tiempo_acumulado = 0
    cte_proporcion_cm_px = 0
    centro_plano = (0, 0)
    
    reproduccion_pausada = False
    
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        
    while True:
        
        if not reproduccion_pausada:
            ret, frame = cap.read()
            
            # Condicion de corte
            if (cv2.pollKey() & 0xFF == ord('q')) or (not ret):
                print("pressed q")
                t, x, y = [], [], []
                for p in posicion_objeto:
                    t.append(p[0])
                    x.append(p[3])
                    y.append(p[4])
                if len(t) <= 3:
                    t += [0, 0, 0, 0]
                    x += [0, 0, 0, 0]
                    y += [0, 0, 0, 0]
                
                if dos_objetos:
                    t2, x2, y2 = [], [], []
                    for p in posicion_objeto2:
                        t2.append(p[0])
                        x2.append(p[3])
                        y2.append(p[4])
                    if len(t) <= 3:
                        t2 += [0, 0, 0, 0]
                        x2 += [0, 0, 0, 0]
                        y2 += [0, 0, 0, 0]
                    guardar_coordenadas_txt(tiempo_acumulado, cte_proporcion_cm_px, posicion_objeto2, "Guardar archivo de texto con coordenadas Objeto 2", directorio_fuente)
                    graficar(t2[:-3], x2[:-3], y2[:-3], "Grafico posicion Objeto 2") # :-3
                
                guardar_coordenadas_txt(tiempo_acumulado, cte_proporcion_cm_px, posicion_objeto, "Guardar archivo de texto con coordenadas Objeto 1", directorio_fuente)
                graficar(t[:-3], x[:-3], y[:-3], "Grafico posicion Objeto 1") # :-3
                cap.release()
                cv2.destroyAllWindows()
                break
                
            try:
                h, w = frame.shape[:2]
                centro_plano = (int(w/2), int(h/2))
            except AttributeError:
                print("frame None", centro_plano)
            
            # Calibracion: obtengo frame calibrado
            cte_proporcion_cm_px, origen_coordenadas, frame_calibrado = calibracion(frame, ref, centro_plano, colcal, mostrar_calibrado) # Fijado para hacer calibracion con rojo

            # Obtengo tiempos correctos, solo para archivos de video
            if mostrar_calibrado:
                centro_objeto, posicion, posicion_cm, distancia_centro, distancia_centro_cm = seguimiento_objeto(frame_calibrado, color, origen_coordenadas, cte_proporcion_cm_px, dos_objetos)
                # si detecto 2 colores? condicion
                if dos_objetos:
                    centro_objeto2, posicion2, posicion_cm2, distancia_centro2, distancia_centro_cm2 = seguimiento_objeto(frame_calibrado, color2, origen_coordenadas, cte_proporcion_cm_px, dos_objetos)
                tiempo_reproduccion = cap.get(cv2.CAP_PROP_POS_MSEC)/1000
                
                if mostrar_frame:
                    # interfaz_texto(frame_calibrado, posicion, posicion_cm, distancia_centro, distancia_centro_cm, origen_coordenadas)
                    cv2.imshow('frame', frame_calibrado)
            
            else:
                # puse frame_calibrado aca tambien. las mediciones se hacen con frame_calibrado
                centro_objeto, posicion, posicion_cm, distancia_centro, distancia_centro_cm = seguimiento_objeto(frame_calibrado, color, origen_coordenadas, cte_proporcion_cm_px, dos_objetos)
                if dos_objetos:
                    centro_objeto2, posicion2, posicion_cm2, distancia_centro2, distancia_centro_cm2 = seguimiento_objeto(frame_calibrado, color2, origen_coordenadas, cte_proporcion_cm_px, dos_objetos)
                tiempo_reproduccion = cap.get(cv2.CAP_PROP_POS_MSEC)/1000

                if mostrar_frame:
                    # interfaz_texto(frame, posicion, posicion_cm, distancia_centro, distancia_centro_cm, origen_coordenadas)
                    cv2.imshow('frame', frame)
            
            print("Procesando ", posicion_objeto, posicion_objeto2)
            posicion_objeto.append((round(tiempo_reproduccion, 2), posicion[0], posicion[1], posicion_cm[0], posicion_cm[1], distancia_centro, distancia_centro_cm))
            if dos_objetos:
                posicion_objeto2.append((round(tiempo_reproduccion, 2), posicion2[0], posicion2[1], posicion_cm2[0], posicion_cm2[1], distancia_centro2, distancia_centro_cm2))
            
# --------------------------------------------------------------------------  

def guardar_coordenadas_txt(tiempo_a, cte_cal, lista_1, titulo, directorio_fuente):
    root = tk.Tk()
    root.withdraw()
    
    directorio_destino = filedialog.askdirectory(title=titulo, initialdir=directorio_fuente)
    
    date = time.strftime("%a, %d %b %Y %H:%M:%S", time.gmtime())
    nombre_archivo = date[5:7]+"-"+date[8:11]+"-"+date[12:16]+"_"+date[17:25]+".txt"

    if directorio_destino:
        ruta_archivo = f"{directorio_destino}/{nombre_archivo}"
        tiempo = (lista_1[:-3].pop())[0]
        try:
            with open(ruta_archivo, 'w') as archivo:
                archivo.write(f"{date}\n")
                archivo.write(f"Tiempo total del proceso: {tiempo}\n")
                archivo.write("\nCoordenadas objeto 1: \n")
                archivo.write("Tiempo      X(px)      Y(px)      X(cm)      Y(cm)      Dist. centro (px)      Dist. centro (cm)\n")
                for tupla in lista_1[:-3]:
                    archivo.write(f"{tupla[0]} {tupla[1]} {tupla[2]} {tupla[3]} {tupla[4]} {tupla[5]} {tupla[6]}\n")
                                    
            print(f"Texto guardado en '{ruta_archivo}' con éxito.")
        except Exception as e:
            print(f"Error al guardar el texto en '{ruta_archivo}': {str(e)}")
    else:
        print("No se ha seleccionado una carpeta de destino.")

# --------------------------------------------------------------------------

def graficar(t, x, y, titulo_grafico):
    leyenda = ['Valor medio', 'Altura minima Promedio']
    
    y_np = np.array(y)
    min_indices_y = argrelmin(y_np)[0]
    y_min = y_np[min_indices_y]
    promedio_x = np.average(x)
    promedio_min_y = np.average(y_min)
    
    linea_vm_x = ((t[0], t[len(t)-1]), (promedio_x, promedio_x)) # (x0, xf)
    linea_vmin_y= ((t[0], t[len(t)-1]), (promedio_min_y, promedio_min_y))
    print("Promedios: ", np.average(x), np.average(y_min))
    
    fig, axs = plt.subplots(1, 2, layout='constrained')
    plt.suptitle(titulo_grafico)
    
    # Grafico x(t)
    axs[0].plot(t, x, 'k', label="Posicion x(t)")
    axs[0].plot(linea_vm_x[0], linea_vm_x[1], 'r', label=f"{leyenda[0]}={promedio_x:.2f}")
    axs[0].set_xlabel('t')
    axs[0].set_ylabel('x(t)')
    axs[0].grid(True, linestyle = '-.')
    axs[0].legend()
    
    # Grafico y(t)
    axs[1].plot(t, y, 'k', label="Posicion y(t)")
    axs[1].plot(linea_vmin_y[0], linea_vmin_y[1], 'r', label=f"{leyenda[1]}={promedio_min_y:.2f}")
    axs[1].set_xlabel('t')
    axs[1].set_ylabel('y(t)')
    axs[1].grid(True, linestyle = '-.')
    axs[1].legend()
    
    fig.align_labels()
    
    plt.show()
    
# --------------------------------------------------------------------------

def hard_inicio(c, r, mostrar_calibrado, mostrar_frame, nombre_archivo):
    cap = cv2.VideoCapture(0)
    iniciar_deteccion(c, cap, r, mostrar_calibrado, mostrar_frame, nombre_archivo)

