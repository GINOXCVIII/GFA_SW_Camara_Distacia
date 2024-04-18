import cv2
import numpy as np

# Rangos de color para el fucsia (en formato HSV)
lower_pink = np.array([140, 50, 50])
upper_pink = np.array([170, 255, 255])

# Inicializar la cámara
cap = cv2.VideoCapture(0)

while True:
    # Capturar el fotograma de la cámara
    ret, frame = cap.read()
    
    brightness = 8
    contrast = 1.3
    frame = cv2.addWeighted(frame, contrast, np.zeros(frame.shape, frame.dtype), 0, brightness) 

    # Mostrar la imagen resultante
    cv2.imshow("frame", frame)

    # Romper el bucle si se presiona la tecla 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Liberar los recursos y cerrar las ventanas
cap.release()
cv2.destroyAllWindows()
