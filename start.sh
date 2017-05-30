# !/bin/bash\

lockfile -r 0 file.lock || exit 1

# python3 test.py
python3 telegram_jenkins.py

if [ "$?" == "0"  ]
then
  rm -f file.lock
  exit 1
fi

rm -f file.lock

exit 0
