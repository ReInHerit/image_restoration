#!/bin/bash
echo 'starting Django server on port ' $PORT
# turn on bash's job control
python /app/manage.py runserver 0.0.0.0:$PORT &
sleep 5
#
echo 'starting Flask server on port' $FLASK_PORT
python /app/bring_to_life.py

echo 'all servers started'

