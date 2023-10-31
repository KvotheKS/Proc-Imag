import argparse as prs
import numpy as np
import cv2 as cv
import os
import random

parser = prs.ArgumentParser('TrabProcImag', 'Coloring Thresholding')
# parser.add_argument('filename')
parser.add_argument('-i', '--image', required=True)
parser.add_argument('-r', '--rpath', required=True)
parser.add_argument('-n', '--number')
parser.add_argument('-t', '--tries', default=10)
parser.add_argument('-l', '--leniancy', default=5)
args = parser.parse_args()

def lbg(img):
    # img = cv.imread(img_path)
    k = int(args.number)
    k_centers = np.random.randint(0,255, (k,3)).astype(np.double)
    tries = int(args.tries)
    leniancy = args.leniancy
    
    for i in range(0,tries):
        k_new = [[0,0,0] for k_ in range(k)]
        k_choices = [0 for k_ in range(k)]
        
        for p_x in img:
            for c_col in p_x:
                k_idx = np.abs(np.linalg.norm(k_centers-c_col,axis=1)).argmin()
                k_new[k_idx] += c_col
                k_choices[k_idx] += 1
        
        k_old = np.copy(k_centers)
    
        for k_ in range(k):
            # print([0 if k_choices[k_] == 0 else i / k_choices[k_] for i in k_new[k_]])
            k_centers[k_] = [0 if k_choices[k_] == 0 else i / k_choices[k_] for i in k_new[k_]]
        # print(k_centers)
        # exit()
        k_old -= k_centers
        k_old = np.linalg.norm(k_old,axis=1)
        k_old = k_old[k_old.argmax()]
        
        if k_old < leniancy: break
    
    return np.round(k_centers)

def kmeans(img, centers):
    # img = cv.imread(img_path).astype(np.double)
    
    # centers = lbg(img)
    # print(centers)
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            img[i][j] = centers[np.abs(np.linalg.norm(centers - img[i][j],axis=1)).argmin()]
    
    return img.astype(np.uint8)

def dithering(img, arr_list):
    # img = cv.imread(img_path).astype(np.double)
    # num = np.int32(args.number)
    ylim, xlim = img.shape[0], img.shape[1]
    for i in range(ylim):
        for j in range(xlim):
            val = img[i][j].copy()
            newval = arr_list[np.abs(np.linalg.norm(arr_list - val, axis=1)).argmin()]
            qerr = val - newval
            img[i][j] = newval

            ylimflag = i+1 < ylim
            
            if ylimflag:
                img[i+1][j] = img[i+1][j] + ((qerr * 5) / 16)
            
                if j+1 < xlim:
                    img[i+1][j+1] = img[i+1][j+1] + ((qerr * 1) / 16)
            
            if j > 0 and ylimflag:
                img[i+1][j-1] = img[i+1][j-1] + ((qerr * 3) / 16)
            
            if j+1 < xlim:
                img[i][j+1] = img[i][j+1] + ((qerr * 7) / 16)

    return img.astype(np.uint8)

img = cv.imread(args.image).astype(np.double)
palette = lbg(img.copy())
           
os.makedirs(os.path.dirname(args.rpath.format('dither')), exist_ok=True)
os.makedirs(os.path.dirname(args.rpath.format('kmeans')), exist_ok=True)

cv.imwrite(args.rpath.format('kmeans'), kmeans(img.copy(), palette.copy()))
cv.imwrite(args.rpath.format('dither'), dithering(img.copy(), palette.copy()))