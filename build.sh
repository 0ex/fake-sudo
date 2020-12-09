#!/bin/bash -ex

# Prepare the environment
pacman -Syu --noconfirm --noprogressbar --needed base-devel devtools btrfs-progs dbus sudo

dbus-uuidgen --ensure=/etc/machine-id

sed -i "s|MAKEFLAGS=.*|MAKEFLAGS=-j$(nproc)|" /etc/makepkg.conf

useradd -m user
cd /home/user

# Copy PKGBUILD and *.install scripts
cp "$PKGBUILD_DIR"/*install ./ || true
sed "s|%COMMIT%|$GITHUB_SHA|" "$INPUT_PKGBUILD" > PKGBUILD
chown user PKGBUILD

# Build the package
extra-x86_64-build -- -U user

# Save the artifacts
mkdir -p "$INPUT_OUTDIR"
cp *.pkg.* "$INPUT_OUTDIR"/
