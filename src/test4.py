#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 12 16:11:28 2023

@author: imano-oh
"""
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QSlider, QLabel
from PyQt5.QtGui import QColor, QPixmap, QPainter
from PyQt5.QtCore import Qt

class MiVentana(QMainWindow):
    def __init__(self):
        super().__init__()
        
        x = 0
        
        self.setWindowTitle("Selector de Color (Matiz y Brillo)")
        self.setGeometry(100, 100, 400, 300)

        # Crear una barra deslizante para seleccionar el matiz (tono)
        self.slider_matiz = self.crear_slider()
        self.slider_matiz.setRange(0, 359)  # Rango de matiz (0-359 grados)

        # Crear una barra deslizante para seleccionar el brillo
        self.slider_brillo = self.crear_slider()
        self.slider_brillo.setRange(0, 255)  # Rango de brillo (0-100%)

        # Crear una etiqueta para mostrar la muestra del color
        self.etiqueta_color = QLabel(self)
        self.etiqueta_color.setFixedSize(100, 100)  # Tamaño de la muestra de color
        x = self.actualizar_color()  # Actualizar la muestra de color inicial

        # Colores iniciales
        self.matiz = 0
        self.brillo = 100

        # Crear un widget central para organizar los elementos
        central_widget = QWidget(self)
        layout = QVBoxLayout(central_widget)
        layout.addWidget(self.slider_matiz)
        layout.addWidget(self.slider_brillo)
        layout.addWidget(self.etiqueta_color)

        self.setCentralWidget(central_widget)

    def crear_slider(self):
        slider = QSlider(Qt.Horizontal, self)
        slider.valueChanged.connect(self.actualizar_color)
        return slider

    def actualizar_color(self):
        self.matiz = self.slider_matiz.value()
        self.brillo = self.slider_brillo.value()

        # Crear un color a partir de matiz y brillo
        color = QColor.fromHsv(self.matiz, 255, self.brillo) # Color HSV (tono, saturacion, brillo)
        print(self.matiz, 255, self.brillo)

        # Crear una imagen con el color seleccionado
        imagen = QPixmap(100, 100)
        imagen.fill(color)

        # Mostrar la imagen en la etiqueta de muestra de color
        self.etiqueta_color.setPixmap(imagen)
        
        return [self.matiz, 255, self.brillo]

# Crear una aplicación de PyQt5
app = QApplication(sys.argv)

# Crear una instancia de la ventana principal
ventana_principal = MiVentana()

# Mostrar la ventana principal
ventana_principal.show()

# Ejecutar el bucle de eventos de la aplicación
sys.exit(app.exec_())
