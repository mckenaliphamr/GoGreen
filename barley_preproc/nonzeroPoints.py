import tifffile
import scipy.ndimage
import os
import sparse

def writePoints(infile,outfile):
	in_data = tifffile.imread(infile)
	in_sp = sparse.COO(in_data)
	with open(outfile,'w') as f:
		for z,y,x in zip(*in_sp.coords):
			f.write(str(x)+' '+str(y)+' '+str(z)+'\n')

def main():
	for r,d,f in os.walk('./seedImages'):
		for fname in f:
			sname = os.path.splitext(fname)[0]
			writePoints(r+'/'+fname,'./seedPoints/'+sname+'.txt')

if __name__ == '__main__':
	main()