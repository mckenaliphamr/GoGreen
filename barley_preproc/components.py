import tifffile as tf
import scipy.ndimage as ndi
import argparse
import os
import numpy as np

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('in_tiff',help='input tiff file')
    parser.add_argument('out_dir',help='output directory')
    parser.add_argument('--compress',help='compression',nargs=1,type=int,default=6)
    args = parser.parse_args()
    out_dir = args.out_dir

    path,fname = os.path.split(args.in_tiff)
    basefname = os.path.splitext(fname)[0]
    # print(args.in_tiff,path,fname,basefname)

    img = tf.imread(args.in_tiff)
    d,h,w = img.shape
    print(w,h,d)

    labels,num = ndi.label(img, structure=ndi.generate_binary_structure(img.ndim, 1))
    print(num,'components')
    regions = ndi.find_objects(labels)

    hist,bins = np.histogram(labels, bins=num, range=(1,num+1))
    sz_hist = ndi.sum(hist)
    print('hist', hist)
    print('size =',sz_hist)

    argsort_hist = np.argsort(hist)[::-1]

    flex = 2

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

            tf.imwrite('{}/{}_l{}_x{}_y{}_z{}.tif'.format(out_dir,basefname,j,x0,y0,z0),box,photometric='minisblack',compress=3)


if __name__ == '__main__':
    main()
