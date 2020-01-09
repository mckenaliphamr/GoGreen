import os
import numpy as np
import mahotas as mh
import matplotlib.pyplot as plt
import tifffile as tf
from scipy import ndimage as ndi

class UnionFind:
    def __init__(self,mergeF=None):
        self.V = dict()
        self.Vl = []
        self.parent = []
        self.size = []
        self.mergeF = mergeF
        self.data = dict()

    def add(self,v,data=None):
        if v not in self.V:
            i = len(self.V)
            self.V[v] = i
            self.Vl.append(v)
            self.parent.append(i)
            self.size.append(1)
            self.data[v] = data

    def find_parent(self,v):
        i = self.V[v]
        p = i
        while self.parent[p]!=p:
            p = self.parent[p]
        while i!=p:
            i,j = self.parent[i],i
            self.parent[j] = p
        return self.Vl[p]

    def find_size(self,v):
        return self.size[self.V[self.find_parent(v)]]

    # returns (new root,merged root)
    def merge(self,u,v):
        su = self.find_size(u)
        sv = self.find_size(v)
        pu = self.parent[self.V[u]]
        pv = self.parent[self.V[v]]
        if pu==pv:
            return (self.Vl[pu],None)
        d = self.mergeF(self.data[self.Vl[pu]],self.data[self.Vl[pv]])
        if sv<su:
            pu,pv,su,sv = pv,pu,sv,su
        self.parent[pv] = pu
        self.size[pu] = su+sv
        self.data[self.Vl[pu]] = d
        return (self.Vl[pu],self.Vl[pv])

    def getData(self,v):
        return self.data[self.find_parent(v)]

def persistence(f):
    def mergeF(a,b):
        m,e = max((a['max'],a['elder']),(b['max'],b['elder']))
        return {'max':m,'elder':e}
    fi = sorted(list(zip(f,range(len(f)))),reverse=True)
    uf = UnionFind(mergeF)
    pairs = []
    for v,i in fi:
        uf.add(i,{'max':v,'elder':i})
        if i-1 in uf.V and i+1 in uf.V:
            a = uf.getData(i-1)
            b = uf.getData(i+1)
            d,j = min((a['max'],a['elder']),(b['max'],b['elder']))
            if (d-v > 1e-1) and (v!=0):
                print('i,j,d,v: = ',i,j,d,v,d-v, d/v, (d-v)*d/v, (d-v)/d, (d-v)/v, (d-v)*(d-v)/d, (d-v)*(d-v)/v)
            pairs.append((d-v,i,j))
        if i-1 in uf.V:
            uf.merge(i-1,i)
        if i+1 in uf.V:
            uf.merge(i,i+1)
    pairs.append((float('inf'),None,fi[0][1]))
    return pairs

def neopersistence(f):
    def mergeF(a,b):
        m,e = max((a['max'],a['elder']),(b['max'],b['elder']))
        return {'max':m,'elder':e}
    fi = sorted(list(zip(f,range(len(f)))),reverse=True)
    uf = UnionFind(mergeF)
    pairs = []
    for v,i in fi:
        uf.add(i,{'max':v,'elder':i})
        if i-1 in uf.V and i+1 in uf.V:
            a = uf.getData(i-1)
            b = uf.getData(i+1)
            d,j = min((a['max'],a['elder']),(b['max'],b['elder']))
            pairs.append(((d-v)/d,i,j))
        if i-1 in uf.V:
            uf.merge(i-1,i)
        if i+1 in uf.V:
            uf.merge(i,i+1)
    pairs.append((float('inf'),None,fi[0][1]))
    return pairs

def neoneopersistence(f, threshold=1e4):
    def mergeF(a,b):
        m,e = max((a['max'],a['elder']),(b['max'],b['elder']))
        return {'max':m,'elder':e}
    fi = sorted(list(zip(f,range(len(f)))),reverse=True)
    uf = UnionFind(mergeF)
    pairs = []
    for v,i in fi:
        uf.add(i,{'max':v,'elder':i})
        if i-1 in uf.V and i+1 in uf.V:
            a = uf.getData(i-1)
            b = uf.getData(i+1)
            d,j = min((a['max'],a['elder']),(b['max'],b['elder']))
            if d-v > threshold:
                pairs.append(((d-v)/d,i,j))
        if i-1 in uf.V:
            uf.merge(i-1,i)
        if i+1 in uf.V:
            uf.merge(i,i+1)
    pairs.append((float('inf'),None,fi[0][1]))
    return pairs

def start_vals(img):
    hist,bins = np.histogram(img, bins=np.max(img), range=(0,np.max(img)))
    foo = 1
    while(hist[foo] == 0):
        foo += 1
    return foo

