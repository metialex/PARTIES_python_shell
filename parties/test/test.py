import os.path

#_____________________________Importing the package_____________________________#
try:
    from parties import simulation
    from parties import multiple_simulations
    from parties import post_process
    import time
    print('Package loaded successfully')

except:
    print('Error: Unable to import parties library')
    exit()

if os.path.isfile('parties') is False: 
    print('Error: Copy executable "parties" into this directory')
    exit()

#_____________________________Test simulation class_____________________________#

print('Basic test of simulation class...')
try:
    s = simulation(proc_num=2,run_command='mpirun')
    s.run()
    #time.sleep(2)
    s.stop()
    print('Succsesful!')
except:
    print('Something went wrong')
    exit()

#_____________________________Test multiple simulation class_____________________________#

print('Basic test of multiple simulation class...')
Re_range = ['1.0', '10.0']
iterative_variables = {'Re = ':Re_range,
                       'rho_s = ': Re_range}

ms = multiple_simulations(n_avail_proc=2,n_pps=1)
ms.vars = ms.cartesian_product(iterative_variables)
ms.run_parallel()
#except:
#    print('Something went wrong')
#    exit()


#_____________________________Test post_process class_____________________________#
print('Basic test of post_process class...')
try:
    p = post_process()
    #pos = p.get('Particle', 2, ['fixed','X'])[0]
    #p.plot_XY_vel_mag_contour('test',3)
    

except:
    print('Something went wrong')
    exit()

os.system('rm *.h5 *.dat *.png *.log') #comment in order to see the simulation output
