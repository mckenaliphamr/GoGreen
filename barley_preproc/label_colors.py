#!/usr/bin/python3

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import tifffile as tf
import os
import sys
import math

def main():
    src = '/home/ejam/documents/barley_stacks/preproc/comps/'
    sname = sys.argv[1]

    img = dict()
    for r,d,f in os.walk(src + sname):
        for fname in f:
            img[fname] = tf.imread(r+'/'+fname)

    if len(img) > 5 or len(img) < 2:
        print('Found',len(img),'connected components. Expected between 2 and 5. Aborting.')
        exit()

    boxes = dict()
    for fname in img:
        fields = fname.split('_')
        for f in fields:
            if f and f[0] in 'lxyz':
                v = ''
                for c in f[1:]:
                    if c not in '0123456789':
                        break
                    v += c
                v = int(v)
                if f[0]=='x':
                    x = v
                if f[0]=='y':
                    y = v
                if f[0]=='z':
                    z = v
                if f[0]=='l':
                    l = v
        d,h,w = img[fname].shape
        if w*h*d>100000:
            boxes[fname] = (x,y,z,w,h,d,l)
        if l == len(img) - 1:
            marker = fname

    taxicab = dict()
    x,y = boxes[marker][:2]
    x += boxes[marker][3]
    y += boxes[marker][4]
    del img[marker]

    if x < y:
        for fname in img:
            taxicab[fname] = math.fabs(boxes[fname][0] - x) + math.fabs(boxes[fname][1] + 0.75*boxes[fname][4] - y)
    else:
        for fname in img:
            taxicab[fname] = math.fabs(boxes[fname][0] + 0.75*boxes[fname][3] - x) + math.fabs(boxes[fname][1] - y)


    colors = dict()
    red = min(taxicab, key=lambda key: taxicab[key])
    colors[red] = 'Red'

    if len(boxes) == 5:
        orange = max(taxicab, key=lambda key: taxicab[key])
        colors[orange] = 'Orange'
        del taxicab[red]
        del taxicab[orange]
        minx,miny = math.inf, math.inf
        for fname in taxicab:
            if x < y:
                temp = boxes[fname][0] + 0.5*boxes[fname][3]
                if  temp - x < minx:
                    minx = temp - x
                    blue = fname
            else:
                temp = boxes[fname][1] + 0.5*boxes[fname][4]
                if temp - y < miny:
                    miny = temp - y
                    blue = fname

        #print(minx, bluex,'\n',miny, bluey)

        colors[blue] = 'Blue'
        del taxicab[blue]
        colors[min(taxicab)] = 'Green'
        colors[marker] = 'Black'

    for fname in colors:
        print(fname,'\t', colors[fname])

    fig = plt.figure()
    fig.suptitle(sname)
    ax = fig.add_subplot(111, projection='3d')

    for fname in boxes:
        x,y,z,w,h,d,l = boxes[fname]
        cx,cy = x+w/2,y+h/2
        ax.plot([x,x,x,x,x+w,x+w,x+w,x+w,x],[y,y,y+h,y+h,y+h,y+h,y,y,y],[z,z+d,z+d,z,z,z+d,z+d,z,z],c=colors[fname].lower())
        ax.text(x+w/2,y+h/2,z+d,'{} {}'.format('L', l),None, color=colors[fname].lower(), ha='center', va='center')

    plt.show()

    braces = '{}_'

    for fname in colors:
        splt = fname.split('_')
        cname = braces*len(splt) + '{}'
        cname = cname.format(sname,splt[1],colors[fname],*(splt[2:]))
        os.rename(src+sname+'/'+fname, src + sname + '/' + cname)

if __name__ == '__main__':
    main()
