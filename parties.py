import pandas as pd
import os
import pathlib
import subprocess
from subprocess import PIPE
import h5py
from sshtunnel import SSHTunnelForwarder
import sys
import socket
from pexpect import pxssh
import time
from collections import OrderedDict
from itertools import product
from icecream import ic
import fileinput
ic.enable()

class simulation:
    def __init__(self,**kwargs):
        #Default variables
        self.proc_num = 2
        self.tmp_log_file_name = 'tmp.log'
        self.tmp_log_file = None
        self.PARTIESINP = "parties.inp"
        self.sim_folder = None
        self.ssh_login = None
        self.exec_folder = None
        self.parties = None
        self.status = False
        self.vars = None
        self.stop_flag = False
        #Read keyword arguments
        if 'proc_num' in kwargs.keys(): self.sim_folder = kwargs.get('proc_num')
        if 'sim_folder' in kwargs.keys(): self.sim_folder = kwargs.get('sim_folder')
        if 'ssh_login' in kwargs.keys(): self.ssh_login = kwargs.get('ssh_login')

    def run(self):
        self.tmp_log_file = open(self.tmp_log_file_name,'a')
        if self.proc_num > 1:
            self.parties = subprocess.Popen(['mpirun_o','-np', str(self.proc_num), './parties'],stdout=self.tmp_log_file)
            ic(self.parties.poll())
        if self.proc_num == 1:
            self.parties = subprocess.Popen(['./parties'],stdout=self.tmp_log_file)
        self.status = True
    
    def stop(self):
        self.parties.kill()
        self.status = False
        self.stop_flag = False
    
    def set_vars(self,vars):
        od = OrderedDict(sorted(vars.items()))
        cart = list(product(*od.values()))
        self.vars = pd.DataFrame(cart,columns=od.keys())
    
    def change_line(self, file_name, line_keyword, value):
        for line in fileinput.input([file_name], inplace=True):
            if line.strip().startswith(line_keyword):
                new_line = line_keyword + str(value) + '\n'
                line = new_line
            sys.stdout.write(line)


    def gitclone(self):
        print('not implemented yet')
    def make(self):
        os.system('make clean')
        os.system('make')
        print('make')
    def go_to_workfolder():
        print('not implemented yet')
    def ssh_connect(self):
        print('not implemented yet')
        try:
            conn = pxssh.pxssh()
            conn.login('134.169.62.45','metelkin','lwi')
            conn.sendline('metelkin && ls')
            conn.prompt()
            print(conn.before)
        except:
            print('smth went wrong')

class post_process:
    def __init__(self, **kwargs):
        self.text_out_files = None
        self.figures_folders = None
    
    def get(self, name, idx, flags, **kwargs):
        filename= name +'_'+str(idx)+'.h5'
        try:
            f = h5py.File(filename,'r')
            for i,flag in enumerate(flags):
                if i is 0: res = f.get(flag)
                else: res = res.get(flag)
            if 'component' in kwargs.keys(): res = res[0][kwargs.get('component')]
            elif len(res) < 2: res = res[0][0]
            return res
        except:
            print('Unable to find variable')

    def append_to_file(self, filename, data):
        print('asd')


iterative_variables = {'Re = ':range(2,10,2),
                       'default_dt = ':[10, 20],
                       'eps_inf = ': ['0.1',0.2]}


s = simulation()
s.set_vars(iterative_variables)

cols = list(s.vars.columns)
for index, row in s.vars.iterrows():
    #Change all necessary lines in parties.inp
    for comp in range(len(cols)):
        line_keyword = cols[comp]
        value = row[cols[comp]]
        s.change_line(s.PARTIESINP,line_keyword,value)
    ic('change' + str(index))
    time.sleep(10)
    while True:
        break
        time.sleep(2)
        #Start simulation
        if not s.status: s.run()
        if s.stop_flag: s.stop()

    

#ic(s.vars)