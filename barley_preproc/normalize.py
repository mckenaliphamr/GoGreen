files = ['S010','S011','S012','S013','S014','S015','S016','S017','S018','S019']

import numpy as np
from matplotlib import pyplot as plt
import tifffile as tf
import math
import importlib
from unionfind import neoneopersistence
sname = 'S017'
C = None

for sname in files:
    print('> starting with ',sname)
    img = tf.imread('../'+sname+'.tif')
    hist,bins = np.histogram(img,bins=256,range=(0,256))
    tot = img.size
    # hist[0] = 0
    # blur = [sum(hist[i+j]*a if 0<=i+j<len(hist) else 0 for j,a in kernel) for i in range(len(hist))]
    # btot = sum(blur)

    cumul = []
    s = 0
    for v in hist:
        s += v
        cumul.append(s)

    pers = sorted(neoneopersistence(hist),reverse=True)
    print(sname,': pers',pers)

    if not C:
        p0,p1,p2 = pers[:3]
        x0,x1,x2 = p0[2],p1[2],p2[2]
        anchors = [cumul[x0]/tot,cumul[x1]/tot,cumul[x2]/tot]
    else:
        x = np.array([1.,2.,3.])
        for i,a in enumerate(anchors):
            for j,s in enumerate(cumul):
                if s>a*tot:
                    print('[',i,',',j,']: ',s,'>',a,'*',tot,'=',a*tot)
                    break
            if j > 0:
                x[i] = j-1+(a*tot-cumul[j-1])/(cumul[j]-cumul[j-1])
            else:
                x[i] = 0
    if not C:
        C = 1
        y = np.array([x0,x1,x2])
        plt.axvline(y[0])
        plt.axvline(y[1])
        plt.axvline(y[2])
        plt.plot([b for b in bins[:-1]],[log(h+1) for h in hist], label = sname)
    else:
        npz = np.polyfit(x,y,2)
        plt.plot([npz[0]*b*b + npz[1]*b + npz[2] for b in bins[:-1]],[log(h+1) for h in hist], label = sname)

    # plt.plot([X0+(b-x0)*(X1-X0)/(x1-x0) for b in bins[:-1]],[h*(x1-x0)/(X1-X0)/tot for h in hist])
    # plt.plot([m*x+b for x in bins[:-1]],[math.log(h+1) for h in hist], label=sname)
    # plt.plot([X0+(b-x0)*(X1-X0)/(x1-x0) for b in bins[:-1]],[h/tot for h in cumul])

plt.legend(bbox_to_anchor=(1.03,1.),loc=2,borderaxespad=0.)
plt.show()
