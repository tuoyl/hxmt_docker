FROM centos:7 as builder

LABEL maintainer="tuoyl@ihep.ac.cn"

RUN yum update -y && yum install -y \
  epel-release \
  tree     \
  autoconf \
  automake \
  bzip2-devel \
  emacs \
  gcc \
  gcc-c++ \
  gcc-gfortran \
  apt \
  git \
  libpng-devel \
  libSM-devel \
  libX11-devel \
  libXdmcp-devel \
  libXext-devel \
  libXft-devel \
  libXpm-devel \
  libXrender-devel \
  libXt-devel \
  fftw \
  make \
  mesa-libGL-devel \
  ncurses-devel \
  openssl-devel \
  patch \
  perl \
  perl-ExtUtils-MakeMaker \
  readline-devel \
  sqlite-devel \
  sudo \
  tar \
  vim \
  wget \
  which \
  zlib-devel && \
yum clean all && \
rm -rf /var/cache/yum


# Create the astrosoft directory in /home. This will be our
# install target for all astronomy software
ENV ASTROSOFT /home/astrosoft
RUN mkdir -p $ASTROSOFT


## Conda
ENV CONDAPFX=$ASTROSOFT/conda
COPY setup_anaconda.sh /home/setup_anaconda.sh
RUN sh /home/setup_anaconda.sh && rm -f /home/setup_anaconda.sh
##################

########################################################
## Install heasoft with hxmtsoft as a component
## Install_dependencies 
RUN yum -y groupinstall "Development Tools"   &&\
    yum -y install  ncurses-devel libXt-devel \
                    gcc gcc-c++ gcc-gfortran  \
                    compat-gcc-34-g77         \
                    perl-ExtUtils-MakeMaker   \
                    python-devel              &&\
    yum -y install  libpng-devel              &&\
    yum -y install  vim tar wget which git curl bc &&\
    yum -y install centos-release-scl && \
    yum -y install devtoolset-7-gcc* && \
    yum clean all


RUN mkdir -p $ASTROSOFT/hxmtsoft/source
RUN mkdir -p $ASTROSOFT/hxmtsoft/install
COPY setup_hxmtsoft.sh $ASTROSOFT/hxmtsoft/source/
#RUN sh $ASTROSOFT/hxmtsoft/source/setup_hxmtsoft.sh && rm $ASTROSOFT/hxmtsoft/source/setup_hxmtsoft.sh && rm -rf rm $ASTROSOFT/hxmtsoft/source/*
#ENV HEADAS $ASTROSOFT/hxmtsoft/install/x86_64-pc-linux-gnu-libc2.17
#### NOTE: the HXMTsoft url and version should be flexible

###################################################
## HXMT CALDB
#NOTE:caldb version is 2.02
COPY setup_caldb.sh $ASTROSOFT/hxmtsoft/
#RUN sh $ASTROSOFT/hxmtsoft/setup_caldb.sh && rm -rf $ASTROSOFT/hxmtsoft/setup_caldb.sh
#ENV CALDB $ASTROSOFT/hxmtsoft/CALDB
#ENV CALDBALIAS $CALDB/software/tools/alias_config.fits
#ENV CALDBCONFIG $CALDB/caldb.config
#RUN rm -rf $ASTROSOFT/hxmtsoft/CALDB.tar
####################################################



#####################################################
## Install Tempo2
## 
#RUN yum -y install pgplot
RUN mkdir -p $ASTROSOFT/tempo2
COPY setup_tempo2.sh $ASTROSOFT/tempo2/
RUN sh $ASTROSOFT/tempo2/setup_tempo2.sh && rm -rf $ASTROSOFT/tempo2/setup_tempo2.sh
#####################################################








###########################################################################
#                     End Builder, Start final Product
##########################################################################

# Copy build products into a new Container / layer, specifically centos 7
FROM centos:7

# This is the default location of the shared directoy.
VOLUME ["/data"]

# This is the default command that docker will run if no other command is
# specified, that's fine because we want it to just drop into a bash shell.
# Not do anything fancy.
CMD [ "/bin/bash" ]

# Prepary the Environment of the new Container
ENV ASTROSOFT /home/astrosoft
RUN mkdir -p $ASTROSOFT
ENV HEADAS $ASTROSOFT/hxmtsoft/install/x86_64-pc-linux-gnu-libc2.17
ENV CALDB $ASTROSOFT/hxmtsoft/CALDB
ENV CALDBALIAS $ASTROSOFT/hxmtsoft/CALDB/software/tools/alias_config.fits
ENV CALDBCONFIG $ASTROSOFT/hxmtsoft/CALDB//caldb.config

# Copy all the important stuff from the builder into the final product.
# Also, set the permissions to give the wheel group ownership.
COPY --from=builder --chown=root:wheel $ASTROSOFT/hxmtsoft $ASTROSOFT/hxmtsoft
COPY --from=builder --chown=root:wheel $ASTROSOFT/conda $ASTROSOFT/conda
COPY --from=builder --chown=root:wheel $ASTROSOFT/tempo2 $ASTROSOFT/tempo2

# Now install a bunch of Yum packages, not the devel versions.
RUN sed -i '/tsflags=nodocs/d' /etc/yum.conf && \
yum update -y && \
yum install -y \
  bzip2 \
  dejavu-lgc-sans-fonts \
  emacs \
  gcc \
  gcc-c++ \
  gcc-gfortran \
  gedit \
  git \
  libpng \
  libSM \
  libX11 \
  libXdmcp \
  libXext \
  libXft \
  libXp \
  libXpm \
  libXrender \
  libXt \
  fftw \
  make \
  mesa-libGL \
  ncurses\
  openssl \
  patch \
  perl \
  perl-ExtUtils-MakeMaker \
  readline\
  sqlite \
  sudo \
  tar \
  vim \
  vim-X11 \
  wget \
  which \
  xorg-x11-apps \
  epel-release \
  tree     \
  autoconf \
  automake \
  bzip2-devel \
  emacs \
  gcc \
  gcc-c++ \
  gcc-gfortran \
  apt \
  git \
  libpng-devel \
  libSM-devel \
  libX11-devel \
  libXdmcp-devel \
  libXext-devel \
  libXft-devel \
  libXpm-devel \
  libXrender-devel \
  libXt-devel \
  fftw \
  make \
  mesa-libGL-devel \
  ncurses-devel \
  openssl-devel \
  patch \
  perl \
  perl-ExtUtils-MakeMaker \
  readline-devel \
  sqlite-devel \
  sudo \
  tar \
  vim \
  wget \
  which \
  zlib-devel && \
  yum clean all && \
  yum -y install centos-release-scl && \
  yum -y install devtoolset-7-gcc* && \
rm -rf /var/cache/yum


# Give members of the wheel group sudo access to execute all commands
# Redundantly also give this access to the fermi user
RUN echo -e '%wheel        ALL=(ALL)       NOPASSWD: ALL\n\
hxmt        ALL=NOPASSWD: ALL\n\
hxmt ALL=NOPASSWD: /usr/bin/yum' >> /etc/sudoers
# the entrypoint will prepare the environment, create the new
# user directory, source the ScienceTools and the Ftools, and give
# The user a nice colorful shell.
COPY entrypoint /home/entrypoint
RUN cat /home/entrypoint \
        >> /etc/bashrc && \
        rm -r /home/entrypoint

