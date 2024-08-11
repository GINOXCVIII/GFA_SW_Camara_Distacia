#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 1 18:18:48 2024

@author: imano-oh
"""

from PyQt5 import QtWidgets
from ui_hi import Ui_MainWindow
import sys

import f_busqueda_camaras as fbc
import f_colores as col

# ------------------------------------------------------------------------------------------------
camaras = fbc.camaras_indices()
colores = col.lista_colores()

colores_nombres = []
for c in colores:
        colores_nombres.append(c[2]) # c = (color_bajo, color_alto, nombre_color_str)

camara = "Camara"

class MainWindow(QtWidgets.QMainWindow):
    
    def init(self):
        app = QtWidgets.QApplication([])
        window = MainWindow()
        window.show()
        app.exec_()

    def __init__(self):
        super(MainWindow, self).__init__()
        # uic.loadUi('ui_hi.ui', self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self, camaras, colores)
        
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
