#!/usr/bin/python3
# Usage: ./comps-sync.py /path/to/comps-f31.xml.in
# Usage: ./comps-sync.py
#
# Can both remove packages from the manifest
# which are not mentioned in comps, and add packages from
# comps.

import os, sys, subprocess, argparse, shlex, yaml, re
import libcomps
import requests

def fatal(msg):
    print >>sys.stderr, msg
    sys.exit(1)

def write_manifest(fpath, pkgs):
    with open(fpath, 'w') as f:
        f.write('# DO NOT EDIT! This content is generated from comps-sync.py\n')
        f.write('packages:\n')
        for pkg in sorted(pkgs):
            f.write('  - {}\n'.format(pkg))
        print("Wrote {}".format(fpath))

parser = argparse.ArgumentParser()
parser.add_argument("--save", help="Write changes", action='store_true')
parser.add_argument("--file", help="Source path")
parser.add_argument("--releasever", help="Fedora release version")

args = parser.parse_args()

if args.file and args.releasever:
    fatal('The --file and --releasever are mutually exclusive')
if not args.file and not args.releasever:
    fatal('The --releasever argument is mandatory when a comps file is not used')

base_pkgs_path = 'lirios-base-pkgs.yaml'
with open(base_pkgs_path) as f:
    manifest = yaml.safe_load(f)

with open('comps-sync-blacklist.yaml') as f:
    doc = yaml.safe_load(f)
    comps_environments = doc.get('environments', [])
    comps_blacklist = doc.get('blacklist', [])
    comps_whitelist = doc.get('whitelist', [])
    comps_blacklist_groups = doc.get('blacklist_groups', [])
    comps_additional_groups = doc.get('additional_groups', [])
    comps_blacklist_all = [re.compile(x) for x in doc['blacklist_all_regexp']]

def is_blacklisted(pkgname):
    if pkgname in comps_blacklist:
        return True
    for br in comps_blacklist_all:
        if br.match(pkgname):
            return True
    return False

manifest_packages = set(comps_whitelist)

workstation_product_packages = set()
# Parse comps, and build up a set of all packages so we
# can find packages not listed in comps *at all*, beyond
# just the workstation environment.
comps = libcomps.Comps()
if args.file:
    comps.fromxml_f(args.file)
else:
    response = requests.get('https://pagure.io/fedora-comps/raw/master/f/comps-f{}.xml.in'.format(args.releasever))
    if response.status_code != 200:
        fatal('Failed to download comps-f{}.xml.in'.format(args.releasever))
    comps.fromxml_str(response.text)

# Parse the environments, gathering default or mandatory packages
ws_pkgs = {}
for ws_env_name in comps_environments:
    ws_environ = comps.environments[ws_env_name]
    for gid in ws_environ.group_ids:
        group = comps.groups_match(id=gid.name)[0]
        if gid.name in comps_blacklist_groups:
            continue
        for pkg in group.packages:
            pkgname = pkg.name
            if pkg.type not in (libcomps.PACKAGE_TYPE_DEFAULT,
                                libcomps.PACKAGE_TYPE_MANDATORY):
                continue
            pkgdata = ws_pkgs.get(pkgname)
            if pkgdata is None:
                ws_pkgs[pkgname] = pkgdata = (pkg.type, set([gid.name]))
            if (pkgdata[0] == libcomps.PACKAGE_TYPE_DEFAULT and
                pkg.type == libcomps.PACKAGE_TYPE_MANDATORY):
                ws_pkgs[pkgname] = pkgdata = (pkg.type, pkgdata[1])
            pkgdata[1].add(gid.name)

# Additional groups, not present in the selected environments
for group_name in comps_additional_groups:
    group = comps.groups_match(id=group_name)[0]
    if group_name in comps_blacklist_groups:
        continue
    for pkg in group.packages:
        pkgname = pkg.name
        if pkg.type not in (libcomps.PACKAGE_TYPE_DEFAULT,
                            libcomps.PACKAGE_TYPE_MANDATORY):
            continue
        pkgdata = ws_pkgs.get(pkgname)
        if pkgdata is None:
            ws_pkgs[pkgname] = pkgdata = (pkg.type, set([group_name]))
        if (pkgdata[0] == libcomps.PACKAGE_TYPE_DEFAULT and
            pkg.type == libcomps.PACKAGE_TYPE_MANDATORY):
            ws_pkgs[pkgname] = pkgdata = (pkg.type, pkgdata[1])
        pkgdata[1].add(group_name)

# OSTree support is mandatory
ws_ostree_name = 'workstation-ostree-support'
for pkg in comps.groups_match(id=ws_ostree_name)[0].packages:
    pkgdata = ws_pkgs.get(pkg.name)
    if pkgdata is None:
        ws_pkgs[pkg.name] = pkgdata = (pkg.type, ws_ostree_name)

# Look for packages in workstation but not in the manifest
ws_added = {}
for (pkg, data) in ws_pkgs.items():
    if pkgname not in manifest_packages:
        if is_blacklisted(pkgname) is False:
            ws_added[pkg] = data
            manifest_packages.add(pkgname)

def format_pkgtype(n):
    if n == libcomps.PACKAGE_TYPE_DEFAULT:
        return 'default'
    elif n == libcomps.PACKAGE_TYPE_MANDATORY:
        return 'mandatory'
    else:
        assert False

n_comps_new = len(ws_added)
if n_comps_new == 0:
    print("All comps packages are already listed in manifest.")
else:
    print("{} packages not in manifest:".format(n_comps_new))
    for pkg in sorted(ws_added):
        (req, groups) = ws_added[pkg]
        print('  {} ({}, groups: {})'.format(pkg, format_pkgtype(req), ', '.join(groups)))

if n_comps_new > 0 and args.save:
    write_manifest(base_pkgs_path, manifest_packages)
