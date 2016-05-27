#!/usr/bin/env bash

# pull_upstream_changes - Updates repo and applies upstream changes
#
# Copyright (C) 2016 Peter Mosmans
#                    <support AT go-forward.net>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.


# File which has to be available in target directory to qualify as target
FINGERPRINT="docbuilder.py"
# List of directories that need to be updated
SOURCEDIRECTORIES=""
# List of files that need to be updated
SOURCEFILES="docbuilder.py docbuilder_proxy.py proxy_vagrant.py show validate_report.py"
# Root directory within source repo
SOURCEROOT=""
VERSION=0.1

source=$(dirname $(readlink -f $0))
target=$1

if [ -z "$1" ]; then
    echo "Usage: pull_upstream_changes TARGET"
    exit
fi

# Check if the target actually contains the repository
if [ ! -d $target/dtd ]; then
   echo "[-] ${target} does not contain the correct repository"
   exit
fi

# Update repository
echo "[*] Updating source repository (${source})..."
pushd "$source" >/dev/null && git pull && popd >/dev/null

# Only update newer files
echo "[*] Applying changes (if any)..."
for sourcefile in ${SOURCEFILES}; do
    echo cp -uv ${source}/${SOURCEROOT}/${sourcefile} $target/
done
for sourcedirectory in ${SOURCEDIRECTORIES}; do
    echo cp -uvr ${source}/${SOURCEROOT}/${sourcedirectory} $target/
done
echo "[+] Done"
