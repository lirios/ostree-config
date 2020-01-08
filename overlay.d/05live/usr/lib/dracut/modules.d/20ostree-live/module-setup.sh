#!/bin/bash

depends() {
    echo "bash systemd"
}

installkernel() {
    instmods squashfs loop iso9660 overlay
}

install() {
    inst_multiple umount blkid blockdev

    inst_rules "60-cdrom_id.rules"

    inst_script "$moddir/ostree-cmdline.sh" \
        "/usr/sbin/ostree-cmdline"
    inst_script "$moddir/ostree-live-generator" \
        "$systemdutildir/system-generators/ostree-live-generator"

    inst_simple "$moddir/ostree-live-populate-writable.service" \
        "$systemdsystemunitdir/ostree-live-populate-writable.service"

    inst_multiple -o "checkisomd5"
}
