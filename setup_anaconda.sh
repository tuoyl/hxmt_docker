#! /bin/sh

export CONDAPFX=$ASTROSOFT/conda/
curl -s -L https://repo.continuum.io/miniconda/Miniconda2-latest-Linux-x86_64.sh > anaconda.sh
bash anaconda.sh -b -p ${CONDAPFX}
rm -rf anaconda.sh
export PATH=${CONDAPFX}/bin:$PATH
conda init bash
source $HOME/.bashrc
conda update --yes -n base -c defaults conda
conda install --yes -c conda-forge gosu tini
conda create --yes --name hxmt python=3  numpy matplotlib astropy scipy numba stingray -c conda-forge
rm -rf ${CONDAPFX}/pkgs/*
chmod -R g+rwx $ASTROSOFT/conda
conda activate hxmt
