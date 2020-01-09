from pyglet import gl
import ctypes
import numpy as np
import tifffile
import time
import argparse
import os

SAFE_TEX_SIZE = 2750000000

render_vertexbuffer = gl.GLuint(0)
render_vao = gl.GLuint(0)
render_program = 0

framebuffer = gl.GLuint(0)
rendered_texture = gl.GLuint(0)
input_texture = gl.GLuint(0)

def compile_shader(shader_type, shader_source):
	shader_name = gl.glCreateShader(shader_type)
	src_buffer = ctypes.create_string_buffer(shader_source)
	buf_pointer = ctypes.cast(ctypes.pointer(ctypes.pointer(src_buffer)), ctypes.POINTER(ctypes.POINTER(ctypes.c_char)))
	length = ctypes.c_int(len(shader_source) + 1)
	gl.glShaderSource(shader_name, 1, buf_pointer, ctypes.byref(length))
	gl.glCompileShader(shader_name)

	success = gl.GLint(0)
	gl.glGetShaderiv(shader_name, gl.GL_COMPILE_STATUS, ctypes.byref(success))

	length = gl.GLint(0)
	gl.glGetShaderiv(shader_name, gl.GL_INFO_LOG_LENGTH, ctypes.byref(length))
	log_buffer = ctypes.create_string_buffer(length.value)
	gl.glGetShaderInfoLog(shader_name, length, None, log_buffer)

	for line in log_buffer.value[:length.value].decode('ascii').splitlines():
		print('GLSL: ' + line)

	assert success, 'Compiling of the shader failed.'

	return shader_name


def link_program(program):
	gl.glLinkProgram(program)

	length = gl.GLint(0)
	gl.glGetProgramiv(program, gl.GL_INFO_LOG_LENGTH, ctypes.byref(length))
	log_buffer = ctypes.create_string_buffer(length.value)
	gl.glGetProgramInfoLog(program, length, None, log_buffer)

	for line in log_buffer.value[:length.value].decode('ascii').splitlines():
		print('GLSL: ' + line)


def setup_render_program(code):
	vertex_shader = b'''
		attribute vec2 position;
		attribute vec2 texcoord;

		varying vec2 tex_coord;
		void main()
		{
			gl_Position = vec4(position, 0.0, 1.0);
			tex_coord = texcoord;
		}
	'''

	fragment_shader = ('''
		#version 420
		uniform float depth;
		uniform vec3 texelSize;
		uniform sampler3D tex;
		in vec2 tex_coord;
		layout (location=0) out vec4 out_color;

		float getlum(vec3 p) {'''+code+'''}

		void main() {
			float lum = getlum(vec3(tex_coord.x,tex_coord.y,depth));
			out_color = vec4(lum,lum,lum,1.);
		}
	''').encode()

	global render_program
	render_program = gl.glCreateProgram()
	gl.glAttachShader(render_program, compile_shader(gl.GL_VERTEX_SHADER, vertex_shader))
	gl.glAttachShader(render_program, compile_shader(gl.GL_FRAGMENT_SHADER, fragment_shader))
	link_program(render_program)


class VERTEX(ctypes.Structure):
	_fields_ = [
		('position', gl.GLfloat * 2),
		('texcoord', gl.GLfloat * 2)
	]


def setup_render_vertexbuffer():
	gl.glGenVertexArrays(1, ctypes.byref(render_vao))
	gl.glGenBuffers(1, ctypes.byref(render_vertexbuffer))

	loc_position = gl.glGetAttribLocation(render_program, ctypes.create_string_buffer(b'position'))
	loc_texcoord = gl.glGetAttribLocation(render_program, ctypes.create_string_buffer(b'texcoord'))

	if loc_position < 0:
		print('Warning: position is not used in the shader')
	if loc_texcoord < 0:
		print('Warning: texcoord is not used in the shader')

	gl.glBindVertexArray(render_vao)

	gl.glEnableVertexAttribArray(loc_position)
	gl.glEnableVertexAttribArray(loc_texcoord)

	gl.glBindBuffer(gl.GL_ARRAY_BUFFER, render_vertexbuffer)

	gl.glVertexAttribPointer(loc_position, 2, gl.GL_FLOAT, False, ctypes.sizeof(VERTEX), ctypes.c_void_p(VERTEX.position.offset))
	gl.glVertexAttribPointer(loc_texcoord, 2, gl.GL_FLOAT, False, ctypes.sizeof(VERTEX), ctypes.c_void_p(VERTEX.texcoord.offset))

	gl.glBindVertexArray(0)


