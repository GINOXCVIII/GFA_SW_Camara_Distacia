#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 23 17:13:53 2023

@author: imano-oh
"""

import numpy as np

def encontrar_interseccion(p1, p2, p3, p4):
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

# Ejemplo de uso
punto1 = (774, 346)
punto2 = (2845, 427)
punto3 = (1097, 2255)
punto4 = (2405, 2246)

resultado = encontrar_interseccion(punto1, punto2, punto3, punto4)

if resultado:
    print(f"La intersección es en el punto {resultado}")
else:
    print("Las rectas son paralelas y no tienen intersección.")
