"""  Copyright 2015-2018 IST Austria
    File contributed by: Teresa Heiss, Hubert Wagner
    This file is part of Chunky Euler.
    Chunky Euler is free software: you can redistribute it and/or modify
    it under the terms of the GNU Lesser General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    Chunky Euler is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Lesser General Public License for more details.
    You should have received a copy of the GNU Lesser General Public License
    along with Chunky Euler.  If not, see <http://www.gnu.org/licenses/>. """

import PIL.Image
import PIL.ImageFilter
import struct
import sys
import tifffile as tf
import numpy as np
import os
from glob import glob

def image_stack_to_raw(src, dst, filename):

    img = tf.imread(src + filename)
    path, sname = os.path.split(filename)
    output_filename = dst + os.path.splitext(sname)[0] + '_-_' + 'x'.join(map(str, img.shape))+ '.raw'
    out = open(output_filename, 'wb')

    out.write(img.astype('uint8').tostring())

    out.close()
    print( 'output succesfully written to: {}'.format(output_filename) )

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Converts a stack of 2D images (.png, .jpeg etc) to raw 3D image that is u8 encoded (unsigned 8-bit-integer).')
        print('The stack can consist of one single 2D image. In this case the output is a 1 x height x width raw 3D image, which is the same as a height x width raw 2D image.')
        print('Output is written with suffix _t_u8_<size>.from_stack.raw')
        print('usage: python {} "<folder>/*.<ext>" "/path/to/destination"'.format(sys.argv[0]))
        print('Exitting...')
        exit(-1)

    image_stack_to_raw(sys.argv[1],sys.argv[2], sys.argv[3])
