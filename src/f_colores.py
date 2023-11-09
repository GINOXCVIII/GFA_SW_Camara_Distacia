import numpy as np

# Amarillo es el mejor para camara. Los demas son complicados de detectar
# Lista de colores
low_green = np.array([50, 100, 100])
high_green = np.array([70, 255, 255])

low_red = np.array([159, 50, 70])
high_red = np.array([180, 255, 255])

low_blue = np.array([110, 50, 50])
high_blue = np.array([130, 255, 255])

low_yellow = np.array([20, 100, 100])
high_yellow = np.array([35, 255, 255])

low_pink = np.array([140, 50, 50])
high_pink = np.array([170, 255, 255])

low_orange = np.array([10, 100, 100])
high_orange = np.array([20, 255, 255])

low_cyan = np.array([85, 100, 100])
high_cyan = np.array([100, 255, 255])

# Tuplas colores
verde = (low_green, high_green, "Verde")
rojo = (low_red, high_red, "Rojo")
azul = (low_blue, high_blue, "Azul")
amarillo = (low_yellow, high_yellow, "Amarillo")
fucsia = (low_pink, high_pink, "Fucsia")
naranja = (low_orange, high_orange, "Naranja")
cian = (low_cyan, high_cyan, "Cian")

def lista_colores():
	return [rojo, verde, azul, amarillo, fucsia, naranja, cian]
