#!/usr/bin/python
from subprocess import Popen, PIPE
import ntpath
import argparse
import time
import re
import math
import os
import sys

###################################
# SETUP ENV
###################################
balance = str('/home/kit/stud/ucywg/partitioners/kahypar/build/tools/BalanceConstraint')
###################################

parser = argparse.ArgumentParser()
parser.add_argument("partitioner", type=str)
parser.add_argument("graph", type=str)
parser.add_argument("k", type=int)
parser.add_argument("ufactor", type=float)
parser.add_argument("seed", type=int)

args = parser.parse_args()

partitioner = args.partitioner
graph = args.graph
k = args.k
ufactor = args.ufactor
seed = args.seed

p = Popen([balance,
        '-k',
        str(k),
        str(graph)], stdout=PIPE, bufsize=1)

avg_weight = 0
border = 0

for line in iter(p.stdout.readline, b''):
    s = str(line).strip()
    if s.startswith('average block weight'):
        avg_weight = int(re.match(r".* (\d+$)", s).group(1))
    if s.startswith('calculated border'):
        border = int(re.match(r".* (\d+$)", s).group(1))

p.communicate()  # close p.stdout, wait for the subprocess to exit

new_factor = (float(border) / float(avg_weight) * (1 + float(ufactor))) - 1

p = Popen([str(partitioner),
        str(graph),
        str(k),
        str(new_factor),
        str(seed)], stdout=PIPE, bufsize=1, cwd=os.path.realpath(os.getcwd()))

result_string = ""

for line in iter(p.stdout.readline, b''):
    s = str(line).strip()
    if s.startswith("RESULT"):
        result_string = s
    else:
        print(s)

p.communicate()  # close p.stdout, wait for the subprocess to exit

print(result_string + " baseEpsilon=" + str(ufactor) + " calculatedBorder=" + str(border))
