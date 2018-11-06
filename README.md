# hxmt_docker

The container in Dockerhub of HXMT software is called hxmtsoft, which pre-loaded with Ftools, hxmtsoft, tempo2, ds9, python 2.7 and associated modules. 
This page gives you a quick instruction on how to use our hxmtsoft container.

# notice

We didn't provide Dockerfile here. Some required installation packages are oversized to upload, so the dockerfile could not build successfully in any case.

# Installation

Docker is well developed for Linux, Mac, and Windows; you can easily find a Download instruction on its website https://www.docker.com/get-started
This download may require a sign up to their community if you don't want to sign up, you can install the Docker by apt-get install or yum install which depends on your operating system.

# Usage

Our hxmtsoft container is hosted on DockerHub, which is a docker community where developers could publish their images to users.

### Acquire the hxmtsoft image

You can download the hxmtsoft image from DockerHub by doing
```
docker pull ihepuni/hxmtsoft
```
or you can get an image by a tar file provided by users who have already downloaded the image. This image is a compressed 5 Gigabyte file(I'm sorry I've added too much software to it). 
This command pulls the image named hxmtsoft provided by developer ihepuni (that's me) from the DockerHub to your computer. You can also pull a different version of the image by tagging it. For example, by doing 
docker pull ihepuni/hxmtsoft:preliminary_0.1 
you will pull the image that tagged with preliminary_0.1 to your system, the default pulling tag is named latest. You can check different tags which referred to different software version on [DockerHub](https://hub.docker.com/r/ihepuni/hxmtsoft/).

### Check the local images
```
docker images
```
You may get something like this:
```
REPOSITORY          TAG                 IMAGE ID            CREATED             SIZE
ihepuni/hxmtsoft    latest              e287a2cf0031        28 hours ago        9.32GB
```
Create a container from the hxmtsoft image

This step is mutable for the different operating system.
- For MacOS system
This requires XQuartz to be installed and the "Allow Connections from Network Clients"option to be selected in XQuartz > Preferences > Security. This is accessed from the drop-down menu in the upper left corner of your screen, next to the Apple logo.
Quit XQuartz after setting this option.
Create a hxmtsoft container 
```
xhost + 127.0.0.1 && \
docker create -it --init \
-e HOST_USER_ID=`id -u $USER` \
-e DISPLAY=docker.for.mac.localhost:0 \
-v "/directory/you/wannna/share/":/data \
ihepuni/hxmtsoft
```
parameter `-v` assign a local directory to share with the container. A container is like a sandbox, but you can somehow transport data or files to the sandbox in the directory that container and your operating system shared together. In the container, the shared directory is /data/.

- For Ubuntu

Create a hxmtsoft container 
```
docker create -it --init \
-e HOST_USER_ID=`id -u $USER` \
-e DISPLAY=$DISPLAY \
-v /tmp/.X11-unix:/tmp/.X11-unix \
-v "/directory/you/wannna/share/":/data \
ihepuni/hxmtsoft
```

- For Windows

Sorry, I don't have a Windows operating system, I don't know how it works. Please google it and good luck.

Now you create a hxmtsoft container, please run: docker ps -a you may see a new container created like this:
```
CONTAINER ID        IMAGE               COMMAND                  CREATED             STATUS              PORTS               NAMES
da2baa0d63b9        e287a2cf0031        "/bin/bash"              29 hours ago        Up 21 minutes                           gallant_varahamihira
```

CONTAINER ID, IMAGE ID, a startup script, and a randomly assigned name to a container are obtained. You can use the CONTAINER ID or the NAME to start your container.

### Get started

enter container as a root user
```
docker start CONTAINER_ID_or_NAME && \
docker attach CONTAINER_ID_or_NAME
```
or log in as a user named hxmt 
```
docker start CONTAINER_ID_or_NAME && \
docker exec -it CONTAINER_ID_or_NAME su - hxmt
```

Welcome to the Insight-HXMT Container. Good luck & Have fun!
