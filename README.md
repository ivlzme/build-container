# build-container

Requires `docker`. Make sure to follow post-installation steps so you can use `docker` without `sudo`.

Quickly create a docker container for cross compilation.

## Usage
```
$ ./build_container.py -h
usage: build_container.py [-h] [-d DEPS] -a ARCH -o OUTFILE

Create a docker container for cross compilation

optional arguments:
  -h, --help            show this help message and exit
  -d DEPS, --deps DEPS  Dependencies.txt file containing list of extra dependencies to commit to container
  -a ARCH, --arch ARCH  Architecture of image to cross compile for
  -o OUTFILE, --outfile OUTFILE
                        Outfile name for compressed Docker image

Ex. build_container.py -a powerpc-linux-musl -o image.tar.gz
```

## Example
```
$ python3 build_container.py -a powerpc-linux-musl -o image.tar.gz
[+] Pulling docker image "muslcc/i686:powerpc-linux-musl"
powerpc-linux-musl: Pulling from muslcc/i686
Digest: sha256:ac3e212dfae9b8f06203bccce1ad73e1a5dc4800ef4ff773e155cf3d785025e7
Status: Image is up to date for muslcc/i686:powerpc-linux-musl
docker.io/muslcc/i686:powerpc-linux-musl
[+] Reading dependencies file
[+] build_container_initial container exists. Removing
[+] Starting container (docker run --name build_container_initial -i 787f6d8ea3b5 /bin/sh)
[+] Installing dependencies in container (6 packages)
[+] Generating new docker image
container_id 3a44057a4145
sha256:e4ac0160d7bb3b00fcc776819dd6f56645616db4c1fa7acef236d72ad0d3c326
[+] Exporting new docker image to image.tar.gz
```
