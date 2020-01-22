#!/bin/bash
QUEUE_FILE=$1
TMP_QUEUE_FILE=$QUEUE_FILE".tmp"
FAILED_QUEUE_FILE=$QUEUE_FILE".failed"
DEBUG_FILE=$QUEUE_FILE".debug"

module load lib/boost/1.55.0
module unload compiler/gnu/5.2
module load compiler/gnu/9.1
module load mpi/openmpi/4.0-gnu-9.1
module unload devel/python/2.7.12
module load devel/python/3.4.1
export LD_LIBRARY_PATH=/home/kit/iti/mp6747/kahip-mit-flowmod/extern/argtable-2.10/lib/:$LD_LIBRARY_PATH

MAX_IDLE_STEPS=100
STEP=0
SLEEP_TIME=3	#in seconds

if [ ! -f $QUEUE_FILE ]
then
	echo "Queue file" $QUEUE_FILE "not found"
else
	while [ $STEP -lt $MAX_IDLE_STEPS ]
	do
		if [ ! -s $QUEUE_FILE ]
		then
			STEP=$((STEP+1))
			sleep $SLEEP_TIME"s"
		else
			STEP=0
			LINE=$(head -n 1 $QUEUE_FILE)
			echo "Working on $LINE"
			if eval $LINE
			then
				echo "Finished $LINE"
			else
				echo "Failed $LINE"
				echo "$LINE" >> $FAILED_QUEUE_FILE
			fi
			tail -n +2 $QUEUE_FILE > $TMP_QUEUE_FILE && mv $TMP_QUEUE_FILE $QUEUE_FILE
		fi
	done
fi
