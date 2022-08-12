#requres parties 0.0.19

from parties import multiple_simulations
from parties import post_process

import numpy as np
import pandas as pd
import os


def out_func(s):
        #Loop over all simulations
        for item in s.sim_list:
                p=post_process(postfix=item['postfix'])
                #Save snapshot and delete the last Data_idx.h5 file
                data_idx=p.check_changes('Data')
                if data_idx != 0:
                    p.plot_XY_vel_mag_contour('vel_',data_idx)
                    os.system('rm ' + item['postfix'] + '/Data_' + str(data_idx) + '.h5')

#Stop simulation if particle pass the threshold
#def stop_fnc(s):
#    for item in s.sim_list:
#        if item['status'] == 'Done':continue
#        p=post_process(postfix=item['postfix'])
#        idx = p.check_changes('Particle')
#        if idx == 0: continue
#        pos_y=p.get('Particle',idx,['mobile','X'])[0][1]
#        y_max=p.get('Data',0,['grid','yc'])[-1]*0.1
#        if pos_y<y_max:
#            item['simulation'].stop()
#            item['status'] = 'Done'
#            s.work_proc +=s.n_pps


#Setup general the variables
D_range = np.linspace(1,1.2,num=3)
out_t_range = np.linspace(0.1,0.15,num=3)/10
default_t_range = np.linspace(0.1,0.15,num=3)/100
t_max_range = np.linspace(0.1,0.15,num=3)
x_max_range= 5.0*D_range
z_max_range= 5.0*D_range
y_max_range= 5.0*D_range


#Setup parties.inp variables
vars = {'xmax = ':x_max_range,
        'ymax = ':y_max_range,
        'zmax = ':z_max_range,
        'time_max = ':t_max_range,
	'output_time_interval = ': out_t_range,
	'default_dt = ':default_t_range}
df = pd.DataFrame(data=vars)

#Setup various p_mobile.inp 
p_fixed_content=[]
for i in range(len(D_range)):
    r=f"{D_range[i]/2:.3e}"
    x=f"{x_max_range[i]*0.5:.3e}"
    z=f"{z_max_range[i]*0.5:.3e}"
    y=f"{y_max_range[i]*0.5:.3e}"
    p_fixed_content.append('1\n' + x + ' ' + y + ' ' + z + ' ' + r)


#Setup and run simulations
ms = multiple_simulations(n_avail_proc=4,n_pps=4, vars=df,run_command='mpirun', p_fixed=p_fixed_content)
ms.run_parallel(out_func=out_func)
