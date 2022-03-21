#!/bin/bash

scriptname="wwwordlist.py"

pip3 install -r requirements.txt

ddir=$(pwd)

2ulb 2&>/dev/null
	if [ $? -eq 127 ]
	then
		if [ "$1" = "-auto" ]
		then
			cd .. 
			git clone https://github.com/Zarcolio/2ulb
			sudo python3 2ulb/2ulb.py 2ulb/2ulb.py
			cd "$ddir" || exit
			sudo 2ulb $scriptname
			exit 0
		else
			while true; do
				read -p -r "2ulb not found, install 2ulb? [y/n]: " yn
				case $yn in
				    [Yy]*) cd .. || exit; git clone https://github.com/Zarcolio/2ulb ; sudo python3 2ulb/2ulb.py 2ulb/2ulb.py ; cd "$dir" || exit ; sudo 2ulb $scriptname; exit 0 ;;
				    [Nn]*) echo "Aborted" ; exit 1 ;;
				esac
			done
		fi
	else
		sudo 2ulb $scriptname
	fi
