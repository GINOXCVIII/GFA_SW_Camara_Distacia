#! /bin/sh
SCRIPT_PATH=$( cd $(dirname $0) ; pwd )
cd "${SCRIPT_PATH}"
cd src/
python3 main.py
