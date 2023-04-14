#!/bin/bash
echo 'starting Django server on port ' $PORT
python /app/manage.py runserver 0.0.0.0:$PORT
echo 'all servers started'

