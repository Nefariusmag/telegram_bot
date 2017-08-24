# !/bin/bash

status=$1
if [ -z "$status" ]; then
	status="what"
fi

if [ "$status" == "install" ]; then
		apt-get install python3 python-setuptools python3-pip
		yum install python3 python-setuptools python3-pip
		pip3 install logging pyTelegramBotAPI jenkinsapi python-gitlab

elif [ "$status" == "start" ]; then
    lockfile -r 0 file.lock || exit 1
    ./telegram_jenkins.py &
    if [ "$?" == "0"  ]; then
        rm -f file.lock
        exit 1
    fi
    rm -f file.lock
    exit 0

elif [ "$status" == "stop" ]; then
    	kill -9 $(ps aux | grep -v grep | grep telegram_jenkins.py | awk '{print($2)}')

elif [ "$status" == "what" ]; then
    echo "Запусти с параметром: install \ start \ stop"

fi
