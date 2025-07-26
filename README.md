# fake-sudo

fake-sudo uses user namespaces and seccomp system call filtering to pretend to be root.

It can be used instead of fakeroot in some places.

## Install

Requirements:
- libseccomp >= 2.5.0

### Debian

    apt-get install -yq python3-seccomp util-linux
    curl -o /usr/bin/sudo https://github.com/0ex/fake-sudo/raw/master/fake-sudo.py
    chmod +x /usr/bin/sudo

### Arch

    pacman -S python-libseccomp
    curl -o /usr/bin/sudo https://github.com/0ex/fake-sudo/raw/master/fake-sudo.py
    chmod +x /usr/bin/sudo

To avoid sudo being overwritten (out of date):

    curl -L -o /root/fake-sudo.pkg https://github.com/0ex/fake-sudo/releases/download/v1/fake-sudo-1-1-x86_64.pkg.tar.xz
    pacman -U --noconfirm /root/fake-sudo.pkg

## see also

- https://github.com/Changaco/nosudo
- https://salsa.debian.org/clint/fakeroot

## dev notes

- https://man7.org/linux/man-pages/man2/syscalls.2.html
- https://libseccomp.readthedocs.io/en/latest/
- SECCOMP_RET_USER_NOTIF
- https://github.com/seccomp/libseccomp/blob/master/src/python/seccomp.pyx

Flags

- `SECCOMP_USER_NOTIF_FLAG_CONTINUE=1` - let call continue (not totally secure)
