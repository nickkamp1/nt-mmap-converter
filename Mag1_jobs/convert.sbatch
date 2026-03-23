#!/bin/bash
#SBATCH --job-name=mmap_mag1
#SBATCH --output=slurm_logs/mmap_mag1_%j.out
#SBATCH --error=slurm_logs/mmap_mag1_%j.err
#SBATCH -p arguelles_delgado,sapphire,shared
#SBATCH -c 8
#SBATCH --time=05:00:00
#SBATCH --mem=30000

# Environment setup
source /n/holylfs05/LABS/arguelles_delgado_lab/Everyone/nkamp/spack/share/spack/setup-env.sh
spack env activate mlenv

cd /n/holylfs05/LABS/arguelles_delgado_lab/Everyone/nkamp/ML/sources/nt-mmap-converter

if [ -z "$TAG" ]; then
    export TAG=signal/MixingDIS/nue
fi

if [ -z "$FILETYPE" ]; then
    export FILETYPE=SIREN
fi


INPUT=/n/holylfs05/LABS/arguelles_delgado_lab/Everyone/nkamp/IceCube/MagNeMITe/data/MagNeMITe_parquets/Mag1/${TAG}/event
OUTPUT=/n/holylfs05/LABS/arguelles_delgado_lab/Everyone/nkamp/IceCube/MagNeMITe/data/MagNeMITe_mmaps/Mag1/${TAG}

python converter.py --source magnemite --input ${INPUT} --output ${OUTPUT} --filetype ${FILETYPE} --cuts "mag1_class_0 > 0.8" --info
