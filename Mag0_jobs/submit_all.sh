#!/bin/bash
# Submit all Mag0 parquet-to-memmap conversion jobs

CONVERTER_DIR=/n/holylfs05/LABS/arguelles_delgado_lab/Everyone/nkamp/ML/sources/nt-mmap-converter
PARQUET_BASE=/n/holylfs05/LABS/arguelles_delgado_lab/Everyone/nkamp/IceCube/MagNeMITe/data/MagNeMITe_parquets/Mag0
OUTPUT_BASE=/n/holylfs05/LABS/arguelles_delgado_lab/Everyone/nkamp/ML/analysis/MagNeMITe/mmap_data/Mag0_parquets
JOB_DIR=${CONVERTER_DIR}/Mag0_jobs

cd ${JOB_DIR}

# Create output directories
mkdir -p ${OUTPUT_BASE}/background
mkdir -p ${OUTPUT_BASE}/signal/MixingDIS

# Submit jobs
echo "Submitting CORSIKA job..."
sbatch convert_corsika.sbatch

echo "Submitting NuGen jobs..."
for dataset in 22852 22853 22855 22856; do
    sbatch convert_nugen_${dataset}.sbatch
done

echo "Submitting GENIE jobs..."
for dataset in 23257 23258; do
    sbatch convert_genie_${dataset}.sbatch
done

echo "Submitting SIREN DipoleDIS job..."
sbatch convert_dipoledis.sbatch

echo "Submitting SIREN MixingDIS jobs..."
for flavor in nue nuebar numu numubar; do
    sbatch convert_mixingdis_${flavor}.sbatch
done

echo "All jobs submitted!"
