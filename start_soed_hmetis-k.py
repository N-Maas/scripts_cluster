#!/usr/bin/python3
from subprocess import Popen, PIPE
import ntpath
import argparse
import time
import re
import math
import os
import io

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

start = time.time()

p = Popen([hMetis,
           str(graph),
           str(k),
           '-ptype=kway',
           '-dbglvl=34',
	   '-otype=soed',
           '-ufactor='+str(int(ufactor*100)),
           '-seed='+str(seed)], stdout=PIPE, bufsize=1)

result_string = ("RESULT graph="+ntpath.basename(graph) +
        " k=" + str(k) +
        " epsilon=" + str(ufactor) +
        " seed=" + str(seed))

i = 0
results = []
part_sizes = []
hg_weight = 0
for line in io.TextIOWrapper(p.stdout, encoding="utf-8"):
    s = str(line).strip()
    # print(s)
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

end = time.time()

# compute imbalance
max_part_size = max(part_sizes)
total_weight = sum(part_sizes)

print(result_string + " type=hMetis-K" + " objective=SOED" + " measuredTotalPartitionTime=" + str(end-start) + " imbalance=" + str(float(max_part_size) / math.ceil(float(total_weight)/k) - 1.0))
