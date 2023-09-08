#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep  7 16:55:48 2023

@author: imano-oh
"""

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox, QFileDialog, QMainWindow, QMenu, QAction, QLabel, QVBoxLayout, QListWidget, QListWidgetItem, QLineEdit
from PyQt5 import QtWidgets, QtGui, QtCore, uic
from PyQt5.QtMultimedia import QCameraInfo
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
# ------------------------------------------------------------------------------------------------
class MiVentana(QMainWindow):
    def __init__(self):
        super().__init__()
        w = 343
        h = 450
        cam_seleccionada = -1
        col_seleccionado = -1
        ref_seleccionada = -1
        self.setWindowTitle("GFA")  # Establecer el título de la ventana
        self.setGeometry(100, 100, w, h)  # Establecer la posición y el tamaño de la ventana
        self.setFixedSize(w, h)
        
        # Lista de camaras
        self.listView = QListWidget(self)
        self.listView.setGeometry(QtCore.QRect(10, 40, 151, 251))
        self.listView.setObjectName("listView")
        for c in camaras:
            item = QListWidgetItem(c)
            self.listView.addItem(item)
            
        self.label_2 = QtWidgets.QLabel("Camaras", self)
        self.label_2.setGeometry(QtCore.QRect(10, 20, 141, 20))
        self.label_2.setObjectName("label_2")
        
        self.listView.itemClicked.connect(self.seleccion_cam)
        
        # Lista de colores
        self.listView_2 = QListWidget(self)
        self.listView_2.setGeometry(QtCore.QRect(180, 40, 151, 251))
        self.listView_2.setObjectName("listView_2")
        for c in colores:
            item = QListWidgetItem(c)
            self.listView_2.addItem(item)
            
        self.label_3 = QtWidgets.QLabel("Colores", self)
        self.label_3.setGeometry(QtCore.QRect(180, 20, 141, 20))
        self.label_3.setObjectName("label_3")
        
        self.listView_2.itemClicked.connect(self.seleccion_col)
        
        # Cuadro de entrada de la referencia
        self.lineEdit = QLineEdit(self)
        self.lineEdit.setValidator(QtGui.QDoubleValidator()) # Solo se pueden ingresar numeros
        self.lineEdit.setGeometry(QtCore.QRect(110, 310, 113, 22))
        self.lineEdit.setObjectName("lineEdit")
        
        self.pushButton_2 = QtWidgets.QPushButton("Aplciar", self)
        self.pushButton_2.setGeometry(QtCore.QRect(233, 310, 80, 22))
        self.pushButton_2.setObjectName("pushButton_2")
        
        self.pushButton_2.clicked.connect(self.validar_ingreso_referencia)
        
        # Boton para iniciar la captura
        self.pushButton = QtWidgets.QPushButton("Iniciar", self)
        self.pushButton.setGeometry(QtCore.QRect(130, 370, 80, 22))
        self.pushButton.setObjectName("pushButton")
        
        self.pushButton.clicked.connect(self.iniciar_captura)
        
        self.label = QtWidgets.QLabel("Referencia (cm)", self)
        self.label.setGeometry(QtCore.QRect(10, 310, 101, 21))
        self.label.setObjectName("label")
        
        self.label = QtWidgets.QLabel("La calibracion se hace con color Rojo", self)
        self.label.setGeometry(QtCore.QRect(10, 340, w-1, 21))
        self.label.setObjectName("label")
        
    def seleccion_cam(self, item):
        seleccion = item.text()
        print(f"Camara: {seleccion}")
        self.cam_seleccionada = int(seleccion[0]) # El primer caracter de la cadena es el indice de la camara
        print(self.cam_seleccionada)
        # print(item) No puedo usar item como parametro para iniciar la camara
        
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
        if self.cam_seleccionada != -1 and self.col_seleccionado != -1 and self.ref_seleccionada != -1:
            cap = cv2.VideoCapture(self.cam_seleccionada)
            fcd.iniciar_deteccion(self.col_seleccionado, cap, 0, self.ref_seleccionada)
        else:
            print("ganso, rellena todo")
            # Tengo que hacer algun feedback para indicar que faltan cosas
        
app = QApplication(sys.argv)
ventana = MiVentana()
ventana.show()
sys.exit(app.exec_())

