import argparse as prs
import numpy as np
import cv2 as cv
from skimage.filters import threshold_multiotsu

parser = prs.ArgumentParser('TrabProcImag', 'Coloring Thresholding')
# parser.add_argument('filename')
parser.add_argument('-f', '--function', required=True)
parser.add_argument('-m', '--method')
parser.add_argument('-i', '--image', required=True)
parser.add_argument('-r', '--rpath', required=True)
parser.add_argument('-n', '--number')
args = parser.parse_args()

def unpackgrayimg(img):
    return img if type(img) != str else cv.imread(img,0)

def grayThreshold(img_path):
    num = int(args.number)
    original_img = unpackgrayimg(img_path)
    result = np.array(original_img)
    step = 256 // num
    for r in range(step,257,step):
        l = r-step
        result[np.logical_and((original_img >= l),(original_img < r))] = np.uint8((r // step) - 1)*np.uint8((255 // (num - 1)))

    return result

def colorThreshold(img_path):
    (r,g,b) = cv.split(cv.imread(img_path))
    r,g,b = grayThreshold(r), grayThreshold(g), grayThreshold(b)
    return cv.merge((r,g,b))

def otsuThreshold(img_path):
    num = int(args.number)
    original_img = unpackgrayimg(img_path)
    resulting_thresholds = threshold_multiotsu(original_img, num)
    (w,h) = original_img.shape
    for i in range(w):
        for j in range(h):
            original_img[i][j] = resulting_thresholds[np.abs(resulting_thresholds - original_img[i][j]).argmin()]
    
    return original_img

def colorOtsu(img_path):
    (r,g,b) = cv.split(cv.imread(img_path))
    r,g,b = otsuThreshold(r), otsuThreshold(g), otsuThreshold(b)
    return cv.merge((r,g,b))

def dithering(img_path):
    img = unpackgrayimg(img_path).astype(np.int32)
    num = np.int32(args.number)
    step = 256 // num
    arr_list = np.array([np.int32((r // step) - 1)*np.int32((255 // (num - 1))) for r in range(step,257,step)])
    
    xlim, ylim = len(img), len(img[0])
    
    for j in range(ylim):
        for i in range(xlim):
            val = img[i][j]
            newval = arr_list[np.abs(arr_list - val).argmin()]
            img[i][j] = newval
            qerr = val - newval

            ylimflag = j+1 < ylim
            
            if i+1 < xlim:
                img[i+1][j] = np.int32(img[i+1][j] + ((qerr * 7) // 16))
            
                if ylimflag:
                    img[i+1][j+1] = np.int32(img[i+1][j+1] + ((qerr * 1) // 16))
            
            if i>0 and ylimflag:
                img[i-1][j+1] = np.int32(img[i-1][j+1] + ((qerr * 3) // 16))
            
            if ylimflag:
                img[i][j+1] = np.int32(img[i][j+1] + ((qerr * 5) // 16))

    return img.astype(np.uint8)

def colorDither(img_path):
    img = cv.imread(img_path)
    (r,g,b) = cv.split(img)
    r,g,b = dithering(r),dithering(g),dithering(b)
    return cv.merge((r,g,b))

function_dict = {
    'gray_threshold': {
        'simple': grayThreshold,   
        'dither': dithering,
        'otsu': otsuThreshold
    },
    'color_threshold': {
        'simple': colorThreshold,
        'dither': colorDither,
        'otsu': colorOtsu
    }
}

cv.imwrite(args.rpath, function_dict[args.function][args.method](args.image))