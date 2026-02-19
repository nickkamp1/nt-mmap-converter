#!/bin/bash
#SBATCH --job-name=mmap_mixing_nuebar
#SBATCH --output=Mag0_jobs/slurm_logs/mmap_mixing_nuebar_%j.out
#SBATCH --error=Mag0_jobs/slurm_logs/mmap_mixing_nuebar_%j.err
#SBATCH -p arguelles_delgado,sapphire,shared
#SBATCH -c 8
#SBATCH --time=08:00:00
#SBATCH --mem=30000

# Environment setup
source /n/holylfs05/LABS/arguelles_delgado_lab/Everyone/nkamp/spack/share/spack/setup-env.sh
spack env activate mlenv

cd /n/holylfs05/LABS/arguelles_delgado_lab/Everyone/nkamp/ML/sources/nt-mmap-converter

INPUT=/n/holylfs05/LABS/arguelles_delgado_lab/Everyone/nkamp/IceCube/MagNeMITe/data/MagNeMITe_parquets/Mag0/signal/MixingDIS/nuebar/event
OUTPUT=/n/holylfs05/LABS/arguelles_delgado_lab/Everyone/nkamp/ML/analysis/MagNeMITe/mmap_data/Mag0_parquets/signal/MixingDIS/nuebar

python converter.py --source magnemite --input ${INPUT} --output ${OUTPUT} --filetype SIREN --info
