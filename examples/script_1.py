import parties
from parties import multiple_simulations
from parties import post_process

import numpy as np
import pandas as pd



def out_func(s):
        #Create output variabl
        output = {'Re':s.vars['Re = ']}
        df=pd.DataFrame(data=output)

        #Loop over all simulations
        forces=[]
        for item in s.sim_list:
                p=post_process(postfix=item['postfix'])
                force=0.0
                if item['status'] == 'Done':
                        force = p.get('Particle',1,['fixed','F_IBM'])[0][0]
                forces.append(force)
        #print(forces)
        df['Force'] = forces
        df.to_csv('force_output_file.csv')


#Setup the variables
Re_range = np.linspace(5,100,num=3)
max_t_range = np.linspace(0.1,0.2,num=3)
#
vars = {'Re = ':Re_range,
        'time_max = ':max_t_range,
        'output_time_interval = ':max_t_range}
#
df = pd.DataFrame(data=vars)
#
ms = multiple_simulations(n_avail_proc=4,n_pps=4, vars=df,run_command='mpirun')
ms.run_parallel(out_func=out_func)

