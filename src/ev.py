import argparse as prs
import numpy as np
import cv2 as cv
import os
import random
import math

parser = prs.ArgumentParser('TrabProcImag', 'Coloring Thresholding')
# parser.add_argument('filename')
parser.add_argument('-i', '--image', required=True)
parser.add_argument('-r', '--rpath', required=True)
args = parser.parse_args()

# os.makedirs(args.rpath, exist_ok=True)

def entopify(img, inverse=False, trapezium_rate = 0.2):
    img2 = np.zeros(img.shape)
    ic = np.array([img.shape[0], img.shape[1]], dtype=np.double) / 2
    ic2 = np.array([img2.shape[0], img2.shape[1]], dtype=np.double) / 2
    
    for i in range(img2.shape[0]):
        ratio = (1 - trapezium_rate * ( i / (img2.shape[0] - 1) ))
        jl, jr = (img2.shape[1] - 1) * (0.5 - ratio * 0.5), (img2.shape[1] - 1) * (0.5 + ratio * 0.5)
        jl, jr = np.int32(jl), np.int32(jr)
        if not inverse: 
            ratio = 1 / ratio
            for j in range(jl, jr + 1):
                img2[i][j] = img[i][np.clip(np.int32((j - jl) * ratio), 0, img2.shape[1]-1)]
        else:
            for j in range(img2.shape[1]):
                img2[i][j] = img[i][np.clip(np.int32(jl + j * ratio), 0, img2.shape[1] - 1)]
    return img2

def TA(A, B, C):
    return np.abs( (B[0] * A[1] - A[0] * B[1]) + (C[0] * B[1] - B[0] * C[1]) + (A[0] * C[1] - C[0] * A[1]) ) / 2

def rotate(img, rot_matrix):
    # diag_size = math.ceil(math.sqrt(img.shape[0]**2 + img.shape[1]**2))
    disloc = np.array([[img.shape[1]], [img.shape[0]]], dtype = np.double) / 2
        
    A, B, C, D = np.array([[0], [0]], dtype=np.double), np.array([[img.shape[1]],[0]], dtype=np.double), np.array([[0],[img.shape[0]]], dtype=np.double), np.array([[img.shape[1]], [img.shape[0]]], dtype=np.double)
    
    inv = rot_matrix.copy()
    inv[0][1] *= -1
    inv[1][0] *= -1
    
    A = np.matmul(rot_matrix, A - disloc)
    B = np.matmul(rot_matrix, B - disloc)
    C = np.matmul(rot_matrix, C - disloc)
    D = np.matmul(rot_matrix, D - disloc)

    x_min = np.min([A[0][0], B[0][0], C[0][0], D[0][0]])
    y_min = np.min([A[1][0], B[1][0], C[1][0], D[1][0]])
    x_max = np.max([A[0][0], B[0][0], C[0][0], D[0][0]])
    y_max = np.max([A[1][0], B[1][0], C[1][0], D[1][0]])

    xlim, ylim = np.round(x_max-x_min).astype(np.int32), np.round(y_max-y_min).astype(np.int32)

    r_img = np.zeros((ylim,xlim), dtype=np.uint8)
    
    center = np.array([[xlim], [ylim]],dtype = np.double) / 2

    A = np.round(np.reshape(A + center, (2)))
    B = np.round(np.reshape(B + center, (2)))
    C = np.round(np.reshape(C + center, (2)))
    D = np.round(np.reshape(D + center, (2)))


    ylim, xlim = r_img.shape[0], r_img.shape[1]
    rect_area = img.shape[0] * img.shape[1]

    for i in range(ylim):
        for j in range(xlim):
            P = np.array([j,i], dtype=np.double)
            tr = TA(A,P,D) + TA(D,P,C) + TA(C,P,B) + TA(P,B,A)
            if rect_area >= tr:
                c_loc = np.matmul(inv, np.array([[j],[i]], dtype=np.double) - center) + disloc
                c_loc = np.round(c_loc).astype(np.uint32)
    
                r_img[i][j] = img[np.clip(c_loc[1][0], 0, img.shape[0]-1)][np.clip(c_loc[0][0], 0, img.shape[1]-1)]
    
    return r_img

os.makedirs(os.path.dirname(args.rpath),exist_ok=True)

m4 = math.pi / 4

l_rot = np.array([[math.cos(m4), math.sin(m4)], [-math.sin(m4), math.cos(m4)]])
r_rot = np.array([[math.cos(m4), -math.sin(m4)], [math.sin(m4), math.cos(m4)]])

img = cv.imread(args.image,0).astype(np.uint8)

r_img = rotate(entopify(img.copy()), r_rot)

cv.imwrite(args.rpath.format(1), r_img)

# Inverse Operations
r_img = rotate(r_img, l_rot)

c1 = np.array([img.shape[0], img.shape[1]], dtype=np.int32) // 2
c2 = np.array([r_img.shape[0], r_img.shape[1]], dtype=np.int32) // 2
r_img = r_img[c2[0]-c1[0]:c1[0]+c2[0],c2[1]-c1[1]:c1[1]+c2[1]]
r_img = entopify(r_img, True)


cv.imwrite(args.rpath.format(2), r_img)