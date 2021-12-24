import numpy as np
import pandas as pd
import os
import subprocess
from subprocess import PIPE
import h5py
import sys
from collections import OrderedDict
from itertools import product
import fileinput
import time
import glob

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from mpl_toolkits.axes_grid1 import make_axes_locatable

class simulation:
    def __init__(self,
                 proc_num = 2,
                 PARTIESINP = 'parties.inp',
                 log_name = 'tmp.log',
                 run_command = 'mpirun',
                 work_dir = '.'
                 ):
        #Default variables
        self.proc_num = proc_num
        self.PARTIESINP = PARTIESINP
        self.log_name = log_name
        self.run_command = run_command
        self.work_dir=work_dir

        self.tmp_log_file = None
        self.parties = None #process variable - to start/stop simulation
        self.status = False
        self.main_dir = os.getcwd() + '/'
        

    def run(self):
        self.log_name = self.main_dir + self.log_name
        with open(self.log_name,'w') as log_file:
            if self.proc_num > 1:
                self.parties = subprocess.Popen([self.run_command,'-np', str(self.proc_num), './parties'],stdout=log_file,cwd=self.work_dir)
            if self.proc_num == 1:
                self.parties = subprocess.Popen(['./parties'],stdout=log_file,cwd=self.work_dir)
        self.status = True

    def stop(self):
        stop_inp=self.main_dir+'/'+self.work_dir+'/stop.inp'
        f=open(stop_inp,'w')
        f.write('1')
        while (self.check_status != 0):
            time.sleep(0.1)
        self.status = False

    def check_status(self):
        return self.parties.poll()

    #Add main and work directory to change files already in work dir
    def change_line(self, file_name, line_keyword, value):
        for line in fileinput.input([file_name], inplace=True):
            if line.strip().startswith(line_keyword):
                new_line = line_keyword + str(value) + '\n'
                line = new_line
            sys.stdout.write(line)
    
    #Add main and work directory to change files already in work dir
    def change_parties_inp(self,cols,row):
        for comp in range(len(cols)):
            line_keyword = cols[comp]
            value = row[cols[comp]]
            self.change_line(self.PARTIESINP,line_keyword,value)

    #Overwrites the file with 'content'
    #Opens the file with given file name
    #in work directory
    #Add main and work directory to change files already in work dir
    def change_file(self,content,file_name):
        file = self.main_dir + file_name
        f=open(file,'w')
        f.write(content)
        f.close()

class post_process:
    def __init__(self,
                 postfix='',
                 fig_folder='/fig'):
        
        self.figures_folders = fig_folder
        self.postfix = postfix
        self.last_index=0
        self.main_dir = os.getcwd() + '/'
    
    def get(self, name, idx, flags, **kwargs):
        
        def open_h5_file(filename):
            waiting_time=0
            while (waiting_time < 10):
                try:
                    f = h5py.File(filename,'r')
                    break
                except:
                    time.sleep(1)
                    waiting_time +=1
            if waiting_time == 10:
                print('ERROR: File was not been able to open for 10s !!!')
                return -1
            return f

        pstfx=''
        if self.postfix != '': pstfx=self.postfix + '/'
        filename= self.main_dir+pstfx+name+'_'+str(idx)+'.h5'
        f=open_h5_file(filename)

        try:
            for i,flag in enumerate(flags):
                if i == 0: 
                    res = f.get(flag)
                else: res = res.get(flag)
            return res
        except:
            print('Unable to find the variable')
            return -1.0
        
    #This function checks is there a new output Data file
    #if yes - it returns the index of the last written file
    #if no - it returns zero
    def check_changes(self,files_name):

        #Sorting Data files and return array of sorted indexes
        def sort_data_files(f_name):
            files = glob.glob(f_name+'_*')
            indexes = []
            for file in files:
                idx = file.split(f_name+'_')
                idx = idx[1].split('.h5')
                idx = int(idx[0])
                indexes.append(idx)
            indexes.sort()     
            return indexes       

        files_name = self.postfix+'/'+files_name
        files = glob.glob(files_name+'_*')
        if len(files) <= 1: return 0

        indexes = sort_data_files(files_name)
        if self.last_index == indexes[-1]:
            return 0
        else:
            return indexes[-1]





    #revisit this function to account for staggered grid
    def plot_XY_vel_mag_contour(self,
                                out_name,
                                file_idx,
                                plane_position='mid',
                                **kwargs):

        prev_kwargs = kwargs
        file_name='Data'
        #if self.postfix != '': file_name = '/'+self.postfix +'/Data'
        if self.postfix != '': out_name=self.postfix+'/'+out_name

        #Position of the slicing plane
        try:
            if plane_position == 'mid': p_pos=int(self.get(file_name,file_idx,['grid','NZ'])[0]/2)
            else: p_pos=plane_position
        except:
            print(file_name)
            print(file_idx)
            print(self.get(file_name,file_idx,['grid','NZ']))
        
        u = self.get(file_name,file_idx,['u'])[p_pos]
        v = self.get(file_name,file_idx,['v'])[p_pos]
        w = self.get(file_name,file_idx,['w'])[p_pos]

        #Create a x,y data matrix for plot
        NX = self.get(file_name,file_idx,['grid','NX'])[0]
        nx=complex(0,NX)
        NY = self.get(file_name,file_idx,['grid','NY'])[0]
        ny = complex(0,NY)
        x_min = self.get(file_name,file_idx,['grid','xu'])[0]
        x_max = self.get(file_name,file_idx,['grid','xu'])[NX-1]
        y_min = self.get(file_name,file_idx,['grid','yv'])[0]
        y_max = self.get(file_name,file_idx,['grid','yv'])[NY-1]

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
        plt.close('all')

    def find_sort_files(self,first_part,second_part):
        files = glob.glob(first_part+'*')
        indexes = []
        for file in files:
            idx = file.split(first_part)
            idx = idx[1].split(second_part)
            idx = int(idx[0])
            indexes.append(idx)
        indexes.sort()
        return indexes



