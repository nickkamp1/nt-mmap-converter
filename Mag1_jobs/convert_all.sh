
# background
#sbatch --export TAG=background/22803_extended,FILETYPE=CORSIKA convert.sbatch
sbatch --export TAG=background/22852,FILETYPE=NuGen convert.sbatch
sbatch --export TAG=background/22853,FILETYPE=NuGen convert.sbatch
sbatch --export TAG=background/22855,FILETYPE=NuGen convert.sbatch
sbatch --export TAG=background/22856,FILETYPE=NuGen convert.sbatch
sbatch --export TAG=background/23257,FILETYPE=NuGen convert.sbatch
sbatch --export TAG=background/23258,FILETYPE=NuGen convert.sbatch
# signal
#sbatch --export TAG=signal/DipoleDIS,FILETYPE=SIREN convert.sbatch
sbatch --export TAG=background/MixingDIS/nue,FILETYPE=SIREN convert.sbatch
sbatch --export TAG=background/MixingDIS/numu,FILETYPE=SIREN convert.sbatch
sbatch --export TAG=background/MixingDIS/nuebar,FILETYPE=SIREN convert.sbatch
sbatch --export TAG=background/MixingDIS/numubar,FILETYPE=SIREN convert.sbatch
