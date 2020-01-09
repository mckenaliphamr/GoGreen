import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import tifffile
import scipy.ndimage
import os
import math

def angle(x0,y0,x1,y1,x2,y2):
    vx0 = x0-x1
    vy0 = y0-y1
    vx1 = x2-x1
    vy1 = y2-y1
    det = vx0*vy1-vy0*vx1
    dot = vx0*vx1+vy0*vy1
    return -math.atan2(det,dot)

def main():
    img = dict()
    src = '/home/ejam/documents/barley_stacks/preproc/comps/'
    sname = 'S017'
    for r,d,f in os.walk(src+sname):
        for fname in f:
            img[fname] = tifffile.imread(r+'/'+fname)

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

    marker = [fname for fname in boxes if boxes[fname][2]<200 and boxes[fname][5]<300][0]
    mcx,mcy = boxes[marker][0]+boxes[marker][3]/2,boxes[marker][1]+boxes[marker][4]/2
    ix,iy = 750,450

    markerAngle = 5
    colorAbbrev = 'RGOB'
    colors = ['crimson','limegreen','orange','royalblue']
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.plot([ix,ix],[iy,iy],[0,500],c='black')

    for theta,color in zip([45,135,225,315],colors):
        ax.plot([ix+(mcx-ix)*math.cos((theta-markerAngle)*math.pi/180)+(mcy-iy)*math.sin((theta-markerAngle)*math.pi/180),ix],[iy-(mcx-ix)*math.sin((theta-markerAngle)*math.pi/180)+(mcy-iy)*math.cos((theta-markerAngle)*math.pi/180),iy],[0,0],c=color)


    for fname in boxes:
        print(fname, boxes[fname])
        x,y,z,w,h,d,l = boxes[fname]
        theta = (angle(mcx,mcy,ix,iy,x+w/2,y+h/2)*180/math.pi+markerAngle)%360
        print(theta)
        if fname==marker:
            c = 'black'
            cl = '#'
        else:
            ci = 0 if theta<90 else 1 if theta<180 else 2 if theta<270 else 3
            c = colors[ci]
            cl = colorAbbrev[ci]
        cx,cy = x+w/2,y+h/2
        ax.plot([x,x,x,x,x+w,x+w,x+w,x+w,x],[y,y,y+h,y+h,y+h,y+h,y,y,y],[z,z+d,z+d,z,z,z+d,z+d,z,z],c=c)
        ax.text(x+w/2,y+h/2,z+d,'{} {}'.format(cl,l),None,color=c,ha='center',va='center')

    plt.show()

if __name__ == '__main__':
    main()
