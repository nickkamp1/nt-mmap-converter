
# background
sbatch --export TAG=hnl_tracks/background/22803_extended,FILETYPE=CORSIKA convert.sbatch
sbatch --export TAG=hnl_tracks/background/22852,FILETYPE=NuGen convert.sbatch
sbatch --export TAG=hnl_tracks/background/22853,FILETYPE=NuGen convert.sbatch
sbatch --export TAG=hnl_tracks/background/22855,FILETYPE=NuGen convert.sbatch
sbatch --export TAG=hnl_tracks/background/22856,FILETYPE=NuGen convert.sbatch
sbatch --export TAG=hnl_tracks/background/23257,FILETYPE=NuGen convert.sbatch
sbatch --export TAG=hnl_tracks/background/23258,FILETYPE=NuGen convert.sbatch
# signal
# sbatch --export TAG=hnl_tracks/signal/DipoleDIS,FILETYPE=SIREN convert.sbatch
sbatch --export TAG=hnl_tracks/signal/MixingDIS/nue,FILETYPE=SIREN convert.sbatch
sbatch --export TAG=hnl_tracks/signal/MixingDIS/numu,FILETYPE=SIREN convert.sbatch
sbatch --export TAG=hnl_tracks/signal/MixingDIS/nuebar,FILETYPE=SIREN convert.sbatch
sbatch --export TAG=hnl_tracks/signal/MixingDIS/numubar,FILETYPE=SIREN convert.sbatch
