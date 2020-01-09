import tifffile as tf
import scipy.ndimage as ndi
import argparse
import os
import numpy as np
import matplotlib.pyplot as plt

def faces_introduced(img, coords, max_val=255):
    z,y,x = coords
    t = img[coords]

    faces = []
    W,E,B,F,N,S,BW,BE,FW,FE,NE,SE,SW,NW,NB,NF,SB,SF,NBW,NBE,NFW,NFE,SBW,SBE,SFW,SFE = [False]*26
    if img[z,y,x] == 0:
        return 0

    # Check if boundary
    if x-1 < 0 or x+1 > max_val:
        faces.append(1) # add 4 vertices - 4 edges + 1 face
    if y-1 < 0 or y+1 > max_val:
        faces.append(1)
    if z-1 < 0 or z+1 > max_val:
        faces.append(1)

    # Check for 6 faces
    if x > 0 and (img[z,y,x-1] == 0 or img[z,y,x-1] >= t):
        W = True
        faces.append(1) # add one face
    if x < max_val and (img[z,y,x+1] == 0 or img[z,y,x+1] > t):
        E = True
        faces.append(1)

    if y > 0 and (img[z,y-1,x] == 0 or img[z,y-1,x] >= t):
        B = True
        faces.append(1) # add one face
    if y < max_val and (img[z,y+1,x] == 0 or img[z,y+1,x] > t):
        F = True
        faces.append(1)

    if z > 0 and (img[z-1,y,x] == 0 or img[z-1,y,x] >= t):
        S = True
        faces.append(1) # add one face
    if z < max_val and (img[z+1,y,x] == 0 or img[z+1,y,x] > t):
        N = True
        faces.append(1)

    # Check for 12 edges
    if W and B and (img[z,y-1,x-1] == 0 or img[z,y-1,x-1] >= t):
        BW = True
        faces.append(-1) # add one edge
    if E and B and (img[z,y-1,x+1] == 0 or img[z,y-1,x+1] > t):
        BE = True
        faces.append(-1) # add one edge
    if W and F and (img[z,y+1,x-1] == 0 or img[z,y+1,x-1] > t):
        FW = True
        faces.append(-1) # add one edge
    if E and F and (img[z,y+1,x+1] == 0 or img[z,y+1,x+1] > t):
        FE = True
        faces.append(-1) # add one edge

    if B and S and (img[z-1,y-1,x] == 0 or img[z-1,y-1,x] >= t):
        SB = True
        faces.append(-1) # add one edge
    if F and S and (img[z-1,y+1,x] == 0 or img[z-1,y+1,x] > t):
        SF = True
        faces.append(-1) # add one edge
    if B and N and (img[z+1,y-1,x] == 0 or img[z+1,y-1,x] > t):
        NB = True
        faces.append(-1) # add one edge
    if F and N and (img[z+1,y+1,x] == 0 or img[z+1,y+1,x] > t):
        NF = True
        faces.append(-1) # add one edge

    if W and S and (img[z-1,y,x-1] == 0 or img[z-1,y,x-1] >= t):
        SW = True
        faces.append(-1) # add one edge
    if W and N and (img[z+1,y,x-1] == 0 or img[z+1,y,x-1] > t):
        NW = True
        faces.append(-1) # add one edge
    if E and S and (img[z-1,y,x+1] == 0 or img[z-1,y,x+1] > t):
        SE = True
        faces.append(-1) # add one edge
    if E and N and (img[z+1,y,x+1] == 0 or img[z+1,y,x+1] > t):
        NE = True
        faces.append(-1) # add one edge

    # Check for 8 vertices
    if W and B and S and BW and SB and SW and (img[z-1,y-1,x-1] == 0 or img[z-1,y-1,x-1] >= t):
        SBW = True
        faces.append(1) # add one vertex
    if E and B and S and BE and SB and SE and (img[z-1,y-1,x+1] == 0 or img[z-1,y-1,x+1] > t):
        SBE = True
        faces.append(1) # add one vertex
    if W and F and S and FW and SF and SW and (img[z-1,y+1,x-1] == 0 or img[z-1,y+1,x-1] > t):
        SFE = True
        faces.append(1) # add one vertex
    if E and F and S and FE and SF and SE and (img[z-1,y+1,x+1] == 0 or img[z-1,y+1,x+1] > t):
        SBE = True
        faces.append(1) # add one vertex

    if W and B and N and BW and NB and NW and (img[z+1,y-1,x-1] == 0 or img[z+1,y-1,x-1] > t):
        NBW = True
        faces.append(1) # add one vertex
    if E and B and N and BE and NB and NE and (img[z+1,y-1,x+1] == 0 or img[z+1,y-1,x+1] > t):
        NBE = True
        faces.append(1) # add one vertex
    if W and F and N and FW and NF and NW and (img[z+1,y+1,x-1] == 0 or img[z+1,y+1,x-1] > t):
        NFE = True
        faces.append(1) # add one vertex
    if E and F and N and FE and NF and NE and (img[z+1,y+1,x+1] == 0 or img[z+1,y+1,x+1] > t):
        NBE = True
        faces.append(1) # add one vertex

    faces.append(-1) # add the cube itself
    return sum(append)

def ecg(img, max_val=255):

    euler_changes = np.zeros(max_val+1, dtype='int64')

    it = np.nditer(img, flags=['multi_index'])

    while not it.finished:
        t = img[it.multi_index]
        changes = faces_introduced(img,it.multi_index)
        b = it.iternext
        euler_changes[t] += changes

    return euler_changes

