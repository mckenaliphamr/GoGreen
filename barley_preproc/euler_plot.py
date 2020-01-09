"""  Copyright 2015-2018 IST Austria
    File contributed by: Teresa Heiss
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

import numpy as np
import matplotlib.pyplot as plt
import sys
import os


def plot_euler_discrete(filename, fmt):
    Output_of_ChunkyEuler  = np.loadtxt(filename,dtype=int)
    data = np.array(Output_of_ChunkyEuler)
    (m,n) = np.shape(data)
    f = plt.figure()
    for i in range(m-1):
        plt.plot((data[i,0], data[i+1,0]), (data[i,1],data[i,1]), 'k-')
    plt.scatter(data[:,0],data[:,1])
    plt.show()
    output_filename = filename + '.plot.' + fmt
    f.savefig(output_filename, bbox_inches='tight')
    print( 'output succesfully written to: {}'.format(output_filename) )

def plot_euler_continuous(filename, fmt, img_dtype=8):

    path, sname = os.path.split(filename)
    sname = os.path.splitext(sname)[0]
    sname = '_'.join(sname.split('_')[:-2])
    output_filename = sname + '.' + fmt

    Output_of_ChunkyEuler  = np.loadtxt(filename,dtype=int)
    data = np.array(Output_of_ChunkyEuler)
    data = np.vstack((data, np.array([2**img_dtype-1, data[-1,-1]])))

    (m,n) = np.shape(data)
    f = plt.figure()
    plt.plot(data[:,0],data[:,1],'r')
    plt.title(sname)
    plt.xlabel('Density')
    plt.ylabel('Euler Characteristic')
    #plt.show()
    f.savefig(output_filename, bbox_inches='tight')

    # f = plt.figure()
    # sgndata = np.sign(data[:,1:])
    # logdata = sgndata*np.log(sgndata*data[:,1:], where=(sgndata!=0))
    # plt.plot(data[:,0],logdata,'r')
    # plt.title(sname)
    # plt.xlabel('Density')
    # plt.ylabel('log(Euler Characteristic)')
    # f.savefig('log_' + output_filename, bbox_inches='tight')
    # print( 'output succesfully written to: {}'.format(output_filename) )

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Plots the Euler characteristic curve for a given .euler file.')
        print('Two options available: dicrete (default, no third argument needed) or continuous (set third input argument to "c").')
        print('Output is written as a pdf file')
        print('usage: python {} <file.euler> for the discrete version (recommended)'.format(sys.argv[0]))
        print('usage: python {} <file.euler> "c" for the continuous version'.format(sys.argv[0]))
        print('Exitting...')
        exit(-1)
    elif len(sys.argv) == 2:
        plot_euler_discrete(sys.argv[1], '.pdf')
    else:
        if sys.argv[3] == "c":
            plot_euler_continuous(sys.argv[1], sys.argv[2])
        elif sys.argv[3] == "d":
            plot_euler_discrete(sys.argv[1], sys.argv[2])
        else:
            print('Error: The third input argument can only be "c" (continuous) or "d" (discrete, default).')
