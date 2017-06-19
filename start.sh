# !/bin/bash

status=$1
if [ -z "$status" ]; then
	status="what"
fi

if [ "$status" == "install" ]; then
    pip3 install pytelegrambotapi
    pip3 install jenkinsapi

elif [ "$status" == "start" ]; then
    lockfile -r 0 file.lock || exit 1
    python3 telegram_jenkins.py
    if [ "$?" == "0"  ]; then
        rm -f file.lock
        exit 1
    fi
    rm -f file.lock
    exit 0

elif [ "$status" == "what" ]; then
    echo "Запусти с параметром: install \ start"
fi
