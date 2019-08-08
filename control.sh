#!/bin/bash

start() {
   tid=`ps -ef|grep simple_json_backend.py|grep -v grep|awk '{print $2}'`
   if [ ${tid:=0} -ne 0 ]
   then
		echo "Start failed, please check the script"
   else
		source /opt/simple_json_flask_omnibus/venv/bin/activate
		nohup /opt/simple_json_flask_omnibus/venv/bin/python3 -u /opt/simple_json_flask_omnibus/simple_json_backend.py > /opt/simple_json_flask_omnibus/access.log 2>&1 &
    PID=`ps -ef|grep simple_json_backend |grep -v grep|awk '{print $2}'`
    echo PID:$PID "Started"
   fi
}

stop() {
    PIDS=`ps -ef|grep simple_json_backend |grep -v grep|awk '{print $2}'`
    ps -ef|grep simple_json_backend |grep -v grep|awk '{print $2}'|xargs kill -9
    echo PID:$PIDS" Killed"
    rm -rf /opt/simple_json_flask_omnibus/access.log
}


restart() {
   echo "Restarting simple_json_backend"
   stop
   sleep 1
   start
}

show() {
   ps -ef|grep simple_json_backend.py|grep -v grep
}


while getopts "uklr" OPTION
do
  case $OPTION in
  u)
    start
    ;;
  k)
    stop
    ;;
  l)
    show
    ;;
  r)
    restart
    ;;
  esac
done