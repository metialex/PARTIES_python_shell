import numpy as np
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
import simulation
ic.enable()

class multiple_simulations:
    def __init__(self,
                 n_avail_proc = 20,
                 n_pps = 10
                 ):
        self.sim_list=[]
        self.n_avail_proc = n_avail_proc
        self.n_pps = n_pps #number of processors per simulation
    def run_serial(self):
        #create pandas table of simulations
        #while loop to run in sequence
        return 0
    def run_parallel(self):
        #create pandas table of simulations
        # sim_index | sim_name | sim_runs | status | list of parameters
        #While loop which check the status of simulations
        return 0
