FROM ubuntu:22.04

WORKDIR /home/hxmtsoft
ARG ASTROSOFT=/home/astrosoft
ENV ASTROSOFT=${ASTROSOFT}

LABEL maintainer="tuoyl@ihep.ac.cn"

# Make bash RUNs strict & verbose (optional but helpful)
SHELL ["/bin/bash", "-euxo", "pipefail", "-c"]

# Install HEASoft prerequisites
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
 && apt-get -y upgrade \
 && apt-get -y install \
	gcc \
	gfortran \
	g++ \
	libcurl4 \
	libcurl4-gnutls-dev \
	libncurses5-dev \
	libreadline6-dev \
	make \
	ncurses-dev \
	perl-modules \
	python3-dev \
	python3-pip \
	python3-setuptools \
	python-is-python3 \
	tcsh \
	wget \
	xorg-dev \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*


RUN mkdir -p ${ASTROSOFT}/hxmtsoft/source ${ASTROSOFT}/hxmtsoft/install
WORKDIR ${ASTROSOFT}/hxmtsoft

#Copy the source file
COPY CALDB2.07.tar.gz ${ASTROSOFT}/hxmtsoft/
COPY hxmtsoftv2.06.tar.gz ${ASTROSOFT}/hxmtsoft/source/

COPY setup_caldb.sh setup_caldb.sh
COPY setup_hxmtsoft.sh setup_hxmtsoft.sh

# Enable modern GCC toolset in the shell environment for subsequent steps
# RHEL9 family: sourcing this script adjusts PATH/CC/CXX/FC
ENV BASH_ENV=/etc/profile

# Run installs (assumes tarballs exist OR wget lines in scripts are UNcommented)
# Use bash so BASH_ENV is honored
SHELL ["/bin/bash", "-lc"]
RUN sh ./setup_hxmtsoft.sh
RUN sh ./setup_caldb.sh

# Configure shells
RUN useradd -m hxmtsoft && \
 chown -R hxmtsoft:hxmtsoft /home/hxmtsoft
RUN apt-get update \
 && apt-get -y install vim 

## Python
RUN echo "Installing prerequisite Python packages..." \
 && pip3 install --only-binary=:all: astropy numpy scipy matplotlib


RUN /bin/echo "export HEADAS=/home/astrosoft/hxmtsoft/install/x86_64-pc-linux-gnu-libc2.35" >> /home/hxmtsoft/.bashrc \
 && /bin/echo ". \$HEADAS/headas-init.sh" >> /home/hxmtsoft/.bashrc \
 && /bin/echo "# Initialize environment for CALDB" >> /home/hxmtsoft/.bashrc \
 && /bin/echo "export CALDB=$ASTROSOFT/hxmtsoft/CALDB" >> /home/hxmtsoft/.bashrc \
 && /bin/echo "export CALDBALIAS=$CALDB/software/tools/alias_config.fits" >> /home/hxmtsoft/.bashrc \
 && /bin/echo "export CALDBCONFIG=$CALDB/caldb.config" >> /home/hxmtsoft/.bashrc \
 && /bin/echo "# -- Maintained and updated by Youli -- #"

# Clean up
RUN rm -rf ${ASTROSOFT}/hxmtsoft/source

# Initialization
# 1. Create the user (if not already created)
RUN /bin/echo "hxmtsoft ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

# 2. Switch to that user
USER hxmtsoft
WORKDIR /home/hxmtsoft

# 3. Set bash as the default shell, forcing it to be a login shell so .bashrc is sourced
CMD ["bash", "-l"]
