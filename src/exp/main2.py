# -*- coding: utf-8 -*-
"""
Created on Tue Apr 25 17:45:30 2023
Hace el streaming con otro hilo
@author: glattanzio
"""

from PyQt5.QtWidgets import (QApplication, QWidget, QMessageBox, QFileDialog, QHBoxLayout, QLabel)
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys
import cv2 
from time import sleep
import numpy as np
import matplotlib.pyplot as plt
import pyqtgraph as pg
import shutil
import csv
import threading
import time
import os

class GraficoVideo(QtWidgets.QDialog):
    redBajo1 = np.array([0, 100, 20], np.uint8)
    redAlto1 = np.array([8, 255, 255], np.uint8)
    redBajo2=np.array([175, 100, 20], np.uint8)
    redAlto2=np.array([179, 255, 255], np.uint8)
    x = []
    y = []
    t = []
    video_path = 'video.mp4'
    def __init__(self):
        super().__init__()
        uic.loadUi('grafico_video.ui', self)
        self._grafico = pg.GraphicsLayoutWidget(self._grafico,show = False, size=(530,260))
        self._grafico.setBackground([1,1,1,1])
        self.plot = self._grafico.addPlot()
        self.plot.showGrid(x=True, y=True)
        self._boton.clicked.connect(self.graficar)
        self._cargar.clicked.connect(self.getfile)
        
    def getfile(self):
        ret = QFileDialog.getOpenFileName(self, 'Open file','c:\\Users\latta\OneDrive\Escritorio\Pendulo',"All Files (*.*), *.*")
        path = ret[0]
        varaux = path.split('/')
        name = varaux[len(varaux)-1]
        self.video_path = path
        # print(name)
        self._nombre.setText(name)
    
    def graficar(self):
        self.analizar()
        self.plot.clear()
        auxgraf = self._lista.currentIndex()
        if auxgraf == 0:
            vardep = self.x
            varindep = self.t
            self.plot.setTitle('X vs T',color = 'k')
            self.plot.setLabel('left', 'eje x', units='pixeles',color = 'k')
            self.plot.setLabel('bottom', 'tiempo', units='frames',color = 'k')
        elif auxgraf ==1:
            vardep = self.y
            varindep = self.t
            self.plot.setTitle('Y vs T',color = 'k')
            self.plot.setLabel('left', 'eje y', units='pixeles',color = 'k')
            self.plot.setLabel('bottom', 'tiempo', units='frames',color = 'k')
        else:
            vardep = self.y
            varindep = self.x
            self.plot.setTitle('Y vs X',color = 'k')
            self.plot.setLabel('left', 'eje y', units='pixeles',color = 'k')
            self.plot.setLabel('bottom', 'eje x', units='pixeles',color = 'k')
        self.plot.plot(varindep,vardep, pen = pg.mkPen('k', width=1))
        
    def analizar(self):
        self.x = []
        self.y = []
        self.t = []
        cap = cv2.VideoCapture(self.video_path) 
        frame_number = 0
        while (cap.isOpened()):
            isTrue, frame = cap.read()
            if isTrue==True:
                #frame = cv2.flip(frame,1)
                frame_number = frame_number + 1
                hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                #mascara
                maskRed1 = cv2.inRange(hsv, self.redBajo1, self.redAlto1)
                maskRed2 = cv2.inRange(hsv, self.redBajo2, self.redAlto2)
                mask = cv2.add(maskRed1, maskRed2)
                #mejoran la deteccion del objeto
                mask = cv2.erode(mask, None, iterations = 1)
                mask = cv2.dilate(mask, None, iterations = 2)
                mask = cv2.medianBlur(mask, 13)    
                #busco contornos
                contornos, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
                for c in contornos:
                    area = cv2.contourArea(c) # filtro contornos grandes
                    if area > 3000:
                        #tengo la posicion (x,y), podemos tener un punto de referencia de otro color que sea el 0,0
                        M = cv2.moments(c)
                        if (M["m00"]==0): M["m00"]=1
                        xx = int(M["m10"]/M["m00"])
                        yy = int(M['m01']/M['m00'])
                        self.x.append(xx)
                        self.y.append(500-yy)
                        self.t.append(frame_number)        
            else:
                break
                       
        cap.release()
            
            
