#! /bin/bash

SCRIPT_DIR=$(cd $(dirname $0); pwd -P)
cd $SCRIPT_DIR/
python desklight.py  2>&1  > /dev/null

