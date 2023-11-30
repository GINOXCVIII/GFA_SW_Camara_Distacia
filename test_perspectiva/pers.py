import cv2
import matplotlib.pyplot as plt
import numpy as np
import numpy.linalg as npla

low_red = np.array([159, 50, 70])
high_red = np.array([180, 255, 255])

rojo = (low_red, high_red, "Rojo")

def detectar_rojo(frame, color):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, color[0], color[1])
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    contours_sorted = sorted(contours, key=cv2.contourArea, reverse=True)[:4]
    
    for i in contours_sorted:
        area = cv2.contourArea(i)
        nuevoContorno = cv2.convexHull(i)
        cv2.drawContours(frame, [nuevoContorno], -1, (200,5,255), 2)
    
    return contours_sorted

def interseccion(p1, p2, p3, p4):
    # Definir las ecuaciones de las rectas en la forma ax + by = c
    a1, b1, c1 = p2[1] - p1[1], p1[0] - p2[0], p1[0] * (p2[1] - p1[1]) - p1[1] * (p2[0] - p1[0])
    a2, b2, c2 = p4[1] - p3[1], p3[0] - p4[0], p3[0] * (p4[1] - p3[1]) - p3[1] * (p4[0] - p3[0])

    # Construir el sistema de ecuaciones lineales
    sistema_ecuaciones = np.array([[a1, b1], [a2, b2]])
    terminos_independientes = np.array([c1, c2])

    # Resolver el sistema de ecuaciones
    try:
        interseccion = np.linalg.solve(sistema_ecuaciones, terminos_independientes)
        return tuple(interseccion)
    except np.linalg.LinAlgError:
        # Las rectas son paralelas y no tienen intersección
        return None

def centros(frame, cont):
    M = []
    if len(cont) >= 1:
        for c in cont:
            # Calcular centro de cada contorno
            Mc = cv2.moments(c)
            if Mc['m00'] == 0:
                cx = 0
                cy = 0
            else:
                cx = int(Mc['m10'] / Mc['m00'])
                cy = int(Mc['m01'] / Mc['m00'])
            M.append((cx, cy))
        # print("M =", M)
    else:
        # print("M =", [(0, 0), (0, 0), (0,0), (0,0)])
        M = [(0, 0), (0, 0), (0,0), (0,0)]
    
    N = np.float32([M[1],
                    M[3],
                    M[2],
                    M[0]])
    
    return N

def unwarp(img, src, dst, testing):

    h, w = img.shape[:2]
    # use cv2.getPerspectiveTransform() to get M, the transform matrix, and Minv, the inverse
    M = cv2.getPerspectiveTransform(src, dst)
    
    print("Matriz de transformacion A:\n", M, "\n")
    
    M_1 = npla.inv(M)
    print("Matriz inversa:\n", M_1, "\n")
    
    b = np.array([1, 0, 0])
    print("Vector unitario prueba x':\n", b, "\n")
    
    b_1 = M_1.dot(b)
    print("x=inv(M).x' :\n", b_1, "\n")
    
    s = M.dot(b_1)
    print(f"Vector M.x=x' que debería ser mas o menos x'{b}:\n", s)#, s[:2], "\n")
    # print("Submatriz de la inversa que es la que me importa (por coord x y):\n", M_1[:2, :2], "\n")

    # use cv2.warpPerspective() to warp your image to a top-down view
    warped = cv2.warpPerspective(img, M, (w, h), flags=cv2.INTER_LINEAR)
    
    x_11 = np.array([M[0][0], M[1][0]])
    x_12 = np.array([M[0][1], M[1][1]])
    
    print("\n", "x_11:", x_11, "x_12:", x_12)
    
    inter = interseccion(src[1], src[2], src[3], src[0])
    
    inter_t = (M[:2, :2].dot(inter)[0] + 1280, M[:2, :2].dot(inter)[1] + 720) # NO SIRVE
    print("interseccion:", (int(inter[0]), int(inter[1])), (int(inter_t[0]), int(inter_t[1])))
    
    warped = cv2.resize(warped, (720, 720), interpolation = cv2.INTER_LINEAR)

    if testing:
        f, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 10))
        ax1.imshow(img)
        x = [src[0][0], src[2][0], src[3][0], src[1][0], src[0][0]]
        y = [src[0][1], src[2][1], src[3][1], src[1][1], src[0][1]]
        
        ax1.plot(x, y, color='cyan', alpha=0.75, linewidth=2, solid_capstyle='round')
        ax1.plot([inter[0]], [inter[1]], 'r+')
        ax1.set_ylim([h, 0])
        ax1.set_xlim([0, w])
        ax2.imshow(cv2.flip(warped, 1))
        ax2.plot([int(720/2)], [int(720/2)], 'r+')
        plt.show()
    else:
        return warped, M
        
img = cv2.imread("pruba.png", cv2.IMREAD_COLOR)

w, h = img.shape[0], img.shape[1]              

puntos = detectar_rojo(img, rojo)
src = centros(img, puntos)

dst = np.float32([(h, 0),
                  (0, 0),
                  (h, w),
                  (0, w)])                  

print("src:", src, "\n")
print("dst:", dst, "\n")

img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) 
unwarp(img_rgb, src, dst, True)
