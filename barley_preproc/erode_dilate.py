import os
import argparse
import tifffile as tf
from scipy import ndimage as ndi
from scipy.signal import medfilt
import numpy as np
#import cv2

src = '/home/ejam/documents/barley_stacks/preproc/gauss/'
dst = '/home/ejam/documents/barley_stacks/preproc/erdi/'
sname = 'S011'

img = tf.imread(src+sname+'.tif')

print(sname+'.tif', img.dtype, img.shape)

newdata = ndi.grey_erosion(img, mode = 'constant', size=(7,7,7))

print('Erosion done!')

newdata = ndi.grey_dilation(newdata, mode = 'constant', size=(5,5,5))
print('Dilation done!')

#blur = cv2.blur(in_data,(5,5,5))

img[newdata < 30] = 0
tf.imwrite(dst+sname+'.tif',img,photometric='minisblack',compress=2)

