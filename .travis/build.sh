#!/bin/sh

set -e

channel=unstable
arch=$1
variant=$2

dnf install -y kernel-core supermin qemu-system-x86-core

./runvm/runvm -- \
  ./build \
      --remote-url https://repo.liri.io/ostree/repo \
      --mirror-ref lirios/${channel}/${arch}/${variant} \
      --treefile lirios-${channel}-${variant}.yaml \
      --repodir repo
