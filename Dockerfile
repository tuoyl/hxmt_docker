FROM sl:6 as builder

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
ENV ASTROPFX /home/astrosoft
RUN mkdir -p $ASTROPFX



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
    yum clean all

ENV HEADAS $ASTROPFX/hxmtsoft/x86_64-unknown-linux-gnu-libc2.12
COPY hxmtsrc /home/hxmtsrc
RUN source /home/hxmtsrc/setup_heasoft.sh && rm -rf /home/hxmtsrc && rm -f /home/hxmtsrc/setup_heasoft.sh


# ScienceTools. Begin by setting some env vars, then
# Running our setup script. Note that this will also upgrade
# the version of python in the Sciencetools.
#ENV STNAME ScienceTools-v11r5p3-fssc-20180124
#ENV PLAT x86_64-unknown-linux-gnu-libc2.12
#ENV STPFX $ASTROPFX/sciencetools
#COPY fermisrc /home/fermisrc
#RUN sh /home/fermisrc/setup_sciencetools.sh && rm /home/fermisrc/setup_sciencetools.sh


# pgplot. This should really be its own script.
RUN curl -L ftp://ftp.astro.caltech.edu/pub/pgplot/pgplot5.2.tar.gz > pgplot5.2.tar.gz &&\
 tar zxvf pgplot5.2.tar.gz &&\
 rm -rf /pgplot5.2.tar.gz &&\
 mkdir -p $ASTROPFX/pgplot &&\
 cd $ASTROPFX/pgplot &&\
 cp /pgplot/drivers.list . &&\
 sed -i -e '71s/!/ /g' drivers.list &&\
 sed -i -e '72s/!/ /g' drivers.list &&\
 /pgplot/makemake /pgplot linux g77_gcc &&\
 sed -i -e 's/^FCOMPL=g77/FCOMPL=gfortran/g' makefile &&\
 make && make cpg && make clean &&\
 chmod -R g+rwx $ASTROPFX/pgplot &&\
 rm -rf /pgplot

# Tempo
COPY setup_tempo.sh /home/setup_tempo.sh
RUN sh /home/setup_tempo.sh && rm -f /home/setup_tempo.sh

# Tempo2
ENV TEMPO2 $ASTROPFX/tempo2/T2runtime
COPY setup_tempo2.sh /home/setup_tempo2.sh
RUN sh /home/setup_tempo2.sh && rm -f /home/setup_tempo2.sh

# DS9
RUN mkdir $ASTROPFX/bin &&\
 cd $ASTROPFX/bin &&\
 curl http://ds9.si.edu/download/centos6/ds9.centos6.7.6.tar.gz | tar zxv

# RMFIT
RUN cd /usr/local/bin &&\
curl https://fermi.gsfc.nasa.gov/ssc/data/analysis/rmfit/rmfit_v432_64bit.tar.gz | tar zxv




 ##########################################################################
#                     End Builder, Start final Product
##########################################################################

# Copy build products into a new Container / layer, specifically centos 6
FROM sl:6
#MAINTAINER "Fermi LAT Collaboration"

# This is the default location of the shared directoy.
VOLUME ["/data"]

# This is the default command that docker will run if no other command is
# specified, that's fine because we want it to just drop into a bash shell.
# Not do anything fancy.
CMD [ "/bin/bash" ]

# Prepary the Environment of the new Container
ENV ASTROPFX /home/astrosoft
RUN mkdir -p $ASTROPFX
#ENV FERMI_DIR $ASTROPFX/sciencetools/x86_64-unknown-linux-gnu-libc2.12

# Copy all the important stuff from the builder into the final product.
# Also, set the permissions to give the wheel group ownership.
#COPY --from=builder --chown=root:wheel $ASTROPFX/ftools $ASTROPFX/ftools
#COPY --from=builder --chown=root:wheel $ASTROPFX/sciencetools $ASTROPFX/sciencetools
COPY --from=builder --chown=root:wheel $ASTROPFX/hxmtsoft $ASTROPFX/hxmtsoft
COPY --from=builder --chown=root:wheel $ASTROPFX/tempo $ASTROPFX/tempo
COPY --from=builder --chown=root:wheel $ASTROPFX/pgplot $ASTROPFX/pgplot
COPY --from=builder --chown=root:wheel $ASTROPFX/tempo2 $ASTROPFX/tempo2
COPY --from=builder --chown=root:wheel $ASTROPFX/bin $ASTROPFX/bin
COPY --from=builder --chown=root:wheel /usr/local/bin/rmfit_v432 /usr/local/bin/rmfit_v432

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
  zlib-devel && \
yum clean all && \
rm -rf /var/cache/yum

# Immigrate required files
COPY hxmt_packages /home/hxmt/hxmt_packages
RUN sh /home/hxmt/hxmt_packages/setup_package.sh && rm -f /home/hxmt/hxmt_packages/setup_package.sh

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