def thresholding(original, T=12, base_name='orange'):
    m,M = np.min(original), np.max(original)
    foo = start_vals(original)
    thresh = M + 1
    step_size = (M - foo)//T
    sname = 'T{}'.format(T)
    if not os.path.isdir(sname):
        os.makedirs(sname)

    img = np.copy(original)
    for i in range(T):
        mask = original < thresh
        img[~mask] = 0
        thresh -= step_size
        tf.imwrite('{}/{}_T{}_{:03d}.tif'.format(sname,base_name,T,T-i), img, photometric='minisblack', compress=3)

def count_holes(dir_name, extension='.tif', plotting = False, dpi = 300, transparent=True):
    total_holes = []
    i = 0
    for files in sorted(os.listdir(dir_name)):
        if files.endswith(extension):
            scan = os.path.join(dir_name,files)
            img = tf.imread(scan)
            img[img > 0] = -1
            skel = mh.thin(img)
            noholes = mh.morph.close_holes(skel)
            cskel = np.logical_not(skel)
            choles = np.logical_not(noholes)
            holes = np.logical_and(cskel,noholes)
            lab, n = mh.label(holes)
            total_holes.append(n)
            if plotting:
                fig = plt.figure()
                plt.imshow(img)
                plt.tight_layout(pad=0)
                fig.savefig(dir_name + '/binary_{}_{:03d}.png'.format(dir_name,i+1), dpi=dpi, transparent=transparent)
                plt.close(fig)
                fig = plt.figure()
                plt.imshow(skel)
                plt.tight_layout(pad=0)
                fig.savefig(dir_name + '/skel_{}_{:03d}.png'.format(dir_name,i+1), dpi=dpi, transparent=transparent)
                plt.close(fig)
                fig = plt.figure()
                plt.imshow(lab)
                plt.tight_layout(pad=0)
                fig.savefig(dir_name + '/labels_{}_{:03d}.png'.format(dir_name,i+1), dpi=dpi, transparent=transparent)
                plt.close(fig)
            i += 1

    return total_holes

def compute_holes(wkdir, extension='.tif', plotting = False, dpi = 300, transparent=True):

    if not os.path.isdir(wkdir):
        print('There is no directory',wkdir,'. No output generated!')
        return 1

    holes = count_holes(wkdir, extension, plotting, dpi, transparent)
    file = open(wkdir + '/holes.txt', 'w')
    for i in range(len(holes)):
        file.write('{},{}\n'.format(i+1,holes[i]))

def compute_comps(dir_name, extension='.tif'):
    if not os.path.isdir(dir_name):
        print('There is no directory',dir_name,'. No output generated!')
        return 1
    comps = []
    for files in sorted(os.listdir(dir_name)):
        if files.endswith(extension):
            scan = os.path.join(dir_name,files)
            img = tf.imread(scan)
            img[img > 0] = -1
            labels,num = ndi.label(img, structure=ndi.generate_binary_structure(img.ndim, 1))
            comps.append(num)

    comp_file = open(dir_name + '/components.txt', 'w')
    for i in range(len(comps)):
        comp_file.write('{},{}\n'.format(i+1,comps[i]))

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

def svd_dir_alignment(coords, nu, dim=3):

    u,s, vh = np.linalg.svd(coords, full_matrices=False)

    fnu = np.matmul(np.transpose(vh), nu)

    return fnu

    # seed = np.matmul(coords, np.transpose(vh))
    # seed = (seed - seed.min()).astype(int)

    # seed0,seed1,seed2 = np.vsplit(seed, 3)
    # seed0,seed1,seed2 = seed0.squeeze(), seed1.squeeze(), seed2.squeeze()

    # align = np.zeros((1+seed0.max(), 1+seed1.max(), 1+seed2.max()), dtype = 'uint8')
    # align[ seed0, seed1, seed2 ] = img[ np.nonzero(img) ]

    # tf.imwrite(sname+'_aligned.tif', align, photometric='minisblack',compress=3)

def ecc_dir_alignment(img, nu, sname, dim=3):
    new_img = np.zeros_like(img, dtype='uint8')

    coords0,coords1,coords2 = np.nonzero(img)
    coords0,coords1,coords2 = coords0 - np.mean(coords0), coords1 - np.mean(coords1), coords2 - np.mean(coords2)
    coords = np.transpose(np.vstack((coords0,coords1,coords2)))

    fnu = svd_dir_alignment(coords, nu, dim)
    print('fnu = ',fnu)
    heights = np.round(np.matmul(coords, fnu)).astype(int)
    print(heights.max(), heights.min(), heights.max() - heights.min())
    heights -= heights.min()
    foo = 255//heights.max()
    print(heights.max(), heights.min(), heights.max() - heights.min(), foo)
    heights = foo*heights.astype('uint8')
    new_img[np.nonzero(img)] = heights
    tf.imwrite(sname+'_aligned.tif', new_img, photometric='minisblack',compress=3)
