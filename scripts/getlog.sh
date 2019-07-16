#!/bin/sh
echo $LOGS
P=$(eval find $LOGS -name *$1*)
echo $P
less $P
