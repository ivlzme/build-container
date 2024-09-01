#!/usr/bin/env python3

import argparse
import os
import subprocess
import sys

SCRIPT_DIR=os.path.dirname(os.path.realpath(__file__))

def parse_args():
    parser = argparse.ArgumentParser(
            prog='build_container.py',
            description='Create a docker container for cross compilation',
            epilog='Ex. build_container.py --arch powerpc-linux-musl')
    parser.add_argument('-d', '--deps',
        help='Dependencies.txt file containing list of extra dependencies to commit to container',
        default=SCRIPT_DIR+'/dependencies.txt')
    parser.add_argument('-a', '--arch', type=str, help='Architecture of image to cross compile for')
    return parser.parse_args()

def pull_docker_image(name):
    # Right now, only attempt to pull images from muslcc/i686
    muslcc_img = 'muslcc/i686:' + name
    print('[+] Pulling docker image \"{}\"'.format(muslcc_img))
    try:
        subprocess.run(['docker', 'pull', muslcc_img], check=True)
    except subprocess.CalledProcessError as e:
        print('[-] {}'.format(e))
        sys.exit(1)

def read_dependencies(deps_file):
    for open(deps.file, 'r') as f:
        for line in f.readlines():
            

def main():
    args = parse_args()
    pull_docker_image(args.arch)

if __name__ == "__main__":
    main()
