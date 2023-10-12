#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep  7 16:55:48 2023

@author: imano-oh
"""

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QSlider, QListWidget, QListWidgetItem, QLineEdit, QFileDialog
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
colores = ["Rojo", "Verde", "Azul"]

if len(indices_camaras) == len(nombres_camaras):
    for i in range(len(indices_camaras)):
        camara = str(indices_camaras[i]) + ": " + nombres_camaras[i]
        camaras.append(camara)
        
videopath = "Archivo de video"
# ------------------------------------------------------------------------------------------------
class MiVentana(QMainWindow):
    def __init__(self):
        super().__init__()
        w = 432
        h = 450
        cam_seleccionada = -1
        col_seleccionado = -1
        ref_seleccionada = -1
        # Colores HSV [matiz, saturacion, brillo] Saturacion fija ¿se puede cambiar?
        color_1 = [0, 255, 0]
        color_2 = [0, 255, 0]
        
        self.setWindowTitle("GFA")  # Establecer el título de la ventana
        self.setGeometry(100, 100, w, h)  # Establecer la posición y el tamaño de la ventana
        self.setFixedSize(w, h)
        
        # Lista de camaras
        self.listView = QListWidget(self)
        self.listView.setGeometry(QtCore.QRect(10, 60, 151, 251))
        self.listView.setObjectName("listView")
        for c in camaras:
            item = QListWidgetItem(c)
            self.listView.addItem(item)
        self.listView.addItem(videopath)
            
        self.label_2 = QtWidgets.QLabel("Fuentes", self)
        self.label_2.setGeometry(QtCore.QRect(10, 20, 141, 20))
        self.label_2.setObjectName("label_2")
        
        self.listView.itemClicked.connect(self.seleccion_fuente)
        
        """
        # Lista de colores
        self.listView_2 = QListWidget(self)
        self.listView_2.setGeometry(QtCore.QRect(180, 40, 151, 251))
        self.listView_2.setObjectName("listView_2")
        for c in colores:
            item = QListWidgetItem(c)
            self.listView_2.addItem(item)
        """  
        
        # Picker colores
        
        self.label_3 = QtWidgets.QLabel("Colores", self)
        self.label_3.setGeometry(QtCore.QRect(180, 20, 141, 20))
        self.label_3.setObjectName("label_3")
        
        # Color 1 - Color alto
        self.label_4 = QtWidgets.QLabel("Color alto", self)
        self.label_4.setGeometry(QtCore.QRect(180, 50, 141, 20))
        self.label_4.setObjectName("label_4")
        
        self.slider_matiz_1 = self.crear_slider_1()
        self.slider_matiz_1.setRange(0, 359)  # Rango de matiz (0-359 grados)
        self.slider_matiz_1.setGeometry(QtCore.QRect(245, 70, 165, 20))
        self.slider_saturacion_1 = self.crear_slider_1()
        self.slider_saturacion_1.setRange(0, 255)
        self.slider_saturacion_1.setGeometry(QtCore.QRect(245, 100, 165, 20))
        self.slider_brillo_1 = self.crear_slider_1()
        self.slider_brillo_1.setRange(0, 255)
        self.slider_brillo_1.setGeometry(QtCore.QRect(245, 130, 165, 20))
        
        self.etiqueta_color_1 = QLabel(self)
        self.etiqueta_color_1.setGeometry(QtCore.QRect(180, 80, 60, 60))
        
        self.hsv_color_1 = QLabel(self)
        self.hsv_color_1.setGeometry(180, 150, 220, 20)
        
        self.actualizar_color_1()  # Actualizar la muestra de color inicial
        
        # Color 2 - Color bajo
        self.label_5 = QtWidgets.QLabel("Color bajo", self)
        self.label_5.setGeometry(QtCore.QRect(180, 190, 141, 20))
        self.label_5.setObjectName("label_5")
        
        self.slider_matiz_2 = self.crear_slider_2()
        self.slider_matiz_2.setRange(0, 359)  # Rango de matiz (0-359 grados)
        self.slider_matiz_2.setGeometry(QtCore.QRect(245, 210, 165, 20))
        self.slider_saturacion_2 = self.crear_slider_2()
        self.slider_saturacion_2.setRange(0, 255)
        self.slider_saturacion_2.setGeometry(QtCore.QRect(245, 240, 165, 20))
        self.slider_brillo_2 = self.crear_slider_2()
        self.slider_brillo_2.setRange(0, 255)
        self.slider_brillo_2.setGeometry(QtCore.QRect(245, 270, 165, 20))
        
        self.etiqueta_color_2 = QLabel(self)
        self.etiqueta_color_2.setGeometry(QtCore.QRect(180, 220, 60, 60))
        
        self.hsv_color_2 = QLabel(self)
        self.hsv_color_2.setGeometry(180, 290, 220, 20)
        
        self.actualizar_color_2()  # Actualizar la muestra de color inicial
        
        self.label_3 = QtWidgets.QLabel("Colores", self)
        self.label_3.setGeometry(QtCore.QRect(180, 20, 141, 20))
        self.label_3.setObjectName("label_3")
        
        # self.listView_2.itemClicked.connect(self.seleccion_col)
        
        # Cuadro de entrada de la referencia
        self.lineEdit = QLineEdit(self)
        self.lineEdit.setValidator(QtGui.QDoubleValidator()) # Solo se pueden ingresar numeros
        self.lineEdit.setGeometry(QtCore.QRect(110, 330, 113, 22))
        self.lineEdit.setObjectName("lineEdit")
        
        self.label = QtWidgets.QLabel("Referencia (cm)", self)
        self.label.setGeometry(QtCore.QRect(10, 330, 101, 21))
        self.label.setObjectName("label")
        
        self.pushButton_2 = QtWidgets.QPushButton("Aplicar", self)
        self.pushButton_2.setGeometry(QtCore.QRect(233, 330, 80, 22))
        self.pushButton_2.setObjectName("pushButton_2")
        
        self.pushButton_2.clicked.connect(self.validar_ingreso_referencia)
        
        # Boton para iniciar la captura
        self.pushButton = QtWidgets.QPushButton("Iniciar", self)
        self.pushButton.setGeometry(QtCore.QRect(180, 400, 80, 22))
        self.pushButton.setObjectName("pushButton")
        
        self.pushButton.clicked.connect(self.iniciar_captura)
        
        self.label = QtWidgets.QLabel("La calibracion se hace con color Rojo", self)
        self.label.setGeometry(QtCore.QRect(10, 370, w-1, 21))
        self.label.setObjectName("label")
        
    def seleccion_fuente(self, item):
        item_text = item.text()
        if item_text == videopath:
            self.seleccion_videopath()
        else:
            self.seleccion_cam(item)
        
    def seleccion_cam(self, item):
        seleccion = item.text()
        print(f"Camara: {seleccion}")
        self.cam_seleccionada = int(seleccion[0]) # El primer caracter de la cadena es el indice de la camara
        # Puede pasar que haya 10 o mas camaras? Puede fallar
        print(self.cam_seleccionada)
        # print(item) No puedo usar item como parametro para iniciar la camara
        
    def seleccion_videopath(self):
        print("videopath")
        self.cam_seleccionada = videopath
    
    # Ya no se usa
    def seleccion_col(self, item):
        seleccion = item.text()
        print(f"Color: {seleccion}")
        self.col_seleccionado = seleccion[0].lower() # Tomo el primer caracter en minusculas
        print(self.col_seleccionado)
        
    def validar_ingreso_referencia(self):
        rfs = self.lineEdit.text()
        # Hacer una comprobacion por si se ingresa una coma en lugar de un punto
        self.ref_seleccionada = abs(float(rfs))
        print(f"Valor ingresado: {rfs} Numerico: {self.ref_seleccionada}")
        
    def iniciar_captura(self):
        self.col_seleccionado = self.tupla_color(self.color_1, self.color_2)
        print(self.col_seleccionado)
        
        if self.col_seleccionado != -1 and self.ref_seleccionada != -1:
            if self.cam_seleccionada == videopath:
                self.cam_seleccionada = self.cargar_archivo_video()
                cap = cv2.VideoCapture(self.cam_seleccionada)
                fcd.iniciar_deteccion(self.col_seleccionado, cap, 0, self.ref_seleccionada)
            
            elif self.cam_seleccionada != -1:
                cap = cv2.VideoCapture(self.cam_seleccionada)
                fcd.iniciar_deteccion(self.col_seleccionado, cap, 0, self.ref_seleccionada)
        else:
            print("ganso, rellena todo")
            # Tengo que hacer algun feedback para indicar que faltan cosas

    def cargar_archivo_video(self):
        opciones = QFileDialog.Options()
        opciones |= QFileDialog.ReadOnly  # Opcional: abrir el archivo en modo solo lectura

        archivo, _ = QFileDialog.getOpenFileName(self, "Seleccionar Archivo", "", "Todos los Archivos (*)", options=opciones)

        return archivo
    
    def crear_slider_1(self):
        slider = QSlider(Qt.Horizontal, self)
        slider.valueChanged.connect(self.actualizar_color_1)
        
        return slider
    
    def actualizar_color_1(self):
        matiz = self.slider_matiz_1.value()
        saturacion = self.slider_saturacion_1.value()
        brillo = self.slider_brillo_1.value()
        
        # Crear un color a partir de matiz y brillo
        color_muestra = QColor.fromHsv(matiz, saturacion, brillo) # Color HSV (tono, saturacion, brillo)
        # print(self.matiz, 255, self.brillo)

        # Crear una imagen con el color seleccionado
        imagen = QPixmap(100, 100)
        imagen.fill(color_muestra)

        # Mostrar la imagen en la etiqueta de muestra de color
        self.etiqueta_color_1.setPixmap(imagen)
        
        self.hsv_color_1.setText(f"Matiz: {matiz} Saturacion: {saturacion} Brillo: {brillo}")
        self.color_1 = [matiz, saturacion, brillo]
    
    def crear_slider_2(self):
        slider = QSlider(Qt.Horizontal, self)
        slider.valueChanged.connect(self.actualizar_color_2)
        
        return slider
    
    def actualizar_color_2(self):
        matiz = self.slider_matiz_2.value()
        saturacion = self.slider_saturacion_2.value()
        brillo = self.slider_brillo_2.value()
        
        # Crear un color a partir de matiz y brillo
        color_muestra = QColor.fromHsv(matiz, 255, brillo) # Color HSV (tono, saturacion, brillo)
        # print(self.matiz, 255, self.brillo)

        # Crear una imagen con el color seleccionado
        imagen = QPixmap(100, 100)
        imagen.fill(color_muestra)

        # Mostrar la imagen en la etiqueta de muestra de color
        self.etiqueta_color_2.setPixmap(imagen)
        
        self.hsv_color_2.setText(f"Matiz: {matiz} Saturacion: {saturacion} Brillo: {brillo}")
        self.color_2 = [matiz, 255, brillo]
    
    def tupla_color(self, c1, c2):
        return (np.array(c1), np.array(c2))

app = QApplication(sys.argv)
ventana = MiVentana()
ventana.show()
sys.exit(app.exec_())

