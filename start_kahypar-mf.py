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
# set path to KaHyPar binary:
kahypar = str('/home/kit/iti/mp6747/kahypar/release/kahypar/application/KaHyPar')
###################################

my_env = os.environ.copy()

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

# This is the configuration that we will use in the paper
p = Popen([kahypar,
           '-h'+str(graph),
           '-k'+str(k),
           '-e'+str(ufactor),
           '-okm1',
           '-mdirect',
           '-p/home/kit/iti/mp6747/kahypar/config/km1_kahypar_mf_jea19.ini',
           '--seed='+str(seed),
	   '--sp-process=1'
       ], stdout=PIPE, bufsize=1, env=my_env)

for line in iter(p.stdout.readline, b''):
    s = str(line).strip()
    print(s)

p.communicate()  # close p.stdout, wait for the subprocess to exit