def render_to_texture(in_size,out_size,view_z=None):
	z0,z1 = (0,in_size[2]) if view_z==None else view_z
	vertices = (VERTEX * 6)(
		((-1,-1),(0,0)),
		(( 1,-1),(1,0)),
		(( 1, 1),(1,1)),
		(( 1, 1),(1,1)),
		((-1, 1),(0,1)),
		((-1,-1),(0,0))
	)
	gl.glBindTexture(gl.GL_TEXTURE_3D,rendered_texture)
	gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, framebuffer)
	draw_buffers = (gl.GLenum * 1)(gl.GL_COLOR_ATTACHMENT0)
	gl.glDrawBuffers(1, draw_buffers)
	gl.glViewport(0, 0, out_size[0], out_size[1])
	gl.glUseProgram(render_program)
	loc_depth     = gl.glGetUniformLocation(render_program, ctypes.create_string_buffer(b'depth'))
	loc_texelSize = gl.glGetUniformLocation(render_program, ctypes.create_string_buffer(b'texelSize'))
	gl.glUniform3f(loc_texelSize,1/in_size[0],1/in_size[1],1/in_size[2])
	gl.glBindBuffer(gl.GL_ARRAY_BUFFER, render_vertexbuffer)
	gl.glBufferData(gl.GL_ARRAY_BUFFER, ctypes.sizeof(vertices), vertices, gl.GL_DYNAMIC_DRAW)
	gl.glBindVertexArray(render_vao)
	gl.glClearColor(0.0, 0.0, 0.0, 0.0)
	for z in range(out_size[2]):
		gl.glFramebufferTexture3D(gl.GL_FRAMEBUFFER, gl.GL_COLOR_ATTACHMENT0, gl.GL_TEXTURE_3D, rendered_texture, 0, z)
		fbs = gl.glCheckFramebufferStatus(gl.GL_FRAMEBUFFER)
		assert fbs == gl.GL_FRAMEBUFFER_COMPLETE, 'FramebufferStatus is {}'.format(fbs)
		gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
		gl.glUniform1f(loc_depth,(z0+z*(z1-z0))/in_size[2]/out_size[2])
		gl.glBindTexture(gl.GL_TEXTURE_3D,input_texture)
		gl.glDrawArrays(gl.GL_TRIANGLES, 0, 6)
		if z%10==0:
			gl.glFinish()
			print('\033[K{}/{}'.format(z,out_size[2]-1),end='\r')
	gl.glFinish()

	gl.glBindVertexArray(0)


