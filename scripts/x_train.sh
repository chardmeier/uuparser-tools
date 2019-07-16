#!/bin/sh

echo "Submitting batch job: $1";
sbatch -J $1 train.sh $1;
