
# background
sbatch --export TAG=hnl_tracks_with_bdt/background/22803_extended,FILETYPE=CORSIKA convert.sbatch
sbatch --export TAG=hnl_tracks_with_bdt/background/22852,FILETYPE=NuGen convert.sbatch
sbatch --export TAG=hnl_tracks_with_bdt/background/22853,FILETYPE=NuGen convert.sbatch
sbatch --export TAG=hnl_tracks_with_bdt/background/22855,FILETYPE=NuGen convert.sbatch
sbatch --export TAG=hnl_tracks_with_bdt/background/22856,FILETYPE=NuGen convert.sbatch
sbatch --export TAG=hnl_tracks_with_bdt/background/23257,FILETYPE=NuGen convert.sbatch
sbatch --export TAG=hnl_tracks_with_bdt/background/23258,FILETYPE=NuGen convert.sbatch
# signal
#sbatch --export TAG=hnl_tracks_with_bdt/signal/DipoleDIS,FILETYPE=SIREN convert.sbatch
sbatch --export TAG=hnl_tracks_with_bdt/signal/MixingDIS/nue,FILETYPE=SIREN convert.sbatch
sbatch --export TAG=hnl_tracks_with_bdt/signal/MixingDIS/numu,FILETYPE=SIREN convert.sbatch
sbatch --export TAG=hnl_tracks_with_bdt/signal/MixingDIS/nuebar,FILETYPE=SIREN convert.sbatch
sbatch --export TAG=hnl_tracks_with_bdt/signal/MixingDIS/numubar,FILETYPE=SIREN convert.sbatch
