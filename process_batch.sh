#!/bin/bash
#SBATCH --job-name=mmap_converter
#SBATCH --output=slurm_logs/mmap_out_%A_%a.txt
#SBATCH --error=slurm_logs/mmap_err_%A_%a.txt
#SBATCH -p arguelles_delgado,sapphire,shared
#SBATCH -c 32 # num cores
#SBATCH --time=08:00:00
#SBATCH --mem 30000 # memory in MB

# Env
source /n/holylfs05/LABS/arguelles_delgado_lab/Everyone/nkamp/spack/share/spack/setup-env.sh
spack env activate mlenv

# signal
tag=IceCube_DipoleDIS_fixedXS_22Sep2025
input=/n/holylfs05/LABS/arguelles_delgado_lab/Everyone/nkamp/IceCube/MagNeMITe/data/MAGNEMITE/signal/Mag0/${tag}/event/
output=/n/holylfs05/LABS/arguelles_delgado_lab/Everyone/nkamp/ML/analysis/MagNeMITe/mmap_data/Mag0/signal2/${tag}
filetype=SIREN

# background
# tag=23258
# input=/n/holylfs05/LABS/arguelles_delgado_lab/Everyone/nkamp/IceCube/MagNeMITe/data/MAGNEMITE/background/Mag0/${tag}/event/
# output=/n/holylfs05/LABS/arguelles_delgado_lab/Everyone/nkamp/ML/analysis/MagNeMITe/mmap_data/Mag0/background/${tag}
# filetype=NuGen

python converter.py --source magnemite --input ${input} --output ${output} --filetype ${filetype}