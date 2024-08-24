import os
import sys
import networkx as nx
import matplotlib.pyplot as plt



def get_attrs(l):
    attrs={}
    ll = l.split(',')
    for seg in ll:
        ret = seg.split(':')
        if(len(ret)==2):
            if ret[0]=='dis':
                attrs[ret[0]]=float(ret[1])/100
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
    if 'id' in attrs:
        if attrs['id']==0:
            attrs['dis']=50
            attrs['time']=1
    if 'orig' in attrs:
        attrs['dis']=50
        attrs['time']=1
        attrs['src']=-1
    return attrs

def get_attrs_realcrash(l):
    attrs={}
    ll = l.split(',')
    for seg in ll:
        ret = seg.split(':')
        if(len(ret)==2):
            if ret[0]=='dis':
                attrs[ret[0]]=float(ret[1])/100
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
    return attrs

        
def back_trace(poc, queued_testcase):
    # print('back_trace:', poc)
    cur_src = poc['src']
    trace = []
    lineage_max_dis=0
    while(True):
        for node in queued_testcase:
            if(node['id'] == cur_src):
                if(node['id']==0 or 'orig' in node):
                    # node['dis']=(int(lineage_max_dis)//10 + 1)*10
                    node['dis']=MAX_SEED_DIS #150
                    trace.insert(0, node)
                    return trace
                if node['dis'] > lineage_max_dis:
                    lineage_max_dis = node['dis']
                trace.insert(0, node)
                # print('bt: ', trace)
                cur_src = node['src']
                break
    return trace
                

def draw_lineage_for_real_crash(real_crash_file, queue_dir, distance_log_file, pic_name, record_cnt=1, COUSIN_CNT=100):

    # readin all testcase
    all_testcase_list = []
    fr = open(distance_log_file)
    for tci in fr.readlines():
        if(tci.startswith('type:1')==False): # log of every testcase
            continue
        attrs = get_attrs(tci)
        if 'src' not in attrs:
            continue
        all_testcase_list.append(attrs)
    fr.close()
    # print('tc size:', len(all_testcase_list))
    # print(all_testcase_list[0:10])

    # read in all testcase in /queue
    queued_testcase = []
    for queue_i in os.listdir(queue_dir):
        if(queue_i.startswith('id:')):
            queued_testcase.append( get_attrs(queue_i) )
    # print(queued_testcase[-10:-1])

    plt.figure()
    plt.rcParams.update({'font.size': 17})
    ax = plt.gca()
    ax.ticklabel_format(style='sci', axis='x', scilimits=(0,0)) 
    # plt.xscale('log')
    # readin all real_crash id
    fr = open(real_crash_file)
    for l in fr.readlines():
        if(l.startswith('id:')):
            attrs = get_attrs_realcrash(l.replace('\n', ''))
            MAXN_TIME = attrs['time']
            bt = back_trace(attrs, queued_testcase)
            print('poc:', l , 'lineage:', len(bt),  bt, 'MAX_TIME:', MAXN_TIME, 'attrs:', attrs)
            for idx in range(0,len(bt)-1):
                cousin_cnt = COUSIN_CNT
                for tc in all_testcase_list:
                    if tc['time']>MAXN_TIME*1.1:
                        continue
                    # if(tc['id']==0):
                    #     continue
                    if( bt[idx]['id'] == tc['src'] and tc['dis']>0):
                        plt.plot( [ bt[idx]['time'], tc['time']] , [bt[idx]['dis'], tc['dis']], marker='.', linestyle='--', color='grey')
                        cousin_cnt-=1
                    if cousin_cnt==0:
                        break
                # print(bt[idx], bt[idx+1])
                print('bt_idx:', idx, 'cousin:', COUSIN_CNT-cousin_cnt)
                plt.plot( [bt[idx]['time'], bt[idx+1]['time']] , [bt[idx]['dis'], bt[idx+1]['dis']], marker='x', linestyle='--', color='red')
            record_cnt-=1
            if(record_cnt==0):
                break
    fr.close()
    # plt.title("Seed Evolution in the Lineage of POC")
    # plt.xlabel("Time (ms)")
    # plt.ylabel("Distance of Seed")
    plt.savefig(pic_name, bbox_inches='tight') 
    plt.savefig(pic_name+'.eps', bbox_inches='tight') 
    plt.cla()





MAX_SEED_DIS=50
queued_testcase = []
i=9
cousin_cnt = 10000
real_crash_cnt = 1
fuzz_out_dir = '/mnt/data/wenake/aflgo-formal-experiments/cve-2016-4490-cxxfilt/cve-2016-4490-cxxfilt-arithmetic-appr/obj-dist/out/out_'+str(i)+'/'
real_crash_files = fuzz_out_dir + "crashes/real_crash.txt"
queue_dir = fuzz_out_dir + 'queue/'
distance_log_file = fuzz_out_dir + "distance_log"
try:
    draw_lineage_for_real_crash(real_crash_files, queue_dir, distance_log_file, './POC-lineage-analysis/POC-lineage-analysis-with-dis-cve-2016-4490-'+str(i)+'-new.png', real_crash_cnt, cousin_cnt)
except Exception as e:
    print("Exception:", e)

