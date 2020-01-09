import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import tifffile
import scipy.ndimage
import os
import argparse

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('in_path',help='input tiff file or directory')
	parser.add_argument('min_size',help='minimum w*h*d',nargs='?',default=0,type=int)
	args = parser.parse_args()

	files = []
	if os.path.isdir(args.in_path):
		for r,_,fnames in os.walk(args.in_path):
			for fname in fnames:
				files.append((r+'/'+fname))
	elif os.path.isfile(args.in_path):
		files.append(args.in_path)

	print('Found {} file{}'.format(len(files),'' if len(files)==1 else 's'))
	for f in files:
		img = tifffile.imread(f)
		d,h,w = img.shape
		if d*h*w>=args.min_size:
			print(f,w,h,d)
			tifffile.imshow(img,title=f)
			# tifffile.imshow(img,title=f,cmap=plt.cm.magma)
			plt.show()

if __name__ == '__main__':
	main()