#!/usr/bin/python
from subprocess import Popen, PIPE
import ntpath
import argparse
import time
import re
import math
import os

###################################
# SETUP ENV
###################################
hMetis = str('/home/kit/stud/ucywg/partitioners/hMETIS/hmetis-2.0pre1/Linux-x86_64/hmetis2.0pre1')
###################################

parser = argparse.ArgumentParser()
parser.add_argument("graph", type=str)
parser.add_argument("k", type=int)
parser.add_argument("ufactor", type=float)
parser.add_argument("seed", type=int)

args = parser.parse_args()

ufactor = args.ufactor
graph = args.graph
k = args.k
seed = args.seed

hg = open(graph, 'r')

header_parsed = False
count_nets = 0
count_nodes = 0
total_weight = 0

for line in hg:
     # ignore comment lines
    if line.startswith('%'):
        continue
    if not header_parsed:
        hg_param = line.split()
        numNets = int(hg_param[0])
        numNodes = int(hg_param[1])
        header_parsed = True

        if (len(hg_param) < 3):
            total_weight = numNodes
            break
        continue

    if count_nets < numNets:
        count_nets += 1
        continue

    if count_nodes < numNodes:
        total_weight += int(line)
hg.close()
    
#We use hMetis-RB as initial partitioner. If called to partition a graph into k parts
#with an UBfactor of b, the maximal allowed partition size will be 0.5+(b/100)^(log2(k)) n.
#In order to provide a balanced initial partitioning, we determine the UBfactor such that
#the maximal allowed partiton size corresponds to our upper bound i.e.
#(1+epsilon) * ceil(total_weight / k).
exp = 1.0 / math.log(k,2)
rbufactor = 50.0 * (2 * math.pow((1 + ufactor), exp)
            * math.pow(math.ceil(float(total_weight)/k) / float(total_weight), exp) - 1)

actual_rbufactor = rbufactor
if rbufactor < 0.1:
    rbufactor = 0.1

start = time.time()
p = Popen([hMetis,
           str(graph),
           str(k),
           '-ptype=rb',
	   '-otype=soed',
           '-reconst',
           '-dbglvl=34',
           '-ufactor='+str(rbufactor),
           '-seed='+str(seed)], stdout=PIPE, bufsize=1)

result_string = ("RESULT graph="+ntpath.basename(graph) +
        " k=" + str(k) +
        " epsilon=" + str(ufactor) +
        " rbUfactor=" +str(rbufactor) +         
        " seed=" + str(seed) )

i = 0
results = []
part_sizes = []
hg_weight = 0
for line in iter(p.stdout.readline, b''):
    s = str(line).strip()
    print(s)
    if ("UBfactor" in s):
        result_string += (" usedRbUFactor=" + str(float(s.split(',')[1][12:])))
    if ("Vtxs" in s):
        #print(s.split(','))
        result_string += (" numHNs="+str(int(s.split(',')[1][7:])))
        result_string += (" numHEs="+str(int(s.split(',')[2][10:])))
        hg_weight = int(s.split(',')[1][7:])
    if ("initial soed" in s):
        result_string += (" initialSOED"+str(i)+"="+str(float(s.split(':')[1][1:-3])))
        i = i+1
    if ("Multilevel" in s):
        result_string += (" totalPartitionTime="+str(float(s.split()[1])))
        results.append(s)
    if ("Coarsening" in s):
        result_string += (" coarseningTime="+str(float(s.split()[1])))
        results.append(s)
    if ("Initial Partition" in s):
        result_string += (" initialPartitionTime="+str(float(s.split()[2])))
        results.append(s)
    if ("Uncoarsening" in s):
        result_string += (" uncoarseningRefinementTime="+str(float(s.split()[1])))
        results.append(s)
    if ("Total" in s):
        results.append(s)
    if ("Hyperedge Cut" in s):
        result_string += (" cut="+str(float(s.split()[2])))
        results.append(s)
    if ("Sum of External" in s):
        result_string += (" soed="+str(float(s.split()[4])))
        results.append(s)
    if ("Absorption" in s):
        result_string += (" absorption="+str(float(s.split()[1])))
        results.append(s)
    if ("[" in s):
        split = s.split(']')
        for token in split[:-1]:
            t = re.search('\(.*?\)', token)
            part_size = float(t.group(0)[1:-1])
            part_sizes.append(part_size)

p.communicate()  # close p.stdout, wait for the subprocess to exit
end = time.time()

# compute imbalance
max_part_size = max(part_sizes)
total_weight = sum(part_sizes)

print(result_string  + " type=hMetis-RB" + " objective=SOED" + " measuredTotalPartitionTime=" + str(end-start) + " imbalance=" + str(float(max_part_size) / math.ceil(float(total_weight)/k) - 1.0) + " actualRBufactor=" + str(actual_rbufactor))
