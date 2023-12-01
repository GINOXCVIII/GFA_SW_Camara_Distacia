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
import numpy as np
import f_busqueda_camaras as fbc
import f_camara_deteccion as fcd

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
        w = 405
        h = 450
        cam_seleccionada = -1
        col_seleccionado = -1
        ref_seleccionada = -1
        
        self.color_1 = [11, 0, 0]
        self.color_2 = [11, 0, 0]
        
        self.estado = False
        
        self.setWindowTitle("GFA")  # Establecer el título de la ventana
        self.setGeometry(100, 100, w, h)  # Establecer la posición y el tamaño de la ventana
        self.setFixedSize(w, h)
        
        # Lista de camaras
        self.listView = QListWidget(self)
        self.listView.setGeometry(QtCore.QRect(10, 40, 151, 251))
        self.listView.setObjectName("listView")
        self.listView.addItem(camara)
        """
        for c in camaras:
            item = QListWidgetItem(c)
            self.listView.addItem(item)
        """
        self.listView.addItem(videopath)
            
        self.label_2 = QtWidgets.QLabel("Fuentes", self)
        self.label_2.setGeometry(QtCore.QRect(10, 20, 141, 20))
        self.label_2.setObjectName("label_2")
        
        self.listView.itemClicked.connect(self.seleccion_fuente)
        
        # Lista de colores
        self.listView_2 = QListWidget(self)
        self.listView_2.setGeometry(QtCore.QRect(180, 40, 151, 161))
        self.listView_2.setObjectName("listView_2")
        for c in colores_nombres[1:]:
            item = QListWidgetItem(c)
            self.listView_2.addItem(item)
            
        self.label_3 = QtWidgets.QLabel("Colores", self)
        self.label_3.setGeometry(QtCore.QRect(180, 20, 141, 20))
        self.label_3.setObjectName("label_3")
        
        self.listView_2.itemClicked.connect(self.seleccion_col)
        
        # Slider de tolerancia
        self.slider_tolerancia = self.crear_slider()
        self.slider_tolerancia.setRange(0, 10)  # Rango de matiz (0-359 grados)
        self.slider_tolerancia.setGeometry(QtCore.QRect(180, 270, 151, 20))
        
        self.tolerancia_anterior = self.slider_tolerancia.value()
        
        self.etiqueta_color_1 = QLabel(self)
        self.etiqueta_color_1.setGeometry(QtCore.QRect(190, 210, 50, 50))
        self.etiqueta_color_2 = QLabel(self)
        self.etiqueta_color_2.setGeometry(QtCore.QRect(271, 210, 50, 50))
        
        self.actualizar_color()
        
        # Cuadro de entrada de la referencia
        self.lineEdit = QLineEdit(self)
        self.lineEdit.setValidator(QtGui.QDoubleValidator()) # Solo se pueden ingresar numeros
        self.lineEdit.setGeometry(QtCore.QRect(130, 330, 113, 22))
        self.lineEdit.setObjectName("lineEdit")
        
        self.label = QtWidgets.QLabel("Referencia (cm)", self)
        self.label.setGeometry(QtCore.QRect(10, 330, 141, 21))
        self.label.setObjectName("label")
        
        self.pushButton_2 = QtWidgets.QPushButton("Aplicar", self)
        self.pushButton_2.setGeometry(QtCore.QRect(253, 330, 80, 22))
        self.pushButton_2.setObjectName("pushButton_2")
        
        self.pushButton_2.clicked.connect(self.validar_ingreso_referencia)
        
        # Checkbox para mostrar o no imagen calibrada
        self.checkbox_estado = QCheckBox("Mostrar imagen calibrada", self)
        self.checkbox_estado.setGeometry(10, 370, w-1, 21)
        self.checkbox_estado.stateChanged.connect(self.actualizar_estado)
        
        # Boton para iniciar la captura
        self.pushButton = QtWidgets.QPushButton("Iniciar", self)
        self.pushButton.setGeometry(QtCore.QRect(180, 400, 80, 22))
        self.pushButton.setObjectName("pushButton")
        
        self.pushButton.clicked.connect(self.iniciar_captura)
        
        # self.label = QtWidgets.QLabel("La calibracion se hace con color Rojo", self)
        # self.label.setGeometry(QtCore.QRect(10, 370, w-1, 21))
        # self.label.setObjectName("label")
        
    def seleccion_fuente(self, item):
        item_text = item.text()
        if item_text == videopath:
            self.seleccion_videopath()
        else:
            self.seleccion_cam(item)
        
    def seleccion_cam(self, item):
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
        self.actualizar_color()
        print(f"Color: {seleccion}") 
        
    def validar_ingreso_referencia(self):
        rfs = self.lineEdit.text()
        # Hacer una comprobacion por si se ingresa una coma en lugar de un punto
        # Hacer comprobacion cuando no se ingresa nada. Si se apreta Aplicar, se cierra
        self.ref_seleccionada = abs(float(rfs))
        print(f"Valor ingresado: {rfs} Numerico: {self.ref_seleccionada}")
        
    def iniciar_captura(self):
        # self.col_seleccionado = self.tupla_color(self.color_1, self.color_2)
        print(self.col_seleccionado)
        if self.col_seleccionado != -1 and self.ref_seleccionada != -1:
            if self.cam_seleccionada == videopath:
                self.cam_seleccionada = self.cargar_archivo_video()
                cap = cv2.VideoCapture(self.cam_seleccionada)
                fcd.iniciar_deteccion(self.col_seleccionado, cap, self.ref_seleccionada, self.estado)
            elif self.cam_seleccionada == camara:
                fcd.hard_inicio(self.col_seleccionado, self.ref_seleccionada, self.estado) # Una abominacion, pero anda por ahora
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
    
    def crear_slider(self):
        slider = QSlider(Qt.Horizontal, self)
        slider.valueChanged.connect(self.actualizar_color)
        
        return slider
    
    def actualizar_color(self):
        tolerancia_actual = self.slider_tolerancia.value()
        print(self.tolerancia_anterior, tolerancia_actual)
        if tolerancia_actual > self.tolerancia_anterior:
                self.color_1[0] -= 1  
                self.color_2[0] += 1
        elif tolerancia_actual < self.tolerancia_anterior:
                self.color_1[0] += 1  
                self.color_2[0] -= 1
        else:
                print("err")
                
        self.tolerancia_anterior = tolerancia_actual
        
        # Crear un color a partir de matiz y brillo
        color_bajo_muestra = QColor.fromHsv(self.color_1[0], self.color_1[1], self.color_1[2]) # Color HSV (tono, saturacion, brillo)
        color_alto_muestra = QColor.fromHsv(self.color_2[0], self.color_2[1], self.color_2[2])

        # Crear una imagen con el color seleccionado
        imagen_alto = QPixmap(100, 100)
        imagen_alto.fill(color_alto_muestra)
        imagen_bajo = QPixmap(100, 100)
        imagen_bajo.fill(color_bajo_muestra)

        # Mostrar la imagen en la etiqueta de muestra de color
        self.etiqueta_color_1.setPixmap(imagen_bajo)
        self.etiqueta_color_2.setPixmap(imagen_alto)
        
        print(self.color_1, self.color_2)
    
    def tupla_color(self, c1, c2):
        return (np.array(c1), np.array(c2))
        
    def actualizar_estado(self):
        self.estado = self.checkbox_estado.isChecked()
        print(f"Estado actualizado: {self.estado}")

app = QApplication(sys.argv)
ventana = MiVentana()
ventana.show()
sys.exit(app.exec_())

