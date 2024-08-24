import os
import sys
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import ScalarFormatter



def draw_scatter_decrease_by_time(lst_time, lst, pic_name, real_crash_time_list, MAX_RATIO=1):
    plt.figure()
    plt.scatter([lst_time[idx] for idx in range(0, len(lst_time), CONTROL_SAMPLE)], [lst[idx] if lst[idx] <=1 else 1.01 for idx in range(0, len(lst), CONTROL_SAMPLE)],s=1)

    plt.ylim(-1.1,1.1)
    ax = plt.gca()
    # ax.xaxis.set_major_formatter(ScalarFormatter(useMathText=False))
    ax.ticklabel_format(style='sci', axis='x', scilimits=(0,0)) # use scilimits on x and y labels
    # ax.axes.yaxis.set_ticklabels([]) # disable y tick labels 
    # plt.yscale('log')
    plt.ylabel('Distance Decrease')


    plt.savefig(pic_name, bbox_inches='tight') 
    plt.cla()
    plt.close()

def draw_cactusplot_decrease(lst, pic_name):
    plt.figure()
    lst.sort()
    plt.scatter([i for i in range(len(lst))], lst, s=1)
    

    plt.ylim(-1.1,1.1)
    ax = plt.gca()
    # ax.xaxis.set_major_formatter(ScalarFormatter(useMathText=False))
    ax.ticklabel_format(style='sci', axis='x', scilimits=(0,0)) 
    # ax.axes.yaxis.set_ticklabels([]) 
    plt.ylabel('Distance Decrease')


    plt.savefig(pic_name, bbox_inches='tight')
    plt.cla()
    plt.close()




def statistics_index(lst, banner):
    NUM_SIG=0
    NUM_TRIVAL=0
    NUM_POS=0
    for i in lst:
        if i < -0.5:
            NUM_SIG+=1
        elif i < 0:
            NUM_TRIVAL+=1
        else:
            NUM_POS+=1
    lst_np = np.array(lst)
    print(banner)
    print("Distance Decrease:\n seed number: %d \n min = %.2f, mean = %.2f, median = %.2f, max = %.2f \n Significat = %.2f Trival = %.2f Positive = %.2f"
                % ( len(lst_np), min(lst_np), lst_np.mean(), np.median(lst_np), lst_np.max(), NUM_SIG/len(lst), NUM_TRIVAL/len(lst), NUM_POS/len(lst)))

def get_attrs(l, s='log'):
    if 'harmonic' in queue_dir:
        TIME_RATIO=1
    else:
        TIME_RATIO=100
    attrs={}
    ll = l.replace('\n', '').split(',')
    for seg in ll:
        ret = seg.split(':')
        if(len(ret)==2):
            if ret[0]=='dis':
                attrs[ret[0]]=float(ret[1])/TIME_RATIO
            elif ret[0]=='maxdis':
                attrs[ret[0]]=float(ret[1])/TIME_RATIO
            elif ret[0]=='src':
                if ret[1].isdigit():
                    attrs[ret[0]]=int(ret[1])
                else:
                    attrs[ret[0]]=int(ret[1].split("+")[0])
            elif ret[1].isdigit():
                attrs[ret[0]]=int(ret[1])
            else:
                attrs[ret[0]]=ret[1]
        elif(len(ret)==1):
            if(len(attrs)==1):
                attrs['time']=int(ret[0])
            else:
                if 'other' in attrs:
                    attrs['other']+=ret[0]
                else:
                    attrs['other']=ret[0]
    if s=='crash':
        return attrs
    if 'id' in attrs:
        if attrs['id']==0:
            attrs['dis']=50.0
            attrs['time']=1
            attrs['src']=-1
    if(('orig' in attrs)==True):
        attrs['dis']=50.0
        attrs['time']=1
        attrs['src']=-1
    return attrs


