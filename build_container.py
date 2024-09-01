#!/usr/bin/env python3

import argparse
import os
import shlex
import subprocess
import sys

SCRIPT_DIR=os.path.dirname(os.path.realpath(__file__))

def parse_args():
    parser = argparse.ArgumentParser(
            prog='build_container.py',
            description='Create a docker container for cross compilation',
            epilog='Ex. build_container.py -a powerpc-linux-musl -o image.tar.gz')
    parser.add_argument('-d', '--deps',
        help='Dependencies.txt file containing list of extra dependencies to commit to container',
        default=SCRIPT_DIR+'/dependencies.txt')
    parser.add_argument('-a', '--arch', required=True, type=str, help='Architecture of image to cross compile for')
    parser.add_argument('-o', '--outfile', required=True, type=str, help='Outfile name for compressed Docker image')
    return parser.parse_args()

def docker_pull_image(image_name):
    cmd = 'docker pull {}'.format(image_name)
    try:
        subprocess.run(shlex.split(cmd), check=True)
    except subprocess.CalledProcessError as e:
        print('[-] {}'.format(e))
        sys.exit(1)

def docker_get_image_id(image_name):
    cmd = 'docker images -q --filter=reference={}'.format(image_name)
    res = subprocess.run(shlex.split(cmd), check=True, capture_output=True)
    if res:
        return res.stdout.decode('utf-8').strip()
    return None

def docker_get_container_id(container_name):
    cmd = 'docker ps -aqf name={}'.format(container_name)
    res = subprocess.run(shlex.split(cmd), check=True, capture_output=True)
    if res:
        return res.stdout.decode('utf-8').strip()
    return None

def docker_rm_container(container_name):
    cmd = 'docker container rm {}'.format(container_name)
    subprocess.run(shlex.split(cmd), check=True, capture_output=True)

class BuildContainer:
    def __init__(self, arch, deps_file, outfile):
        self.arch = arch
        self.outfile = outfile
        # Right now, only attempt to pull images from muslcc/i686
        self.image = 'muslcc/i686:' + arch
        print('[+] Pulling docker image \"{}\"'.format(self.image))
        docker_pull_image(self.image)
        print('[+] Reading dependencies file')
        self.deps = self.read_dependencies(deps_file)
        self.image_id = docker_get_image_id(self.image)

    def read_dependencies(self, deps_file):
        deps = []
        with open(deps_file, 'r') as f:
            for line in f.readlines():
                deps.append(line.strip())
        return deps

    def export_image(self, image_id):
        cmd = 'docker save -o {} {}'.format('image.tar', image_id)
        subprocess.run(shlex.split(cmd), check=True)
        cmd = 'tar -czf {} {}'.format(self.outfile, 'image.tar')
        subprocess.run(shlex.split(cmd), check=True)

    def update_image(self):
        """
        Start the container in interactive mode with a /bin/sh process. Then `apk add` all
        of the dependencies we need for the container. Before we exit, docker commit the
        changes to the image and create a new image.
        NOTE: we use apk because the muslcc images are Alpine based
        """
        if not self.deps or not self.image_id:
            return

        # Make sure container doesn't exist
        name = 'build_container_initial'
        if docker_get_container_id(name):
            print('[+] {} container exists. Removing'.format(name))
            docker_rm_container(name)

        # Start the container
        docker_cmd = 'docker run --name {} -i {} /bin/sh'.format(name, self.image_id)
        print('[+] Starting container ({})'.format(docker_cmd))
        s = subprocess.Popen(shlex.split(docker_cmd), stdin=subprocess.PIPE, stdout=subprocess.PIPE)

        # Install the dependencies
        print('[+] Installing dependencies in container ({} packages)'.format(len(self.deps)))
        apk_cmd = 'apk add {}\n'.format(' '.join(self.deps))
        s.communicate(bytes(apk_cmd, encoding='utf-8'))

        # TODO: wait until we find the string "OK: " in the output so we know the packages are done installing
        import time
        time.sleep(10)

        # Create new image from container's changes
        print('[+] Generating new docker image')
        container_id = docker_get_container_id(name)
        if not container_id:
            print('[-] Failed to get container id for running container')
            sys.exit(1)
        print('container_id {}'.format(container_id))
        new_image_name = self.image + '-updated'
        docker_cmd = 'docker commit {} {}'.format(container_id, new_image_name)
        subprocess.run(shlex.split(docker_cmd), check=True)

        # Stop the container and then generate a tarball for the new build image
        s.terminate()
        new_image_id = docker_get_image_id(new_image_name)
        print('[+] Exporting new docker image to {}'.format(self.outfile))
        self.export_image(new_image_id)

def main():
    args = parse_args()
    container = BuildContainer(args.arch, args.deps, args.outfile)
    container.update_image()

if __name__ == "__main__":
    main()
