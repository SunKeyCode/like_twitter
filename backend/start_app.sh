#!/bin/bash

WORKER=""

echo ">>> script started <<<"
echo "Debug=$DEBUG"
trap exit SIGINT

# initializes db
alembic upgrade head
alembic_status=$?

if [ $alembic_status -ne 0 ]
then
  echo "Script ended due to alembic error..."
  exit 1
fi
echo "alembic status=$alembic_status"

if [ $WORKERS ]
then
  workers=$WORKERS
else
  workers=4
fi

# Starts application
if [ $DEBUG = "true" ]
then
  echo "Отладка включена"
  uvicorn main:app --host=0.0.0.0 --reload & WORKER=$!
else
  uvicorn main:app --host=0.0.0.0 --workers=$workers & WORKER=$!
fi
wait $WORKER

echo ">>> ended <<<"