def setup_framebuffer():
	gl.glGenFramebuffers(1, ctypes.byref(framebuffer))
	gl.glGenTextures(1, ctypes.byref(input_texture))
	gl.glGenTextures(1, ctypes.byref(rendered_texture))

	gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, framebuffer)

	# Set up the input texture
	gl.glBindTexture(gl.GL_TEXTURE_3D, input_texture)
	gl.glTexParameteri(gl.GL_TEXTURE_3D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
	gl.glTexParameteri(gl.GL_TEXTURE_3D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)
	gl.glTexParameteri(gl.GL_TEXTURE_3D, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE)
	gl.glTexParameteri(gl.GL_TEXTURE_3D, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE)
	gl.glTexParameteri(gl.GL_TEXTURE_3D, gl.GL_TEXTURE_WRAP_R, gl.GL_CLAMP_TO_EDGE)

	# Set up the render target texture
	gl.glBindTexture(gl.GL_TEXTURE_3D, rendered_texture)
	gl.glTexParameteri(gl.GL_TEXTURE_3D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
	gl.glTexParameteri(gl.GL_TEXTURE_3D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)

def attach_input(in_data,in_size):
	# Load input
	gl.glBindTexture(gl.GL_TEXTURE_3D, input_texture)
	glTypeFromNp = {
		np.dtype('uint8'):   gl.GL_UNSIGNED_BYTE,
		np.dtype('uint16'):  gl.GL_UNSIGNED_SHORT,
		np.dtype('uint32'):  gl.GL_UNSIGNED_INT,
		np.dtype('float32'): gl.GL_FLOAT
	}
	gl.glPixelStorei(gl.GL_UNPACK_ALIGNMENT, 1)
	gl.glTexImage3D(gl.GL_TEXTURE_3D, 0, gl.GL_RED, in_size[0], in_size[1], in_size[2], 0, gl.GL_RED, glTypeFromNp[in_data.dtype], ctypes.c_void_p(in_data.ctypes.data))

def attach_output(out_size):
	# Clear output
	gl.glBindTexture(gl.GL_TEXTURE_3D, rendered_texture)
	gl.glTexImage3D(gl.GL_TEXTURE_3D, 0, gl.GL_RED, out_size[0], out_size[1], out_size[2], 0, gl.GL_RED, gl.GL_UNSIGNED_INT, 0)


def main():
	t = time.time()

	parser = argparse.ArgumentParser()
	parser.add_argument('--tex',     help='input tiff file (*.tiff for sequence)',default='')
	parser.add_argument('--in_box',  help='--insize x y z w h d',type=int,nargs=6,default=[0,0,0,0,0,0])
	parser.add_argument('--code',    help='--code "return texture(tex,p).r;"',default='return texture(tex,p).r;')
	parser.add_argument('--size',    help='--size w h d',nargs=3,type=int,default=[0,0,0])
	parser.add_argument('--seam',    help='--seam dd',nargs=1,type=int,default=10)
	parser.add_argument('--compress',help='compression level',type=int,default=2)
	parser.add_argument('out_tiff',  help='output tiff file',type=str)
	args = parser.parse_args()

	seam = args.seam
	if '*' in args.tex:
		import os
		dr = os.path.split(args.tex)[0]+'/'
		print(dr,os.path.isdir(dr))
		seq = tifffile.TiffSequence(args.tex)
		in_data = seq.asarray()
		print(in_data.shape,in_data.dtype)
		print(in_data[0][0][0])
		# in_data = in_data.astype(np.uint32)
		# print(in_data[0][0][0])
	elif os.path.isfile(args.tex):
		in_data = tifffile.imread(args.tex)
	else:
		in_data = np.zeros((1,1,1),dtype=np.uint32)
	if len(in_data.shape)!=3:
		print('Not a 3D grayscale tiff:',in_data.shape)
	# if len(in_data.shape)==4:
	# 	print('Using red channel')


	in_d,in_h,in_w = in_data.shape
	in_size = in_w,in_h,in_d
	bx,by,bz,bw,bh,bd = args.in_box
	bw = in_w-bx if bw==0 or bx+bw>in_w else bw
	bh = in_h-by if bh==0 or by+bh>in_h else bh
	bd = in_d-bz if bd==0 or bz+bd>in_d else bd

	time_loaded = time.time()
	print('Loading input {} took {:.2f} seconds'.format(in_size,time_loaded-t))
	if (bw,bh,bd)!=in_size:
		print('Clipping to [{},{})x[{},{})x[{},{})'.format(bx,bx+bw,by,by+bh,bz,bz+bd))
		in_size = (bw,bh,bd)
		in_w,in_h,in_d = in_size
		in_data = in_data[bz:bz+bd,by:by+bh,bx:bx+bw]

	out_w,out_h,out_d = args.size
	out_w = in_w if out_w<=0 else out_w
	out_h = in_h if out_h<=0 else out_h
	out_d = in_d if out_d<=0 else out_d
	out_size = (out_w,out_h,out_d)

	pixPerZ = in_w*in_h
	zPerBatch = SAFE_TEX_SIZE//pixPerZ-2*seam
	batches = [(i,i+zPerBatch) for i in range(0,in_d,zPerBatch)]

	setup_framebuffer()
	setup_render_program(args.code)
	setup_render_vertexbuffer()
	time_setup = time.time()
	print('Setup took {:.2f} seconds'.format(time_setup-time_loaded))

	time_buffered = time_setup
	warned = False
	out_batches = []
	for z0,z1 in batches:
		z0 = max(0,z0)
		z1 = min(in_d,z1)
		z0s = max(0,z0-seam)
		z1s = min(in_d,z1+seam)

		batch_out_d = out_d*(z1-z0)/in_d
		if not warned and batch_out_d!=int(batch_out_d) and len(batches)>1:
			warned = True
			print('Warning: input/output Z-dimension mismatch while using multiple batches')
		batch_out_d = int(batch_out_d)
		batch_in_size = (in_w,in_h,z1s-z0s)
		batch_out_size = (out_w,out_h,batch_out_d)

		attach_input(in_data[z0s:z1s],batch_in_size)
		attach_output(batch_out_size)
		time_transfer = time.time()
		print('Texture transfer {} took {:.2f} seconds'.format((z0s,z0,z1,z1s),time_transfer-time_buffered))

		render_to_texture(batch_in_size,batch_out_size,(z0-z0s,z1-z0s))
		time_rendered = time.time()
		print('Rendering took {:.2f} seconds'.format(time_rendered-time_transfer))

		buf = (gl.GLubyte*(out_w*out_h*batch_out_d))()
		gl.glBindTexture(gl.GL_TEXTURE_3D,rendered_texture)
		gl.glPixelStorei(gl.GL_PACK_ALIGNMENT, 1)
		gl.glGetTexImage(gl.GL_TEXTURE_3D,0,gl.GL_RED,gl.GL_UNSIGNED_BYTE,buf)
		out_batches.append(np.frombuffer(buf,dtype=np.uint8).reshape((batch_out_d,out_h,out_w)))

		time_buffered = time.time()
		print('Buffering took {:.2f} seconds'.format(time_buffered-time_rendered))
	
	out_data = np.concatenate(out_batches)
	time_cat = time.time()
	print('Concatenating took {:.2f} seconds'.format(time_cat-time_buffered))

	# export
	t = time.time()
	tifffile.imwrite(args.out_tiff,out_data,bigtiff=True,compress=args.compress,photometric='minisblack',metadata={'title':str(out_data.shape),'code':str(args.code)})
	time_exported = time.time()
	print('Exporting took {:.2f} seconds; size {:.2f} MB'.format(time_exported-t,os.path.getsize(args.out_tiff)/1024**2))

if __name__ == '__main__':
	main()