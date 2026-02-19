#!/bin/bash
#SBATCH --job-name=mmap_corsika
#SBATCH --output=Mag0_jobs/slurm_logs/mmap_corsika_%j.out
#SBATCH --error=Mag0_jobs/slurm_logs/mmap_corsika_%j.err
#SBATCH -p arguelles_delgado,sapphire,shared
#SBATCH -c 16
#SBATCH --time=24:00:00
#SBATCH --mem=60000

# Environment setup
source /n/holylfs05/LABS/arguelles_delgado_lab/Everyone/nkamp/spack/share/spack/setup-env.sh
spack env activate mlenv

cd /n/holylfs05/LABS/arguelles_delgado_lab/Everyone/nkamp/ML/sources/nt-mmap-converter

INPUT=/n/holylfs05/LABS/arguelles_delgado_lab/Everyone/nkamp/IceCube/MagNeMITe/data/MagNeMITe_parquets/Mag0/background/22803_extended/event
OUTPUT=/n/holylfs05/LABS/arguelles_delgado_lab/Everyone/nkamp/ML/analysis/MagNeMITe/mmap_data/Mag0_parquets/background/22803_extended

python converter.py --source magnemite --input ${INPUT} --output ${OUTPUT} --filetype CORSIKA --info
