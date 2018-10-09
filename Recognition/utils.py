import cv2
import mahotas


def recognition_borders(image):
    image = cv2.resize(image, (50, 50))
    t = mahotas.thresholding.otsu(image)
    for k in range(1, 50, 1):
        for z in range(1, 50, 1):
            color = image[k, z]
            if color > t:
                image[k, z] = 0
            else:
                image[k, z] = 255
    thresh = image.copy()
    return thresh


def update_values(results, meter):
    return (results[0][0]) * (10 ** meter)
