import tifffile as tf
import scipy.ndimage as ndi
import numpy as np
#import cv2

src = '/home/ejam/documents/barley_stacks/preproc/raw/'
dst = '/home/ejam/documents/barley_stacks/preproc/gauss/'
sname = 'S011'

img = tf.imread(src+sname+'.tif')

resol,stepsize,C = 256,16,1

if C:
    npz = np.arange(resol).astype('uint8')
    z11 = np.array([1.25468523e-04, 1.04264659e+00, 1.66969406e+00])
    for i in range(len(npz)):
        aux = round(z11[0]*npz[i]*npz[i]+z11[1]*npz[i]+z11[2])
        if aux < 256 and aux > 0:
            npz[i] = int(aux)
        elif aux > 255:
            npz[i] = 255
        else:
            npz[i] = 0

    with np.nditer(img, flags=['external_loop'], op_flags=['readwrite']) as it:
        for x in it:
            x[...] = npz[x]

print(img.dtype,img.shape)

blur = ndi.gaussian_filter(img,3, mode='constant',truncate=3)
img[blur < 55] = 0

tf.imwrite(dst+sname+'.tif',img,photometric='minisblack',compress=2)
