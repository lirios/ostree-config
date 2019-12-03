depends() {
    echo "bash systemd dmsquash-live"
    return 0
}

install() {
    inst_script "$moddir/ostree-cmdline.sh" \
        "/usr/sbin/ostree-cmdline"
    inst_script "$moddir/ostree-live-generator" \
        "$systemdutildir/system-generators/ostree-live-generator"

    inst_simple "$moddir/ostree-live-populate-writable.service" \
        "$systemdsystemunitdir/ostree-live-populate-writable.service"
}
