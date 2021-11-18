import numpy as np
import pandas as pd
import os
import subprocess
from subprocess import PIPE
import h5py
import sys
from collections import OrderedDict
from itertools import product
from icecream import ic
import fileinput
import time

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from mpl_toolkits.axes_grid1 import make_axes_locatable

ic.enable()

class simulation:
    def __init__(self,
                 proc_num = 2,
                 PARTIESINP = 'parties.inp',
                 BOUNDARYH = 'src/Include/Boundary.h',
                 log_name = 'tmp.log',
                 run_command = 'mpirun',
                 ):
        #Default variables
        self.proc_num = proc_num
        self.PARTIESINP = PARTIESINP
        self.log_name = log_name
        self.run_command = run_command
        self.tmp_log_file = None
        self.parties = None #process variable - to start/stop simulation
        self.status = False
        
    def rm_log(self):
        os.system('rm '+ self.log_name)

    def run(self, folder='.'):
        self.tmp_log_file = open(self.log_name,'a')
        if self.proc_num > 1:
            self.parties = subprocess.Popen([self.run_command,'-np', str(self.proc_num), './parties'],stdout=self.tmp_log_file,cwd=folder)
        if self.proc_num == 1:
            self.parties = subprocess.Popen(['./parties'],stdout=self.tmp_log_file,cwd=folder)
        self.status = True

    def stop(self):
        self.parties.kill()
        self.status = False

    def check_status(self):
        if self.parties.poll() is not 0: return 1
        else: return 0

    def change_line(self, file_name, line_keyword, value):
        for line in fileinput.input([file_name], inplace=True):
            if line.strip().startswith(line_keyword):
                new_line = line_keyword + str(value) + '\n'
                line = new_line
            sys.stdout.write(line)

    def change_parties_inp(self,cols,row):
        for comp in range(len(cols)):
            line_keyword = cols[comp]
            value = row[cols[comp]]
            self.change_line(self.PARTIESINP,line_keyword,value)

    def make(self):
        os.system('make clean')
        os.system('make')


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



class multiple_simulations:
    def __init__(self,
                 n_avail_proc = 20,
                 n_pps = 10,
                 vars = None
                 ):
        self.sim_list=[]
        self.n_avail_proc = n_avail_proc
        self.n_pps = n_pps #number of processors per simulation
        self.vars = vars #iteratable variables
        self.print_status = False
    
    def run_serial(self, stop_condition = False):
        if self.vars is None:
            print('No variables to iterate')
        else:
            cols = list(self.vars.columns)
            for idx, rows in self.vars.iterrows():
                s = simulation(proc_num=self.n_pps, run_command='mpirun_o')
                self.set_postfix(cols,rows)                
                os.system('mkdir ' + self.postfix)
                s.change_parties_inp(cols,rows)
                os.system('cp *.inp parties ' + self.postfix + '/')
                s.run(folder=(self.postfix+'/'))
                while s.check_status() or stop_condition is True:
                    time.sleep(1)
                    print('Running job: ' + self.postfix,end='\r')
                s.stop()
        return 0
    
    def run_parallel(self,):
        
        def update_simulation_status():
            res = 0
            for item in self.sim_list:
                if item['status'] is 'Running' and item['simulation'].check_status() is 0:
                    item['status'] = 'Done'
                    res += self.n_pps
            return res

        def print_sim_table(prev_print_status):

            print_cmd = '**************Simulation table**************\n'
            print_cmd += 'idx\tstatus\t\tpostfix\n'
            for item in self.sim_list:
                print_cmd += str(item['idx'])+'\t'+str(item['status'])+'\t\t'+str(item['postfix'])+'\n'
            #Variables to make updated table
            dummy = (100 * ' ' + '\n')*(len(self.sim_list)+2)
            end_var = '\033[F'*(len(self.sim_list)+2)
            
            if prev_print_status is True: print('',end=end_var)
            print(dummy,end=end_var)
            print(print_cmd,end='')


        if self.vars is None:
            print('No variables to iterate')
            return 0

        cols = list(self.vars.columns)
        work_proc = self.n_avail_proc

        #Create a list of simulations
        for idx, rows in self.vars.iterrows():
            s = simulation(proc_num=self.n_pps, run_command='mpirun_o')
            self.set_postfix(cols,rows)
            sim = {'simulation':s,
                   'postfix':self.postfix,
                   'status':'Pending',
                   'idx':idx}
            self.sim_list.append(sim)

            #Prepare folders for each simulation
            s.change_parties_inp(cols,rows)
            os.system('mkdir ' + self.postfix)
            os.system('cp *.inp parties ' + self.postfix + '/')

        #Run simulations parallely
        while True:
            #################### Simulation Update #####################
            #This piece of code constantly goes through all simulations#
            #checks it's status and runs new simulations if there are  #
            #enogh processers                                          #
            ########################## Start ###########################
            work_proc = self.n_avail_proc
            for item in self.sim_list:
                if item['status'] is 'Done' or 'Running': continue
                if work_proc < self.n_pps:
                    while work_proc < self.n_pps:
                        #Keep updating the status of running simulations
                        work_proc += update_simulation_status()
                        print_sim_table(self.print_status)
                        self.print_status = True
                        time.sleep(1)
                #run this simulation
                item['simulation'].run(folder=(item['postfix']+'/'))
                item['status'] = 'Running'
                work_proc -= self.n_pps
            ########################## Stop ###########################
            time.sleep(1)
        print('Simulations are completed')
        return 0

    def cartesian_product(self,vars):
        od = OrderedDict(sorted(vars.items()))
        cart = list(product(*od.values()))
        return pd.DataFrame(cart,columns=od.keys())

    def set_postfix(self,cols,row):
        self.postfix=""
        for comp in range(len(cols)):
            line_keyword = cols[comp]
            value = row[cols[comp]]
            if type(value) is np.float64: value = round(value,3)
            tmp = line_keyword.replace(" ","")
            tmp = tmp.replace("=","")
            self.postfix += tmp + "_" + str(value)
            if comp < (len(cols)-1): self.postfix += "_"