# !/bin/bash

status=$1

if [ "$status" == "install" ]; then
		# apt-get install python3 python-setuptools python3-pip
		sudo dnf -y install python3 python-setuptools python3-pip procmail
		sudo pip3 install pyTelegramBotAPI jenkinsapi python-gitlab
		sudo pip install logging
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

elif [ -z "$status" -o "$status" != "install" -o "$status" != "start" -o "$status" != "stop" ]; then
	status="what"
fi

if [ "$status" == "what" ]; then
    echo "Запусти с параметром: install \ start \ stop"

fi
