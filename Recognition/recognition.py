from . import utils
import cv2
import numpy as np
import mahotas
import os


def detect(image_name):
    samples = np.loadtxt(os.getcwd(), np.float32)
    responses = np.loadtxt(os.getcwd(), np.float32)
    responses = responses.reshape((responses.size, 1))
    model = cv2.ml.KNearest_create()
    model.train(samples, cv2.ml.ROW_SAMPLE, responses)

    rois = 100
    xf = 1
    xfx = xf

    image = cv2.imread(image_name)
    image = cv2.resize(image, (800, 500))
    gris = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    mascar = np.zeros(image.shape[:2], dtype="uint8")
    cv2.rectangle(mascar, (xf, rois), (xf + 800, rois + 90), 255, -1)

    for j in range(1, 800, 1):
        for i in range(1, 500, 1):
            color = gris[i, j]
            gris[i, j] = 255 - color

    gris = cv2.GaussianBlur(gris, (3, 3), 0)
    T1 = mahotas.thresholding.otsu(gris)
    clahe = cv2.createCLAHE(clipLimit=1.0)
    grises = clahe.apply(gris)

    T2 = mahotas.thresholding.otsu(grises)
    T = (T2 + T1 + 5) / 2

    for k in range(rois, rois + 90, 1):
        for z in range(xf, 800, 1):
            color = grises[k, z]
            if color > T:
                grises[k, z] = 0
            else:
                grises[k, z] = 255

    mascara = np.zeros(image.shape[:2], dtype="uint8")
    cv2.rectangle(mascara, (xf, rois), (xf + 800, rois + 90), 255, -1)
    image1 = cv2.bitwise_and(grises, grises, mask=mascara)

    blurred = cv2.GaussianBlur(image1, (7, 7), 0)
    blurred = cv2.medianBlur(blurred, 1)

    v = np.mean(blurred)
    sigma = 0.33
    lower = (int(max(0, (1.0 - sigma) * v)))
    upper = (int(min(255, (1.0 + sigma) * v)))

    edged = cv2.Canny(blurred, lower, upper)
    img, contours, _ = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    contours = sorted([(c, cv2.boundingRect(c)[0]) for c in contours], key=lambda x: x[1])
    meter = 4
    second_meter = 1

    consumption = 0
    for (c, _) in contours:
        (x, y, w, h) = cv2.boundingRect(c)
        if w > 11 and h > 13 and w < 100:
            if (x - xfx) > 10:
                if second_meter < 6:
                    xfx = x + w
                    roi2 = gris[y:y + h, x:x + w]
                    roi = utils.recognition_borders(roi2)
                    roi_small = cv2.resize(roi, (10, 10))
                    roi_small = roi_small.reshape((1, 100))
                    roi_small = np.float32(roi_small)
                    retval, results, neigh_resp, dists = model.findNearest(roi_small, k=1)

                    digit = utils.update_values(results, meter)
                    consumption = int(consumption) + int(digit)
                    second_meter += 1
                    meter -= 1

    return consumption
