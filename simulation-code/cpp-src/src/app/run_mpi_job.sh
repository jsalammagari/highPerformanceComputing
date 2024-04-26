#!/bin/bash
#SBATCH --job-name=mpi_pm10_processing
#SBATCH --output=mpi_job_%j.out
#SBATCH --error=mpi_job_%j.err
#SBATCH --ntasks=10
#SBATCH --time=01:00:00
#SBATCH --partition=broadwl

module load mpi
mpirun ./pm10_simulation
