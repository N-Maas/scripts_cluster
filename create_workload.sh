#!/bin/bash

# Set the folder containing the hypergraphs
instance_dir="/pfs/work2/workspace/scratch/ucywg-benchmarks_node_weights-0/"

# Values of k
declare -a kValues=("2" "32" "128")

# Imbalance
declare -a eValues=("0.03" "0.1")

# scripts to execute
start_scripts="$PWD/start_soed_kkahypar*.py"

# create scripts
create_scripts="$PWD/create_arg_combinations.py"

# wrapper script
wrapper="$PWD/start_partitioner_weighted_cluster.py"

# workload file
workload_file="workload.txt"

module load lib/boost/1.55.0
module unload compiler/gnu/5.2
module load compiler/gnu/9.1
module load mpi/openmpi/4.0-gnu-9.1
module load devel/python/3.3.3

$create_scripts

if [[ ! -d "$PWD/../results" ]]; then
    mkdir "$PWD/../results"
fi

for partitioner in $start_scripts
do
    if [[ ! -f "$partitioner" ]]; then
	echo "$partitioner does not exist"
	exit 1
    fi
    tool_name=$(basename "$partitioner")
    tool_name="${tool_name%.py}"
    if [[ ! -d "$PWD/../results/$tool_name" ]]; then
	mkdir "$PWD/../results/$tool_name"
    fi
    for instance in $instance_dir/*.hgr;
    do
        instance_name=`echo $instance | sed 's!.*/!!'`
    	for k in "${kValues[@]}"
    	do
            for epsilon in "${eValues[@]}"
            do
                for seed in `seq 0 9`
                do
                    echo "timeout 8h $wrapper $partitioner $instance $k $epsilon $seed >> $PWD/../results/$tool_name/$instance_name.$k.$epsilon.$seed.results" >> $workload_file
                done
    	    done
        done
    done
done
