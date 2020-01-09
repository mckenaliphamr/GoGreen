import tifffile as tf
import scipy.ndimage as ndi
import argparse
import os
import sys
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

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('src',help='source directory')
    parser.add_argument('dst',help='dest directory')
    parser.add_argument('resol',help='resolution')
    parser.add_argument('C',help='normalize bool')
    parser.add_argument('flex',help='flex')
    parser.add_argument('sname',help='input tiff file')
    parser.add_argument('--compress',help='compression',nargs=1,type=int,default=6)

    args = parser.parse_args()
    src = args.src
    dst = args.dst
    resol = int(args.resol)
    C = int(args.C)
    flex = int(args.flex)
    sname = args.sname[:-4]

    img = tf.imread(src+'raw/'+sname+'.tif')
    print(sname, img.shape)

    if C:
        npz = np.arange(resol, dtype = 'uint8')
        z11 = np.array([2.60816755e-04, 9.86351883e-01, 2.96785144e+00])
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

    print('Normalized !')

    blur = ndi.gaussian_filter(img,3, mode='constant',truncate=3)
    img[blur < 55] = 0

    print('Gauss-blurred!')
    tf.imwrite(src+'gauss/'+sname+'.tif',img,photometric='minisblack',compress=2)

    blur = ndi.grey_erosion(img, mode = 'constant', size=(7,7,7))
    print('Erosion done!')

    blur = ndi.grey_dilation(blur, mode = 'constant', size=(5,5,5))
    print('Dilation done!')

    img[blur < 30] = 0
    tf.imwrite(src+'erdi/'+sname+'.tif',img,photometric='minisblack',compress=2)

    img = clean_zeroes(img)

    blur = ndi.grey_opening(img, mode='constant', size=(1,11,11))
    print('Cleaned!')

    img[blur < 20] = 0

    img = clean_zeroes(img)

    tf.imwrite(src+'clean/'+sname+'.tif',img,photometric='minisblack',compress=2)

    labels,num = ndi.label(img, structure=ndi.generate_binary_structure(img.ndim, 1))
    print(num,'components')
    regions = ndi.find_objects(labels)

    hist,bins = np.histogram(labels, bins=num, range=(1,num+1))
    sz_hist = ndi.sum(hist)
    print('hist', hist)
    print('size =',sz_hist)

    argsort_hist = np.argsort(hist)[::-1]

    for j in range(len(regions)):
        i = argsort_hist[j]
        r = regions[i]
        if(hist[i]/sz_hist > 1e-2):
            z0,y0,x0,z1,y1,x1 = r[0].start,r[1].start,r[2].start,r[0].stop,r[1].stop,r[2].stop
            mask = labels[r]==i+1
            box = img[r].copy()
            box[~mask] = 0
            mass = 1.0/np.sum(box)
            grow = np.arange(box.shape[0], dtype = 'float64')
            grow[0] = np.sum(box[0,:,:])

            for k in range(1,len(grow)):
                zmass = np.sum(box[k,:,:])
                grow[k] = grow[k-1] + zmass

            if grow[-1] != np.sum(box):
                print('grow[-1] != np.sum(box)', j, args.in_tiff)
                break

            grow = grow*mass
            logdiff = np.abs(np.ediff1d(np.gradient(np.log(grow))))
            critic = []

            for k in range(len(logdiff)-1,0,-1):
                if(logdiff[k] > 1e-6):
                    critic.append(k)
                    if(len(critic) > flex):
                        break

            if(np.sum(np.ediff1d(critic) == -1) == flex):
                k = critic[0]+1

            print('{} (x,y,z)=({},{},{}), (w,h,d)=({},{},{})'.format(j,x0,y0,z0,box.shape[2],box.shape[1],box.shape[0]))
            print(box.shape[0], critic, logdiff[-1])

            if( k+1 < box.shape[0]):
                print('Reduced from',box.shape[0],'to',k)
                box = box[:k,:,:]

            tf.imwrite('{}{}_l{}_x{}_y{}_z{}.tif'.format(dst,sname,j,x0,y0,z0),box,photometric='minisblack',compress=3)


if __name__ == '__main__':
    main()
