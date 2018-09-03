#! /bin/sh

export CONDAPFX=$ASTROPFX/bin/anaconda.sh
curl -s -L https://repo.continuum.io/miniconda/Miniconda2-latest-Linux-x86_64.sh > anaconda.sh
bash anaconda.sh -b -p ${CONDAPFX}
rm anaconda.sh
# echo "export PATH=${CONDAPFX}/bin:$PATH" >> ${HOME}/.bashrc
export PATH=${CONDAPFX}/bin:$PATH
conda install --yes -c conda-forge gosu tini
conda create --name fermi -c conda-forge \
  fermipy \
  jupyter \
  libpng \
  pgplot \
  pyyaml \
  --yes
rm -rf ${CONDAPFX}/pkgs/*
chmod -R g+rwx $ASTROPFX/bin/anaconda