# assess all testcase distance from queued_testcase, sampling rate shall be awared, listed by time
def assess_queued_seed(queue_dir, pic_name):
    # readin several real crash time for MAXN_CREASH_TIME
    MAXN_CREASH_TIME = 0
    real_crash_file = queue_dir + "../crashes/real_crash.txt"
    fr = open(real_crash_file)
    for l in fr.readlines():
        attrs = get_attrs(l, 'crash')
        MAXN_CREASH_TIME=max(MAXN_CREASH_TIME, attrs['time'])
        break
    MAXN_CREASH_TIME=MAXN_CREASH_TIME*1.2
    print("MAXN_CREASH_TIME:", MAXN_CREASH_TIME)
    # MAXN_CREASH_TIME = 0x7f7f7f7f
    fr.close()

    # readin queued_seed
    queued_seed = []
    for queue_i in os.listdir(queue_dir):
        if(queue_i.startswith('id:')):
            attrs = get_attrs(queue_i)
            if attrs['time']>MAXN_CREASH_TIME:
                continue
            queued_seed.append(attrs)

    # readin all testcase
    all_testcase_file = queue_dir + "../distance_log"
    all_testcase_list = []
    fr = open(all_testcase_file)
    for tci in fr.readlines():
        if(tci.startswith('type:1')==False):
            continue
        attrs = get_attrs(tci)
        if 'src' not in attrs:
            continue
        if attrs['time']>MAXN_CREASH_TIME:
            continue
        all_testcase_list.append(attrs)
    fr.close()

    
    print('seed number:', len(queued_seed), 'testcase number:', len(all_testcase_list), 'MAXN_CREASH_TIME', MAXN_CREASH_TIME)

    
    # readin several real crash time before MAXN_CREASH_TIME
    real_crash_time_list = []
    real_crash_file = queue_dir + "../crashes/real_crash.txt"
    fr = open(real_crash_file)
    for l in fr.readlines():
        attrs = get_attrs(l, 'crash')
        if(attrs['time'] > MAXN_CREASH_TIME):
            continue
        real_crash_time_list.append(attrs['time'])
    fr.close()


    decrease_ratio_by_time = []
    decrease_ratio_the_time = []
    decrease_list_by_seed = []
    seed_distance_list = []
    for idx in range(len(queued_seed)):
        seed = queued_seed[idx]
        decrease_avg_of_seed = 0
        decrease_avg_cnt_of_seed = 0
        for tc in all_testcase_list:
            if 'src' not in tc:
                continue
            if tc['time'] > MAXN_CREASH_TIME:
                continue
            if(seed['id'] == tc['src']):
                if seed['dis']==0:
                    continue
                if( tc['dis'] < 0 ):     # wrong calculation of distance
                    continue
                elif( seed['dis'] < 0 ):   # wrong calculation of distance
                    continue 
                elif(seed['dis'] <= tc['dis']):
                    decrease_avg_of_seed += (tc['dis'] / seed['dis'] - 1)
                    decrease_ratio_by_time.append( (tc['dis'] / seed['dis'] - 1) )
                    decrease_ratio_the_time.append( tc['time'] )
                    decrease_avg_cnt_of_seed+=1
                elif(seed['dis'] > tc['dis']):
                    decrease_avg_of_seed += (tc['dis'] / seed['dis'] - 1)
                    decrease_ratio_by_time.append( (tc['dis'] / seed['dis'] - 1) )
                    decrease_ratio_the_time.append( tc['time'] )
                    decrease_avg_cnt_of_seed+=1
        if(decrease_avg_cnt_of_seed==0):
            continue
        seed_distance_list.append(seed['dis'])
        decrease_list_by_seed.append( decrease_avg_of_seed/decrease_avg_cnt_of_seed )
        if abs(decrease_avg_of_seed/decrease_avg_cnt_of_seed) >5 :
            print(seed, decrease_avg_of_seed, decrease_avg_cnt_of_seed)
    
    draw_scatter_decrease_by_time(decrease_ratio_the_time, decrease_ratio_by_time, pic_name+"-scatter-decrease-by-time.png", real_crash_time_list)
    draw_cactusplot_decrease(decrease_ratio_by_time, pic_name+"-decrease-cactusplot-ylim.png")
    statistics_index(decrease_ratio_by_time, target)

    return decrease_list_by_seed




CONTROL_SAMPLE=1
i=7
queue_dir = '/mnt/data/wenake/aflgo-formal-experiments/cve-2016-4490-cxxfilt/cve-2016-4490-cxxfilt-arithmetic-appr/obj-dist/out/out_'+str(i)+'/queue/'
target = 'cve-2016-4490-arithmetic-appr-run-'+str(i)
try:
    print(target)
    all_decrease_list_by_seed = assess_queued_seed(queue_dir, './mutation-assess/' + target)
except Exception as e:
    print("Exception:", e)