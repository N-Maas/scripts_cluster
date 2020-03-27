#!/usr/bin/python3
from subprocess import Popen, PIPE
import ntpath
import argparse
import time
import re
import math
import os
import io
from os import mkdir
from os.path import basename, splitext, isfile, isdir
from shutil import copyfile, rmtree

###################################
# SETUP ENV
###################################
mondriaan = str('/home/kit/stud/ucywg/partitioners/Mondriaan/mondriaan/tools/Mondriaan')
evaluator = str('/home/kit/stud/ucywg/partitioners/kahypar/build/tools/EvaluateMondriaanPartition')
converter = str('/home/kit/stud/ucywg/partitioners/kahypar/build/tools/HgrToMondriaanMtx')
CONVERTER_OUTPUT = open("/dev/null")
MONDRIAAN_TMP = str('/tmp')
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

modified_hg_dir = MONDRIAAN_TMP + "/mondriaan_" + splitext(basename(graph))[0] + ".parts" + str(k) + ".epsilon" + str(ufactor) + ".seed" + str(seed)
modified_hg_path = modified_hg_dir + "/" + splitext(basename(graph))[0] + ".parts" + str(k) + ".epsilon" + str(ufactor) + ".seed" + str(seed) + ".hgr"
mondriaan_graph = modified_hg_path + ".mondriaan.mtx"

if not isdir(modified_hg_dir):
    mkdir(modified_hg_dir)

if not isfile(modified_hg_path):
    copyfile(graph, modified_hg_path)

if not isfile(mondriaan_graph):
    Popen([str(converter), str(modified_hg_path)], stdout=CONVERTER_OUTPUT).communicate()


start = time.time()
p = Popen([mondriaan,
           str(mondriaan_graph),
           str(k),
           str(ufactor),
           '-Metric=lambda1',
           '-SplitStrategy=onedimcol',
           '-Seed='+str(seed)], stdout=PIPE, bufsize=1)

result_string = ("RESULT epsilon=" + str(ufactor) +    
        " seed=" + str(seed))

mond_time = "none"
for line in io.TextIOWrapper(p.stdout, encoding="utf-8"):
    s = str(line).strip()
    print(s)
    if ("matrix distribution elapsed time:" in s):
        mond_time = float(re.sub('seconds$', '', s[33:]))

end = time.time()

mondriaan_output_file = mondriaan_graph+'-v'+str(k)#+'-s'+str(seed)

p = Popen([evaluator,
           str(modified_hg_path),
           str(mondriaan_output_file)], stdout=PIPE, bufsize=1)

for line in io.TextIOWrapper(p.stdout, encoding="utf-8"):
    s = str(line).strip()
    print(s)
    if ("RESULT " in s):
        result_string = result_string+str(s[6:])

rmtree(modified_hg_dir) # delete the temporary directory after usage

print(result_string + " type=mondriaan" + " objective=km1" + " partitionTime=" + str(mond_time) + " measuredTotalPartitionTime=" + str(end-start))
