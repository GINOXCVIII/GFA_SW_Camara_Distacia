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
camara = "Camara"
# ------------------------------------------------------------------------------------------------
class MiVentana(QMainWindow):
    def __init__(self):
        super().__init__()
        w = 385
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
        
        # Picker colores
        
        self.label_3 = QtWidgets.QLabel("Colores", self)
        self.label_3.setGeometry(QtCore.QRect(180, 20, 141, 20))
        self.label_3.setObjectName("label_3")
        
        # Color 1 - Color bajo
        self.label_4 = QtWidgets.QLabel("Color bajo", self)
        self.label_4.setGeometry(QtCore.QRect(180, 50, 141, 20))
        self.label_4.setObjectName("label_4")
        
        self.slider_matiz = self.crear_slider()
        self.slider_matiz.setRange(0, 359)  # Rango de matiz (0-359 grados)
        self.slider_matiz.setGeometry(QtCore.QRect(255, 70, 20, 165))
        self.slider_toleracion = self.crear_slider()
        self.slider_toleracion.setRange(0, 50)
        self.slider_toleracion.setGeometry(QtCore.QRect(300, 70, 20, 165))
        
        self.etiqueta_color_1 = QLabel(self)
        self.etiqueta_color_1.setGeometry(QtCore.QRect(180, 80, 60, 60))
        self.etiqueta_color_2 = QLabel(self)
        self.etiqueta_color_2.setGeometry(QtCore.QRect(180, 180, 60, 60))
        
        self.hsv_color_1 = QLabel(self)
        self.hsv_color_1.setGeometry(180, 260, 260, 20)
        
        # self.hsv_color_2 = QLabel(self)
        # self.hsv_color_2.setGeometry(180, 290, 260, 20)
        
        self.actualizar_color()  # Actualizar la muestra de color inicial
        
        # Color 2 - Color alto
        self.label_5 = QtWidgets.QLabel("Color alto", self)
        self.label_5.setGeometry(QtCore.QRect(180, 150, 141, 20))
        self.label_5.setObjectName("label_5")
        
        self.label_3 = QtWidgets.QLabel("Colores", self)
        self.label_3.setGeometry(QtCore.QRect(180, 20, 141, 20))
        self.label_3.setObjectName("label_3")
        
        # self.listView_2.itemClicked.connect(self.seleccion_col)
        
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
        print("camara")
        self.cam_seleccionada = camara
        
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
            elif self.cam_seleccionada == camara:
                fcd.hard_inicio(self.col_seleccionado, self.ref_seleccionada) # Una abominacion, pero anda por ahora
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
        slider = QSlider(Qt.Vertical, self)
        slider.valueChanged.connect(self.actualizar_color)
        
        return slider
    
    def actualizar_color(self):
        matiz = self.slider_matiz.value()
        tolerancia = self.slider_toleracion.value()
        
        matiz_alto = min(matiz + tolerancia, 359)
        saturacion_alto = 255
        brillo_alto = 255
                
        matiz_bajo = max(matiz - tolerancia, 0)
        saturacion_bajo = 100
        brillo_bajo = 100
        
        # Crear un color a partir de matiz y brillo
        color_alto_muestra = QColor.fromHsv(matiz_alto, saturacion_alto, brillo_alto) # Color HSV (tono, saturacion, brillo)
        color_bajo_muestra = QColor.fromHsv(matiz_bajo, saturacion_bajo, brillo_bajo)

        # Crear una imagen con el color seleccionado
        imagen_alto = QPixmap(100, 100)
        imagen_alto.fill(color_alto_muestra)
        imagen_bajo = QPixmap(100, 100)
        imagen_bajo.fill(color_bajo_muestra)

        # Mostrar la imagen en la etiqueta de muestra de color
        self.etiqueta_color_1.setPixmap(imagen_bajo)
        self.etiqueta_color_2.setPixmap(imagen_alto)
        
        self.hsv_color_1.setText(f"Matiz alto: {matiz_alto} Matiz bajo: {matiz_bajo}")
        
        self.color_1 = [matiz_bajo, saturacion_bajo, brillo_bajo]
        self.color_2 = [matiz_alto, saturacion_alto, brillo_alto]
    
    def tupla_color(self, c1, c2):
        return (np.array(c1), np.array(c2))

app = QApplication(sys.argv)
ventana = MiVentana()
ventana.show()
sys.exit(app.exec_())

