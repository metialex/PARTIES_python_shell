Re_range = np.logspace(-1,2,num=8)
Dp_range = np.logspace(0,-1,num=2)

iterative_variables = {'Re = ':Re_range,
                       'Dp_inf = ':Dp_range}


#print(iterative_variables)

s = simulation(proc_num=1)
p = post_process()

def calc_perm_term(eps,Re,Dp):
    perm = ((Dp**2)*(eps**3))/(180*(1.0-eps)**2)
    return (Re*perm)/eps

if 1 is 1:
    iterative_variables = {'Re = ':Re_range,
                       'Dp_inf = ':Dp_range}

    s.set_vars(iterative_variables)

    s.vars['CFL_dt'] = s.vars['Re = '] * 5e-4
    s.vars['por_dt'] = (calc_perm_term(0.5, s.vars['Re = '], s.vars['Dp_inf = ']))/(2.0/15.0)
    s.vars['default_dt = '] = s.vars[['CFL_dt', 'por_dt']].min(axis=1)
    s.vars = s.vars.drop(['CFL_dt'],axis=1)
    s.vars['time_max = '] = s.vars['default_dt = ']*300.0
    s.vars['output_time_interval = '] = s.vars['default_dt = ']*100.0
    s.vars['max_dt = '] = s.vars['default_dt = ']*100.0
    s.vars['permeability = '] = ((s.vars['Dp_inf = ']**2)*(0.5**3))/(180*(1.0-0.5)**2)

    print(s.vars)

    cols = list(s.vars.columns)

    result = pd.DataFrame(columns=['Re','Dp','sim_time'])

    for index,row in s.vars.iterrows():
        p.set_postfix(cols,row)
        s.change_parties_inp(cols,row) #change parties.inp before a new simulation
        s.run()
        ic(p.postfix)
        while True:
            time.sleep(2)
            if s.parties.poll() is not None:
                sim_time_1 = p.get('Resume', 2, ['timer'],component=2)
                sim_time_2 = p.get('Resume', 3, ['timer'],component=2)
                sim_time = (sim_time_2-sim_time_1)/row['output_time_interval = ']

                sim_time_1 = p.get('Resume', 2, ['timer'],component=0)
                sim_time_2 = p.get('Resume', 3, ['timer'],component=0)
                sim_time_total = (sim_time_2-sim_time_1)/row['output_time_interval = ']

                dt = p.get('Resume', 3,['dt'], component=0)

                result = result.append({'Re':row['Re = '],
                                        'Dp':row['Dp_inf = '],
                                        'sim_time':sim_time,
                                        'sim_time_total':sim_time_total,
                                        'dt':dt},
                                        ignore_index=True)
                print('simulation time = ' + str(sim_time))
                result.to_csv('simulation_time.csv')
                break
        ic("stop")
        s.stop()
        


#IBM
if 1 is 0:
    iterative_variables = {'Re = ':Re_range}

    s.set_vars(iterative_variables)

    s.vars['CFL_dt'] = 0.005
    s.vars['default_dt = '] = s.vars['CFL_dt']
    s.vars = s.vars.drop(['CFL_dt'],axis=1)
    s.vars['time_max = '] = s.vars['default_dt = ']*450.0
    s.vars['output_time_interval = '] = s.vars['default_dt = ']*150.0
    s.vars['max_dt = '] = s.vars['default_dt = ']*100.0

    cols = list(s.vars.columns)

    result = pd.DataFrame(columns=['Re','sim_time'])

    for index,row in s.vars.iterrows():
        p.set_postfix(cols,row)
        s.change_parties_inp(cols,row) 
        s.run()
        ic(p.postfix)
        while True:
            time.sleep(2)
            if s.parties.poll() is not None:
                sim_time_1 = p.get('Resume', 2, ['timer'],component=2)
                sim_time_2 = p.get('Resume', 3, ['timer'],component=2)
                sim_time = (sim_time_2-sim_time_1)/row['output_time_interval = ']

                sim_time_1 = p.get('Resume', 2, ['timer'],component=0)
                sim_time_2 = p.get('Resume', 3, ['timer'],component=0)
                sim_time_total = (sim_time_2-sim_time_1)/row['output_time_interval = ']

                dt = p.get('Resume', 3,['dt'], component=0)

                result = result.append({'Re':row['Re = '],
                                        'sim_time':sim_time,
                                        'sim_time_total':sim_time_total,
                                        'dt':dt},
                                        ignore_index=True)
                print('simulation time = ' + str(sim_time))
                result.to_csv('simulation_time_IBM.csv')
                break
        ic("stop")
        s.stop()
        


#ic(s.vars)