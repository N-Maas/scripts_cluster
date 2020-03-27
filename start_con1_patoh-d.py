#!/usr/bin/python3
from subprocess import Popen, PIPE
import ntpath
import re
import os
import argparse
import time
import math
import random
import sys
import io
from os.path import basename

###################################
# SETUP ENV
###################################
# PaToH = str('/software/patoh-Linux-x86_64/Linux-x86_64/patoh')
PaToH = str('/home/kit/stud/ucywg/partitioners/PaToH/build/Linux-x86_64/patoh')
PATOH_TMP = str('/tmp')
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

if (seed == -1):
    seed = random.randint(0, 2**32 - 1)

modified_hg_path = PATOH_TMP+'/patoh_' + basename(graph)
# we need to modify our hypergraph format due to a different input file format for patoh3.5
hg = open(graph, 'r')
modified_hg = open(modified_hg_path, 'w')
#print("modified hg path: " + modified_hg_path)

# patoh expects the following header:
# (0 /1 indexing scheme) |V| |E| |pins| (0 = no weights, 1 = cell weight, 2 = net weight, 3 both) constraint???

header_parsed = False

hg_param = [] # edges, nodes, type

modified_hg_list = []

count_nets = 0
count_pins = 0
total_weight = 0

node_weights = ""
for line in hg:
# ignore comment lines
    if line.startswith('%'):
        continue
    
    if not header_parsed:
        hg_param = line.split()
        if (len(hg_param) < 3):
            # no type specified, assume unweighted hg
            hg_param.append(0)
        else:
            if hg_param[2] == '0':
                # unweighted
                hg_param[2] = 0
            elif hg_param[2] == '1':
                # edge weights
                hg_param[2] = 2
            elif hg_param[2] == '10':
                # node weights
                hg_param[2] = 1
            elif hg_param[2] == '11':
                # both
                hg_param[2] = 3
            else:
                print("ERROR! type: " + str(int(hg_param[2])))
        header_parsed = True
    else:
    # count the number of pins
        if count_nets < int(hg_param[0]):
            count_pins += len(line.split())
            if (int(hg_param[2]) > 1):
                # ignore the first 'pin' since it is the weight
                count_pins -= 1
            count_nets += 1
            modified_hg_list.append(line)
        else:
        # from now on, node weights follow
        # patoh wants all node weights in a single line!
            assert(len(line.split()) == 1)
            node_weights += line.split()[0] + " "
            total_weight += int(line.split()[0])

# write the modified hypergraph
modified_hg.write(str(1) + " " + str(hg_param[1]) + " " + str(hg_param[0]) + " " + str(count_pins) + " " + str(hg_param[2]) + '\n')
for line in modified_hg_list:
    modified_hg.write(line)
    
modified_hg.write(node_weights+ '\n')
modified_hg.close()
hg.close()

start = time.time()
p = Popen([PaToH,
           modified_hg_path,
           str(k),
           'SD='+str(seed), # seed
           'FI='+str(ufactor), # imbalance ratio
           'OD=2', # non verbose output
           'UM=O', # connectivity metric
           'WI=0', # dont write the partitioning info to disk
           'BO=C', # balance on cell
           'A0=100', #  MemMul_CellNet
           'A1=100', #  MemMul_Pins
           'A2=100', #  MemMul_General
       ], stdout=PIPE, bufsize=1)

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
    print(s)
    if ("Cells" in s):
        print(s.split(','))
        t = re.compile('#Cells : \s*([^\s]*)')
        result_string += (" numHNs="+str(t.findall(s)[0]))
        t = re.compile('Nets : \s*([^\s]*)')
        result_string += (" numHEs="+str(t.findall(s)[0]))
    if ("Par.Res." in s):
        t = re.compile('Cost: \s*([^\s]*)')
        result_string += (" initialkMinusOne="+str(float(t.findall(s)[0])))
    if ("Total   " in s):
        t = re.compile('Total\s*:\s*([^\s]*)')
        result_string += (" totalPartitionTime="+str(float(t.findall(s)[0])))
    if ("Coarsening " in s):
        t = re.compile('Coarsening\s*:\s*([^\s]*)')
        result_string += (" coarseningTime="+str(float(t.findall(s)[0])))
    if ("Partitioning " in s):
        t = re.compile('Partitioning\s*:\s*([^\s]*)')
        result_string += (" initialPartitioningTime="+str(float(t.findall(s)[0])))
    if ("Uncoarsening " in s):
        t = re.compile('Uncoarsening\s*:\s*([^\s]*)')
        result_string += (" uncoarseningRefinementTime="+str(float(t.findall(s)[0])))
    if ("'Con - 1' Cost" in s):
        t = re.compile("'Con - 1' Cost:\s*([^\s]*)")
        result_string += (" km1="+str(float(t.findall(s)[0])))
    if ("Part Weights" in s):
        t = re.compile('Min=\s*([^\s]*)')
        min_part = float(t.findall(s)[0])
        t = re.compile('Max=\s*([^\s]*)')
        max_part = float(t.findall(s)[0])
        t = re.compile('Max=\s*[^\s]*\s*\(([^\s]*)\)')
        their_eps = t.findall(s)[0]
        result_string += " reported_imbalance="+str(their_eps)
        imb = float(max_part) / math.ceil(float(total_weight) / k) - 1.0
        result_string += " imbalance="+str(imb)

end = time.time()

os.remove(modified_hg_path) # delete the temporary file after usage

print(result_string + " type=PaToH-D" + " objective=km1" +  " measuredTotalPartitionTime=" + str(end-start))
