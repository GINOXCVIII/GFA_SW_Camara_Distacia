# https://learnopencv.com/how-to-find-frame-rate-or-frames-per-second-fps-in-opencv-python-cpp/

import cv2

captura = cv2.VideoCapture(0)
salida = cv2.VideoWriter('videoSalida.avi',cv2.VideoWriter_fourcc(*'XVID'),captura.get(cv2.CAP_PROP_FPS),(640,480))

while (captura.isOpened()):
	ret, imagen = captura.read()
	print (captura.get(cv2.CAP_PROP_FPS))
	if ret == True:
		cv2.imshow('video', imagen)
		salida.write(imagen)
		if cv2.waitKey(1) & 0xFF == ord('q'):
			break
	else: break

captura.release()
salida.release()
cv2.destroyAllWindows()
