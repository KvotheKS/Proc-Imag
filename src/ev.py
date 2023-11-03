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
                img2[i][j] = img[i][np.clip(np.int32(jl + j * ratio), 0, jr)]
    return img2

def TA(A, B, C):
    return np.abs( (B[0] * A[1] - A[0] * B[1]) + (C[0] * B[1] - B[0] * C[1]) + (A[0] * C[1] - C[0] * A[1]) ) / 2

def ib(A,B,C):
    return A>=B and A<C

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

    r_img = np.zeros((ylim+1,xlim+1), dtype=np.uint8)
    
    center = np.array([[xlim], [ylim]],dtype = np.double) / 2

    A = np.round(np.reshape(A + center, (2)))
    B = np.round(np.reshape(B + center, (2)))
    C = np.round(np.reshape(C + center, (2)))
    D = np.round(np.reshape(D + center, (2)))


    ylim, xlim = r_img.shape[0], r_img.shape[1]
    rect_area = img.shape[0] * img.shape[1]
    ylimorg, xlimorg = img.shape[0], img.shape[1]
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


r1 = entopify(img.copy())


r2 = rotate(r1.copy(), r_rot)


# Inverse Operations
r3 = rotate(r2.copy(), l_rot)
c1 = np.array([img.shape[0], img.shape[1]], dtype=np.int32) // 2
c2 = np.array([r3.shape[0], r3.shape[1]], dtype=np.int32) // 2
r3 = r3.copy()[c2[0]-c1[0]:c1[0]+c2[0],c2[1]-c1[1]:c1[1]+c2[1]]

r4 = entopify(r3.copy(), True)


# cv.imwrite(args.rpath.format(2), r_img)

def sympad(img, y, x):
    rimg = np.zeros((y,x))
    yl, xl = (y - img.shape[0]) // 2, (x-img.shape[1]) // 2
    rimg[yl:yl+img.shape[0],xl:xl+img.shape[1]] = img[:,:]
    return rimg

y = max(img.shape[0], r1.shape[0],r2.shape[0],r3.shape[0],r4.shape[0])
x = max(img.shape[1], r1.shape[1],r2.shape[1],r3.shape[1],r4.shape[1])
img = sympad(img, y, x)
r1 = sympad(r1, y, x)
r2 = sympad(r2, y, x)
r3 = sympad(r3, y, x)
r4 = sympad(r4, y, x)
r5 = sympad(r4-img+128, y, x)

cv.imwrite(args.rpath.format(0), img)
cv.imwrite(args.rpath.format(1), r1)
cv.imwrite(args.rpath.format(2), r2)
cv.imwrite(args.rpath.format(3), r3)
cv.imwrite(args.rpath.format(4), r4)
cv.imwrite(args.rpath.format(5), r5)