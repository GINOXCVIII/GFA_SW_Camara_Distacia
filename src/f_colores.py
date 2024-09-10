import numpy as np

# Amarillo es el mejor para camara. Los demas son complicados de detectar
# Lista de colores

# low_green = np.array([34, 16, 0])
# high_green = np.array([81, 255, 250])
low_green = np.array([34, 16, 0])
high_green = np.array([100, 250, 250])

low_red = np.array([150, 45, 65])
high_red = np.array([185, 255, 255])

low_blue = np.array([85, 21, 0])
high_blue = np.array([130, 255, 255])

low_yellow = np.array([20, 100, 100])
high_yellow = np.array([35, 255, 255])

low_pink = np.array([140, 50, 50])
high_pink = np.array([170, 255, 255])

low_orange = np.array([7, 100, 100])
high_orange = np.array([24, 255, 255])

low_cyan = np.array([85, 100, 100])
high_cyan = np.array([100, 255, 255])

low_black = np.array([100, 65, 10])
high_black = np.array([160, 100, 100])

# Tuplas colores
verde = (low_green, high_green, "Verde")
rojo = (low_red, high_red, "Rojo")
azul = (low_blue, high_blue, "Azul")
amarillo = (low_yellow, high_yellow, "Amarillo")
fucsia = (low_pink, high_pink, "Fucsia")
naranja = (low_orange, high_orange, "Naranja")
cian = (low_cyan, high_cyan, "Cian")
negro = (low_black, high_black, "Negro")

def lista_colores():
	return [negro, rojo, verde, azul, amarillo, fucsia, naranja] # , cian]
