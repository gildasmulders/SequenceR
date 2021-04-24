#!/bin/bash
# Submission script for Manneback
#SBATCH --job-name=sequencer_training
#SBATCH --time=10:00:00 # hh:mm:ss
#
#SBATCH --ntasks=1
#SBATCH --gres="gpu:1"
#SBATCH --mem-per-cpu=2625 # megabytes
#SBATCH --partition=gpu
#
#
#SBATCH --output=sequencer_out.txt

srun mysequencer-train-test.sh --uniqueid --checkpoint=10000 --steps=20000
#srun mysequencer-test.sh --model=/home/ucl/ingi/muldersg/SequenceR/model/final-model-word2vec_step_10000.pt

