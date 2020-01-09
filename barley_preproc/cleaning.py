import os
import argparse
import tifffile as tf
from scipy import ndimage as ndi
import numpy as np

def clean_zeroes(img):
    dim = img.ndim
    orig_size = img.size

    cero = list(range(2*dim))

    for k in range(dim):
        ceros = np.all(img == 0, axis = (k, (k+1)%dim))

        for i in range(len(ceros)):
            if(~ceros[i]):
                break
        for j in range(len(ceros)-1, 0, -1):
            if(~ceros[j]):
                break
        cero[k] = i
        cero[k+dim] = j+1

    img = img[cero[1]:cero[4], cero[2]:cero[5], cero[0]:cero[3]]

    print(round(100-100*img.size/orig_size),'% reduction from input')

    return img


sname = 'S017'
src = '/home/ejam/documents/barley_stacks/preproc/erdi/'
dst = '/home/ejam/documents/barley_stacks/preproc/clean/'
img = tf.imread(src+sname+'.tif')

print(sname+'.tif', img.dtype, img.shape)

img = clean_zeroes(img)

opened = ndi.grey_opening(img, mode='constant', size=(1,11,11))
print('1st opening')

#opened = ndi.grey_opening(opened, mode='constant', size=(7,7,7))
print('2nd opening')

img[opened < 20] = 0

img = clean_zeroes(img)

tf.imwrite(dst+sname+'.tif',img,photometric='minisblack',compress=2)