class GraficoArchivo(QtWidgets.QDialog):
    path =''
    def __init__(self):
        super().__init__()
        uic.loadUi('grafico_archivo.ui', self)
        self._grafico = pg.GraphicsLayoutWidget(self._grafico,show = False, size=(530,260))
        self._grafico.setBackground([1,1,1,1])
        self.plot = self._grafico.addPlot()
        self.plot.showGrid(x=True, y=True)
        self._cargar.clicked.connect(self.getfile)
        self._graficar.clicked.connect(self.graficar)
        
        
    def getfile(self):
        ret = QFileDialog.getOpenFileName(self, 'Open file','',"All Files (*.*), *.*")
        self.path = ret[0]
        varaux = self.path.split('/')
        name = varaux[len(varaux)-1]
        # print(name)
        self._nombre.setText(name)
        
    def graficar(self):
        x=[]
        y=[]
        t=[]
        with open(self.path, 'r', ) as file:
            reader = csv.reader(file)
            for row in reader:
                if (row[0] != 'x'):
                    x.append(int(row[0]))
                    y.append(int(row[1]))
                    t.append(int(row[2]))
        self.plot.clear()
        auxgraf = self._lista.currentIndex()
        if auxgraf == 0:
            vardep = x
            varindep = t
            self.plot.setTitle('X vs T',color = 'k')
            self.plot.setLabel('left', 'eje x', units='pixeles',color = 'k')
            self.plot.setLabel('bottom', 'tiempo', units='frames',color = 'k')
        elif auxgraf ==1:
            vardep = y
            varindep = t
            self.plot.setTitle('Y vs T',color = 'k')
            self.plot.setLabel('left', 'eje y', units='pixeles',color = 'k')
            self.plot.setLabel('bottom', 'tiempo', units='frames',color = 'k')
        else:
            vardep = y
            varindep = x
            self.plot.setTitle('Y vs X',color = 'k')
            self.plot.setLabel('left', 'eje y', units='pixeles',color = 'k')
            self.plot.setLabel('bottom', 'eje x', units='pixeles',color = 'k')
        self.plot.plot(varindep,vardep, pen = pg.mkPen('k', width=1))
        
