import os
import subprocess
import argparse

# python processAll.py 'D:/Barley Project/' './out/noAir' --meta './meta/slopeIntercept.txt'
# python processAll.py 'D:/Barley Project/' './out/noAir' --meta './meta/slopeIntercept.txt' --overwrite

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('in_dir',help='input directory')
	parser.add_argument('out_dir',help='output directory')
	parser.add_argument('--meta',help='file with tab-delimited lines: yname\tslope\tintercept',type=str)
	parser.add_argument('--overwrite',action='store_true')
	args = parser.parse_args()

	baseDir = args.in_dir
	outDir = args.out_dir

	slopes,intercepts = dict(),dict()
	if args.meta and os.path.isfile(args.meta):
		with open(args.meta) as f:
			lines = f.read().split('\n')
			for l in lines:
				fields = l.split('\t')
				if len(fields)<3:
					continue
				name,slope,intercept = fields
				slopes[name],intercepts[name] = float(slope),float(intercept)
	else:
		print('No slopes and intercepts given, using 1 and 0')

	jobid = 0
	for (path,d,f) in os.walk(baseDir):
		if path.endswith(' Slices'):
			_,dirName = os.path.split(path)
			dirTerms = dirName.split(' ')
			Yname = ' '.join(dirTerms[:2])
			sname = dirTerms[0]
			slope = slopes.get(Yname,1)
			intercept = intercepts.get(Yname,0)
			code = 'int r=3; float wtSum = 0.; float wtTot = 0.; for (int x=-r;x<=r;x+=1) for (int y=-r;y<=r;y+=1) for (int z=-r;z<=r;z+=1) {{vec3 q = vec3(x,y,z); float wt = 1.; wtTot += wt; wtSum += {}*texture(tex,p+texelSize*vec3(x,y,z)).r*wt+{};}} float lum = texture(tex,p).r; if (wtSum/wtTot<.185) lum = 0; return lum;'
			outFile = '{}/{}.tif'.format(outDir,sname)
			# cmd = ['python3','convertTexture.py','--tex','{}/{}_*.tif'.format(path,Yname),'--code',code.format(slope,intercept),outFile]

			cmd = ['python3','convertTexture.py','--tex','"{}/{}_*.tif"'.format(path,Yname),'--code','"{}"'.format(code.format(slope,intercept)),'"{}"'.format(outFile)]
			print('jobCmd[{}]='.format(jobid)+' '.join(cmd))
			jobid += 1

			# print(sname)
			# if args.overwrite or not os.path.isfile(outFile):
			# 	subprocess.run(cmd)
			# else:
			# 	print('Already exists. Run with --overwrite to ignore this check.')
			# print('Done')
	numjobs = jobid