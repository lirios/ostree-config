#!/usr/bin/env bash

set -xeuo pipefail

# Remove root password
passwd -d root

# https://github.com/projectatomic/rpm-ostree/issues/1542#issuecomment-419684977
for x in /etc/yum.repos.d/*modular.repo; do
    sed -i -e 's,enabled=[01],enabled=0,' ${x}
done

# Work around https://bugzilla.redhat.com/show_bug.cgi?id=1265295
# Also note the create-new-then-rename dance for rofiles-fuse compat
if ! grep -q '^Storage=persistent' /etc/systemd/journald.conf; then
    (cat /etc/systemd/journald.conf && echo 'Storage=persistent') > /etc/systemd.journald.conf.new
    mv /etc/systemd.journald.conf{.new,}
fi

# See: https://src.fedoraproject.org/rpms/glibc/pull-request/4
# Basically that program handles deleting old shared library directories
# mid-transaction, which never applies to rpm-ostree. This is structured as a
# loop/glob to avoid hardcoding (or trying to match) the architecture.
for x in /usr/sbin/glibc_post_upgrade.*; do
    if test -f ${x}; then
        ln -srf /usr/bin/true ${x}
    fi
done

# Undo RPM scripts enabling units; we want the presets to be canonical
# https://github.com/projectatomic/rpm-ostree/issues/1803
rm -rf /etc/systemd/system/*
systemctl preset-all
rm -rf /etc/systemd/user/*
systemctl --user --global preset-all
