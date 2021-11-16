from simulation import simulation
from icecream import ic
import os
import h5py
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from mpl_toolkits.axes_grid1 import make_axes_locatable


class post_process:
    def __init__(self, **kwargs):
        self.text_out_files = None
        self.figures_folders = None
        self.postfix = ""
    
    def get(self, name, idx, flags, **kwargs):
        filename= name +'_'+str(idx)+'.h5'
        try:
            f = h5py.File(filename,'r')
        except:
            print('Unable to open the file')

        try:
            for i,flag in enumerate(flags):
                if i is 0: 
                    res = f.get(flag)
                else: res = res.get(flag)
            return res
        except:
            print('Unable to find the variable')
            return -1.0
        

    def set_postfix(self,cols,row):
        p.postfix=""
        for comp in range(len(cols)):
            line_keyword = cols[comp]
            value = row[cols[comp]]
            if type(value) is np.float64: value = round(value,3)
            tmp = line_keyword.replace(" ","")
            tmp = tmp.replace("=","")
            self.postfix += tmp + "_" + str(value)
            if comp < (len(cols)-1): self.postfix += "_"

    #revisit this function to account for staggered grid
    def plot_XY_vel_mag_contour(self,
                                out_name,
                                file_idx,
                                plane_position='mid',
                                **kwargs):

        prev_kwargs = kwargs

        #Position of the slicing plane
        if plane_position is 'mid': p_pos=int(self.get('Data',file_idx,['grid','NZ'])[0]/2)
        else: p_pos=plane_position

        u = self.get('Data',file_idx,['u'])[p_pos]
        v = self.get('Data',file_idx,['v'])[p_pos]
        w = self.get('Data',file_idx,['w'])[p_pos]

        #Create a x,y data matrix for plot
        NX = self.get('Data',file_idx,['grid','NX'])[0]
        nx=complex(0,NX)
        NY = self.get('Data',file_idx,['grid','NY'])[0]
        ny = complex(0,NY)
        x_min = self.get('Data',file_idx,['grid','xu'])[0]
        x_max = self.get('Data',file_idx,['grid','xu'])[NX-1]
        y_min = self.get('Data',file_idx,['grid','yv'])[0]
        y_max = self.get('Data',file_idx,['grid','yv'])[NY-1]

        Y, X = np.mgrid[y_min:y_max:ny, x_min:x_max:nx]
        speed = np.sqrt(u**2 + v**2 + w**2)

        #Figure parameters
        fig = plt.figure(figsize=(NX/20+(0.05*NX/20), NY/20))
        gs = gridspec.GridSpec(nrows=1, ncols=1)
        plt.pcolormesh(X,Y, speed,shading="nearest", alpha = 1.0,**prev_kwargs)
        
        #Colorbar parameters
        ax = plt.gca()
        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size="5%", pad=0.05)
        plt.colorbar(cax=cax)
        
        #Savefigure
        plt.savefig(out_name + str(file_idx) + '.png')


    def append_to_file(self, filename, data):
        print('asd')