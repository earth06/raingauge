#! /bin/bash

RUNPYTHON=/home/takato/miniforge3/envs/pi/bin/python
SCRIPT_DIR=$(cd $(dirname $0); pwd -P)

cd $SCRIPT_DIR/src
$RUNPYTHON raingauge_observer.py  2>&1  > /dev/null

