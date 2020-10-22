#! /bin/sh

export CONDAPFX=$ASTROSOFT/conda/
curl -s -L https://repo.continuum.io/miniconda/Miniconda2-latest-Linux-x86_64.sh > anaconda.sh
bash anaconda.sh -b -p ${CONDAPFX}
rm anaconda.sh
# echo "export PATH=${CONDAPFX}/bin:$PATH" >> ${HOME}/.bashrc
export PATH=${CONDAPFX}/bin:$PATH
conda install --yes -c conda-forge gosu tini
conda create --name hxmt python=3  numpy matplotlib astropy scipy -c conda-forge
#conda create --name hxmt -c conda-forge \
#  argparse \
#  corner \
#  astropy \
#  matplotlib \
#  numpy \
#  jupyter \
#  libpng \
#  pgplot \
#  pyyaml \
#  python=3.7 \
#  --yes
rm -rf ${CONDAPFX}/pkgs/*
chmod -R g+rwx $ASTROSOFT/conda
conda activate hxmt

conda init bash