class MainWindow(QtWidgets.QMainWindow):
    redBajo1 = np.array([0, 100, 20], np.uint8)
    redAlto1 = np.array([8, 255, 255], np.uint8)
    redBajo2=np.array([175, 100, 20], np.uint8)
    redAlto2=np.array([179, 255, 255], np.uint8)
    height = 360
    width = 440
    dimensions = (width, height)
    x=[]
    y=[]
    t=[]
    
    def init(self):
        app = QtWidgets.QApplication([])
        window = MainWindow()
        window.show()
        app.exec_()

    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.grabando = False
        super(MainWindow, self).__init__()
        uic.loadUi('interfaz1.0.ui', self)
        self._boton.clicked.connect(self.Grabacion)
        self.actionVideo.triggered.connect(self.grafico_video)
        self.actionArchivo.triggered.connect(self.grafico_archivo)
        self.actionArchivo_2.triggered.connect(self.guardo_archivo)
        self.stream = threading.Thread(target = self.show_frame, args=())
        self.stream.start()
    
    def grafico_video(self):
        v = GraficoVideo()
        v.exec_()
       
    def grafico_archivo(self):
        a = GraficoArchivo()
        a.exec_()
    
    def guardo_archivo(self):
        ret = QFileDialog.getSaveFileName(self, "Guardar Archivo", "archivo.csv", "(*.csv)")
        self.analizar()
        with open(ret[0], 'w', newline= '') as file:
            writer = csv.writer(file)
            writer.writerow(["x", "y", "t"])
            for i in range(len(self.t)):
                writer.writerow([self.x[i], self.y[i], self.t[i]])
    def grabar(self, salida):
        while (self.grabando):
            ok, frame = self.cap.read()
            if ok:
                frame = cv2.resize(frame,self.dimensions, interpolation = cv2.INTER_AREA)
                salida.write(frame)
        
    def show_frame(self):
        while(True):
            ok, frame = self.cap.read()
            if ok:
                frame = cv2.resize(frame,self.dimensions, interpolation = cv2.INTER_AREA)
                if  not self.grabando:
                    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                    #mascara
                    maskRed1 = cv2.inRange(hsv, self.redBajo1, self.redAlto1)
                    maskRed2 = cv2.inRange(hsv, self.redBajo2, self.redAlto2)
                    mask = cv2.add(maskRed1, maskRed2)
                    #mejoran la deteccion del objeto
                    mask = cv2.erode(mask, None, iterations = 1)
                    mask = cv2.dilate(mask, None, iterations = 2)
                    mask = cv2.medianBlur(mask, 13)    
                    #busco contornos
                    contornos, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
                    for c in contornos:
                        area = cv2.contourArea(c) # filtro contornos grandes
                        if area > 3000:
                            #tengo la posicion (x,y), podemos tener un punto de referencia de otro color que sea el 0,0
                            M = cv2.moments(c)
                            if (M["m00"]==0): M["m00"]=1
                            xx = int(M["m10"]/M["m00"])
                            yy = int(M['m01']/M['m00'])
                            frame = cv2.circle(frame,(xx,yy), 5, (0,0,255) , 6)
                    image = QImage(frame, frame.shape[1], frame.shape[0], frame.shape[1] * 3, QImage.Format_RGB888).rgbSwapped()
                    self._pantalla.setPixmap(QPixmap(image))  
                    mask_aux = cv2.cvtColor(mask, cv2.COLOR_GRAY2RGB)
                    image_mask = QImage(mask_aux, mask_aux.shape[1], mask_aux.shape[0], mask_aux.shape[1] * 3, QImage.Format_RGB888).rgbSwapped()
                    self._pantalla2.setPixmap(QPixmap(image_mask))
    
    def analizar(self):
        self.x = []
        self.y = []
        self.t = []
        cap = cv2.VideoCapture('video.mp4') 
        frame_number = 0
        while (cap.isOpened()):
            isTrue, frame = cap.read()
            if isTrue==True:
                #frame = cv2.flip(frame,1)
                frame_number = frame_number + 1
                hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                #mascara
                maskRed1 = cv2.inRange(hsv, self.redBajo1, self.redAlto1)
                maskRed2 = cv2.inRange(hsv, self.redBajo2, self.redAlto2)
                mask = cv2.add(maskRed1, maskRed2)
                #mejoran la deteccion del objeto
                mask = cv2.erode(mask, None, iterations = 1)
                mask = cv2.dilate(mask, None, iterations = 2)
                mask = cv2.medianBlur(mask, 13)    
                #busco contornos
                contornos, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
                for c in contornos:
                    area = cv2.contourArea(c) # filtro contornos grandes
                    if area > 3000:
                        #tengo la posicion (x,y), podemos tener un punto de referencia de otro color que sea el 0,0
                        M = cv2.moments(c)
                        if (M["m00"]==0): M["m00"]=1
                        xx = int(M["m10"]/M["m00"])
                        yy = int(M['m01']/M['m00'])
                        self.x.append(xx)
                        
                        self.y.append(500-yy)
                        self.t.append(frame_number)        
            else:
                break
                       
        cap.release()
        
    def mostrarFoto(self, foto, pantalla):
        cv_img = cv2.imread(foto)
        cv_img = cv2.resize(cv_img, self.dimensions, interpolation = cv2.INTER_AREA)
        image = QImage(cv_img, cv_img.shape[1],cv_img.shape[0], cv_img.shape[1] * 3,QImage.Format_RGB888).rgbSwapped()
        pantalla.setPixmap(QPixmap(image))
        
    def closeEvent(self, event):
        close = QMessageBox()
        close.setIcon(QMessageBox.Question)
        close.setWindowTitle("Close Window")
        close.setText("Are you sure you want to close the window?")
        close.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
        close = close.exec()
        if close == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()
            
    def Grabacion(self):
        if(self._boton.text() == "Adquirir"):
            print("adquiero")
            self._boton.setText("Frenar")
            self.salida = cv2.VideoWriter("video.mp4",cv2.VideoWriter_fourcc(*"mp4v"), 20.0, (self.width,self.height))
            self.grabando = True
            self.grabador = threading.Thread(target =self.grabar, args=(self.salida,))
            self.grabador.start()
            print(self.grabando)
        else:
            self._boton.setText("Adquirir")
            print("pauso")
            self.salida.release()
            self.grabando = False
            print(self.grabando)
            self.guardarVideo()
            
    def guardarVideo(self):
        ret = QFileDialog.getSaveFileName(self, "Guardar Video", "video.mp4", "Video Files (*.mp4)")
        print(ret[0])
        print(os.path.dirname(os.path.realpath(__file__))+"/video.mp4")
        if os.path.exists(ret[0]):
            os.remove(ret[0])
        shutil.copyfile('video.mp4',ret[0])

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

