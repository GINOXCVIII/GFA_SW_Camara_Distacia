#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 30 15:39:40 2023

@author: imano-oh
"""

import cv2
import numpy as np
import numpy.linalg as npla
from operator import itemgetter, attrgetter

low_red = np.array([159, 50, 70])
high_red = np.array([180, 255, 255])

rojo = (low_red, high_red, "Rojo")

def detectar_rojo(frame, color):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, color[0], color[1])
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    contours_sorted = sorted(contours, key=cv2.contourArea, reverse=True)[:4]
    
    for i in contours_sorted:
        area = cv2.contourArea(i)
        nuevoContorno = cv2.convexHull(i)
        cv2.drawContours(frame, [nuevoContorno], -1, (200,5,255), 2)
    
    return contours_sorted

def interseccion(p1, p2, p3, p4):
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

def centros(frame, cont):
    M = []
    if len(cont) >= 4:
        for c in cont:
            # Calcular centro de cada contorno
            Mc = cv2.moments(c)
            if Mc['m00'] == 0:
                cx = 0
                cy = 0
            else:
                cx = int(Mc['m10'] / Mc['m00'])
                cy = int(Mc['m01'] / Mc['m00'])
            M.append((cx, cy))
        #print("M =", M)
    else:
        #print("M =", [(0, 0), (0, 0), (0,0), (0,0)])
        M = [(0, 0), (0, 0), (0,0), (0,0)]
    
    return M

def unwarp(img, puntos):
    
    def ordenar_puntos(puntos):
        # Separo de a dos: los de y mas chico (que mas arriba estan) y los de y mas grande (mas abajo)
        puntos_inferior = sorted(puntos, key=itemgetter(1), reverse=True)[:2]
        puntos_superior = sorted(puntos, key=itemgetter(1))[:2]
        
        # Ordeno segun la distancia en x respecto al origen (ordeno de izquierda a derecha)
        puntos_inferior = sorted(puntos_inferior, key=itemgetter(0))
        puntos_superior = sorted(puntos_superior, key=itemgetter(0))
        
        puntos_ordenados = puntos_superior + puntos_inferior
        
        return puntos_ordenados

    h, w = img.shape[:2]
    
    puntos_ordenados = ordenar_puntos(puntos)

    src = np.float32([puntos_ordenados[0],
                      puntos_ordenados[1],
                      puntos_ordenados[2],
                      puntos_ordenados[3]])
                      
    # print("Dimensiones wxh", w, "x", h)
    dst = np.float32([(w, 0),
                    (0, 0),
                    (w, h),
                    (0, h)])
    
    # use cv2.getPerspectiveTransform() to get M, the transform matrix, and Minv, the inverse
    M = cv2.getPerspectiveTransform(src, dst)
    
    print("Matriz de transformacion A:\n", M, "\n")
    # M_1 = npla.inv(M)
    # print("Matriz inversa:\n", M_1, "\n")

    # use cv2.warpPerspective() to warp your image to a top-down view
    warped = cv2.warpPerspective(img, M, (w, h), flags=cv2.INTER_LINEAR)
    
    return warped

def test_captura(cam):
    cap = cv2.VideoCapture(cam)
    try:
        w = cap.get(3)
        h = cap.get(4)
    except ValueError:
        w, h = 1, 1
    
    # print(w, h)
    
    while(True):
    
        ret, frame = cap.read()
        
        if not ret:
            cap.release()
            cv2.destroyAllWindows()
            break
        
        contornos = detectar_rojo(frame, rojo)
        
        lista_de_puntos = centros(frame, contornos)
        frame_cal = unwarp(frame, lista_de_puntos)
        frame_cal = cv2.flip(frame_cal, 0)
        
        x = interseccion(lista_de_puntos[0], lista_de_puntos[1], lista_de_puntos[2], lista_de_puntos[3])
        if x != None:
            px_x = (int(x[0]), int(x[1]))
            print("Interseccion:", x, px_x, "\n")
            print("---------x---------\n") 
        else:
            px_x = (0, 0)
        
        cv2.circle(frame, px_x, 3, (0, 255, 255), -1)
        cv2.putText(frame, f"{px_x}", px_x, cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 220, 255), 2)
        
        cv2.putText(frame, f"M[0]", lista_de_puntos[0], cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 220, 255), 2)
        cv2.putText(frame, f"M[1]", lista_de_puntos[1], cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 220, 255), 2)
        cv2.putText(frame, f"M[2]", lista_de_puntos[2], cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 220, 255), 2)
        cv2.putText(frame, f"M[3]", lista_de_puntos[3], cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 220, 255), 2)
        
        cv2.circle(frame_cal, (int(w/2), int(h/2)), 3, (0, 255, 255), -1)
        cv2.putText(frame_cal, f"Centro", (int(w/2), int(h/2)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 220, 255), 2)
        
        resized_frame = cv2.resize(frame_cal, (500, 500), interpolation = cv2.INTER_LINEAR)
        
        cv2.imshow('frame', frame)
        cv2.imshow('resized_frame', resized_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

test_captura(0)
# test_captura("/home/pi/Documents/pruba.mp4")

# HACER LAS MEDICIONES EN LA IMAGEN CONVERTIDA Y REESCALADA. ¿FUNCIONARÁ?
