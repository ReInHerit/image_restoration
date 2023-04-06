#!/bin/bash
echo 'starting Django sever'
# turn on bash's job control
python /app/manage.py runserver 0.0.0.0:8000 &
sleep 5
#
echo 'starting python sever'
python /app/bring_to_life.py

echo 'all servers started'

