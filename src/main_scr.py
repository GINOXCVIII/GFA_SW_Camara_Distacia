#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep  7 16:55:48 2023

@author: imano-oh
"""

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QSlider, QListWidget, QListWidgetItem, QLineEdit, QFileDialog, QCheckBox
from PyQt5.QtGui import QColor, QPixmap
from PyQt5.QtCore import Qt

import sys
import cv2
import time
import os
import numpy as np
import f_busqueda_camaras as fbc
import f_camara_deteccion as fcd
import f_grabar_video as fgv

# ------------------------------------------------------------------------------------------------
bocchi = ["b","o","c","c","h","i","z","a","r","o","c","k"]
indices_camaras = fbc.camaras_indices()
nombres_camaras = fbc.camaras_nombres()
camaras = []
colores = fcd.get_lista_colores()

colores_nombres = []
for c in colores:
        colores_nombres.append(c[2])

if len(indices_camaras) == len(nombres_camaras):
    for i in range(len(indices_camaras)):
        camara = str(indices_camaras[i]) + ": " + nombres_camaras[i]
        camaras.append(camara)
        
videopath = "Archivo de video"
camara = "Camara"

# ------------------------------------------------------------------------------------------------
class MiVentana(QMainWindow):
    def __init__(self):
        super().__init__()
        w = 345
        h = 380
        cam_seleccionada = -1
        col_seleccionado = -1
        ref_seleccionada = -1
        
        self.color_1 = [11, 0, 0]
        self.color_2 = [11, 0, 0]
        
        self.mostrar_calibrado = False
        self.guardar_video = False
        
        self.setWindowTitle("tonChan")  # Establecer el título de la ventana
        self.setGeometry(100, 100, w, h)  # Establecer la posición y el tamaño de la ventana
        self.setFixedSize(w, h)
        
        # Lista de camaras
        self.listView = QListWidget(self)
        self.listView.setGeometry(QtCore.QRect(10, h-340, 151, 161))
        self.listView.setObjectName("listView")
        self.listView.addItem(camara)

        """
        for c in camaras:
            item = QListWidgetItem(c)
            self.listView.addItem(item)
        """

        self.listView.addItem(videopath)
            
        self.label_2 = QtWidgets.QLabel("Fuentes", self)
        self.label_2.setGeometry(QtCore.QRect(10, h-365, 141, 20))
        self.label_2.setObjectName("label_2")
        
        self.listView.itemClicked.connect(self.seleccion_fuente)
        
        # Lista de colores
        self.listView_2 = QListWidget(self)
        self.listView_2.setGeometry(QtCore.QRect(180, h-340, 151, 161))
        self.listView_2.setObjectName("listView_2")
        for c in colores_nombres[1:]:
            item = QListWidgetItem(c)
            self.listView_2.addItem(item)
            
        self.label_3 = QtWidgets.QLabel("Colores", self)
        self.label_3.setGeometry(QtCore.QRect(180, h-365, 141, 20))
        self.label_3.setObjectName("label_3")
        
        self.listView_2.itemClicked.connect(self.seleccion_col)

        # Cuadro de entrada de la referencia
        self.lineEdit = QLineEdit(self)
        self.lineEdit.setValidator(QtGui.QDoubleValidator()) # Solo se pueden ingresar numeros
        self.lineEdit.setGeometry(QtCore.QRect(165, h-165, 78, 22))
        self.lineEdit.setObjectName("lineEdit")
        
        self.label = QtWidgets.QLabel("Longitud lado inferior", self)
        self.label.setGeometry(QtCore.QRect(10, h-165, 156, 21))
        self.label.setObjectName("label")
        
        self.pushButton_2 = QtWidgets.QPushButton("Aplicar", self)
        self.pushButton_2.setGeometry(QtCore.QRect(253, h-165, 80, 22))
        self.pushButton_2.setObjectName("pushButton_2")
        
        self.pushButton_2.clicked.connect(self.validar_ingreso_referencia)
        
        # Checkbox 
        # para mostrar o no imagen calibrada
        self.checkbox_mostrar_calibrado = QCheckBox("Mostrar imagen calibrada", self)
        self.checkbox_mostrar_calibrado.setGeometry(10, h-130, w-1, 21)
        
        self.checkbox_mostrar_calibrado.stateChanged.connect(self.actualizar_mostrar_calibrado)
        
        # para guardar video
        self.checkbox_guardar_video = QCheckBox("Guardar archivo video (solo Camara)", self)
        self.checkbox_guardar_video.setGeometry(10, h-100, w-1, 21)
        
        self.checkbox_guardar_video.stateChanged.connect(self.actualizar_guadar_video)

        # Boton para iniciar la captura
        self.pushButton = QtWidgets.QPushButton("Iniciar", self)
        self.pushButton.setGeometry(QtCore.QRect(132, h-70, 80, 22))
        self.pushButton.setObjectName("pushButton")
        
        self.pushButton.clicked.connect(self.iniciar_captura)

# --------------------------------------------------------------------------

    def seleccion_fuente(self, item):
        item_text = item.text()
        if item_text == videopath:
            self.seleccion_videopath()
        else:
            self.seleccion_cam(item)
        
    def seleccion_cam(self, item):
        # Hacer un chequeo por si no hay camara
        print("camara")
        self.cam_seleccionada = camara
        
    def seleccion_videopath(self):
        print("videopath")
        self.cam_seleccionada = videopath
    
    def seleccion_col(self, item):
        seleccion = item.text()
        i = colores_nombres.index(seleccion)
        self.color_1 = colores[i][0]
        self.color_2 = colores[i][1]
        self.col_seleccionado = self.tupla_color(self.color_1, self.color_2)
        
        print(f"Color: {seleccion}") 
        
    def validar_ingreso_referencia(self):
        rfs = self.lineEdit.text()
        # Hacer una comprobacion por si se ingresa una coma en lugar de un punto
        # Hacer comprobacion cuando no se ingresa nada. Si se apreta Aplicar, se cierra
        self.ref_seleccionada = abs(float(rfs))
        print(f"Valor ingresado: {rfs} Numerico: {self.ref_seleccionada}")
        
    def iniciar_captura(self):
        date = time.strftime("%a, %d %b %Y %H:%M:%S", time.gmtime())
        nombre_archivo = date[5:7]+"-"+date[8:11]+"-"+date[12:16]+"_"+date[17:25]
        
        # self.col_seleccionado = self.tupla_color(self.color_1, self.color_2)
        print(self.col_seleccionado)
        
        if self.col_seleccionado != -1 and self.ref_seleccionada != -1:
            
            if self.cam_seleccionada == videopath:
                self.cam_seleccionada = self.cargar_archivo_video()
                cap = cv2.VideoCapture(self.cam_seleccionada)
                fcd.iniciar_deteccion(self.col_seleccionado, cap, self.ref_seleccionada, self.mostrar_calibrado, True, nombre_archivo)
            
            elif self.cam_seleccionada == camara:
                if self.guardar_video:
                        directorio = self.guardar_archivo_video()
                        ruta_video = fgv.captura_video(self.col_seleccionado, directorio, self.ref_seleccionada, self.mostrar_calibrado)
                        cap = cv2.VideoCapture(ruta_video)
                        fcd.iniciar_deteccion(self.col_seleccionado, cap, self.ref_seleccionada, self.mostrar_calibrado, False, nombre_archivo)
                elif not self.guardar_video:
                        directorio = '/tmp'
                        ruta_video = fgv.captura_video(self.col_seleccionado, directorio, self.ref_seleccionada, self.mostrar_calibrado)
                        cap = cv2.VideoCapture(ruta_video)
                        fcd.iniciar_deteccion(self.col_seleccionado, cap, self.ref_seleccionada, self.mostrar_calibrado, False, nombre_archivo)
                        os.remove(ruta_video)
                        # fcd.hard_inicio(self.col_seleccionado, self.ref_seleccionada, self.mostrar_calibrado, True, nombre_archivo) # Una abominacion, pero anda por ahora
                        # Se cuelga antes de graficar
                """
            
            elif self.cam_seleccionada != -1:
                cap = cv2.VideoCapture(self.cam_seleccionada)
                fcd.iniciar_deteccion(self.col_seleccionado, cap, 0, self.ref_seleccionada)
                """
        else:
            print("ganso, rellena todo")
            # Tengo que hacer algun feedback para indicar que faltan cosas

    def cargar_archivo_video(self):
        opciones = QFileDialog.Options()
        opciones |= QFileDialog.ReadOnly  # Opcional: abrir el archivo en modo solo lectura

        archivo, _ = QFileDialog.getOpenFileName(self, "Seleccionar Archivo", "", "Todos los Archivos (*)", options=opciones)

        return archivo
    
    def guardar_archivo_video(self):
        directorio = QFileDialog.getExistingDirectory(self, 'Seleccionar Directorio')
        print(f"Directorio: {directorio}")
        # self.entrada_directorio.setText(directorio)
        
        return directorio

    def tupla_color(self, c1, c2):
        return (np.array(c1), np.array(c2))
        
    def actualizar_mostrar_calibrado(self):
        self.mostrar_calibrado = self.checkbox_mostrar_calibrado.isChecked()
        print(f"Estado actualizado: {self.mostrar_calibrado}")
        
    def actualizar_guadar_video(self):
        self.guardar_video = self.checkbox_guardar_video.isChecked()
        print(f"Estado actualizado: {self.guardar_video}")

app = QApplication(sys.argv)
ventana = MiVentana()
ventana.show()
sys.exit(app.exec_())

