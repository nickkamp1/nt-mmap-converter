#!/bin/bash
#SBATCH --job-name=mmap_mag1
#SBATCH --output=slurm_logs/mmap_mag1_%j.out
#SBATCH --error=slurm_logs/mmap_mag1_%j.err
#SBATCH -p serial_requeue,arguelles_delgado,sapphire,shared
#SBATCH -c 1
#SBATCH --time=02:00:00
#SBATCH --mem=8G

# Environment setup
source /n/holylfs05/LABS/arguelles_delgado_lab/Everyone/nkamp/spack/share/spack/setup-env.sh
spack env activate mlenv

cd /n/holylfs05/LABS/arguelles_delgado_lab/Everyone/nkamp/ML/sources/nt-mmap-converter

export COSMIC_CUT=0.99392705
export STARTING_TRACK_CUT=0.29585832
export OTHER_TRACK_CUT=0.99343127

if [ -z "$TAG" ]; then
    export TAG=signal/MixingDIS/nue
fi

if [ -z "$FILETYPE" ]; then
    export FILETYPE=SIREN
fi


INPUT=/n/holylfs05/LABS/arguelles_delgado_lab/Everyone/nkamp/IceCube/MagNeMITe/data/MagNeMITe_parquets/Mag1/${TAG}/event
OUTPUT=/n/holylfs05/LABS/arguelles_delgado_lab/Everyone/nkamp/IceCube/MagNeMITe/data/MagNeMITe_mmaps/Mag1/${TAG}

python converter.py --source magnemite --input ${INPUT} --output ${OUTPUT} --filetype ${FILETYPE} --cuts "mag1_bdt_hnl_vs_cosmics > ${COSMIC_CUT} and mag1_bdt_hnl_vs_starting_tracks > ${STARTING_TRACK_CUT} and mag1_bdt_hnl_vs_other_tracks > ${OTHER_TRACK_CUT}" --info
