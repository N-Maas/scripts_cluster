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
kahypar = str('/home/kit/stud/ucywg/partitioners/kahypar-master/')
config = str('km1_kKaHyPar_dissertation.ini')
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

kahypar_bin = kahypar + 'build/kahypar/application/KaHyPar'
kahypar_config = kahypar + 'config/' + config

start = time.time()

p = Popen([kahypar_bin,
        '-h',
        str(graph),
        '-k',
        str(k),
        '-e',
        str(ufactor),
        '--seed',
        str(seed),
        '-s',
        '1',
        '-o',
        'km1',
        '-m',
        'direct',
        '-p',
        kahypar_config], stdout=PIPE, bufsize=1)

result_string = ""

for line in io.TextIOWrapper(p.stdout, encoding="utf-8"):
    s = str(line).strip()
    if s.startswith("RESULT"):
        result_string = s
    else:
        # print(s)
        pass

end = time.time()

print(result_string + " type=kKaHyPar" + " measuredTotalPartitionTime=" + str(end-start))