class multiple_simulations:
    def __init__(self,
                 n_avail_proc = 4,
                 n_pps=None,
                 vars = None,
                 run_command='mpirun',
                 p_fixed = None,
                 p_mobile=None,
                 ):
        
        self.n_avail_proc = n_avail_proc
        self.n_pps=n_pps
        self.vars = vars #iteratable variables
        self.p_fixed=p_fixed
        self.p_mobile=p_mobile
        
        self.sim_list=[]
        self.run_command = run_command
        self.postfix=""
        self.print_status = False
        self.work_proc=0
    
    
    def run_parallel(self,out_func=None,stop_func=None):
        
        def update_simulation_status():
            res = 0
            for item in self.sim_list:
                if item['status'] == 'Running' and item['simulation'].check_status() != None:
                    if item['simulation'].check_status() == 0:
                        item['status'] = 'Done'
                    if item['simulation'].check_status() == 1:
                        item['status'] = 'Crashed'
                    res += item['n_pps']
            return res

        def print_sim_table():

            print_cmd = '**************Simulation table**************\n'
            print_cmd += 'idx\tstatus\t\tpostfix\n'
            for item in self.sim_list:
                print_cmd += str(item['idx'])+'\t'+str(item['status'])+'\t\t'+str(item['postfix'])+'\n'
            #Variables to make updated table
            dummy = (50 * ' ' + '\n')*(len(self.sim_list)+2)
            end_var = '\033[F'*(len(self.sim_list)+2)
            
            if self.print_status == True: print('',end=end_var)
            print(dummy,end=end_var)
            print(print_cmd,end='')
            self.print_status = True


        if self.vars is None:
            print('No variables to iterate')
            return 0

        cols = list(self.vars.columns)

        #Create a list of simulations
        for idx, rows in self.vars.iterrows():
            self.set_postfix(cols,rows)
            s = simulation(proc_num=int(self.n_pps[idx]),
                           run_command=self.run_command,
                           log_name=self.postfix+'/tmp.log',
                           work_dir='/'+self.postfix
                           )
            sim = {'simulation':s,
                   'postfix':self.postfix,
                   'status':'Pending',
                   'idx':idx,
                   'n_pps':int(self.n_pps[idx])}
            self.sim_list.append(sim)

            #Prepare folders for each simulation
            s.change_parties_inp(cols,rows)
            if self.p_fixed != None: s.change_file(self.p_fixed[idx],'p_fixed.inp')
            if self.p_mobile != None: s.change_file(self.p_mobile[idx],'p_mobile.inp')
            os.system('mkdir ' + self.postfix)
            os.system('cp *.inp parties ' + self.postfix + '/')

        #Run simulations parallely
        self.work_proc = self.n_avail_proc
        while True:
            time.sleep(0.1)
            #################### Simulation Update #####################
            #This piece of code constantly goes through all simulations#
            #checks it's status and runs new simulations if there are  #
            #enough processers                                          #
            ########################## Start ###########################
            for item in self.sim_list:
                if item['status'] == 'Done' or item['status'] == 'Crashed':  continue
                if item['status'] == 'Running':
                    self.work_proc += update_simulation_status()
                    continue
                if self.work_proc < item['n_pps']: continue
                #Run simulation
                item['simulation'].run()
                item['status'] = 'Running'
                self.work_proc -= item['n_pps']
            ########################## Stop ############################
            
            #Output function
            if out_func is not None: out_func(self)

            #Stop function
            if stop_func is not None: stop_func(self)

            #Update the simulation table in the terminal
            print_sim_table()
            
            #Out of while loop if all simulations are completed
            stop_flag = True
            for item in self.sim_list:
                if item['status'] == 'Running' or item['status'] == 'Pending': stop_flag = False
            if stop_flag == True: break

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
            #if type(value) == np.float64: value = round(value,3)
            tmp = line_keyword.replace(" ","")
            tmp = tmp.replace("=","")
            str_value=f"{value:.3e}"
            self.postfix += tmp + "_" + str_value
            if comp < (len(cols)-1): self.postfix += "_"